import uuid

from django.utils.dateparse import parse_datetime
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import ConversationSerializer
from .models import Conversation
from .models import Conversation, Message
from .choices import ConversationStatus, MessageType
from .tasks import process_message_group


class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    lookup_field = 'id'


class WebhookView(APIView):
    def post(self, request):
        event_type = request.data.get('type')
        timestamp = request.data.get('timestamp')
        data = request.data.get('data')

        if not event_type or not data or not timestamp:
            return Response({'error': 'Payload inválido'}, status=status.HTTP_400_BAD_REQUEST)

        match event_type:
            case 'NEW_CONVERSATION':
                return self._handle_new_conversation(data, timestamp)
            
            case 'NEW_MESSAGE':
                return self._handle_new_message(data, timestamp)
            
            case 'CLOSE_CONVERSATION':
                return self._handle_close_conversation(data)
            
            case _:
                return Response({'error': 'Tipo desconhecido'}, status=status.HTTP_400_BAD_REQUEST)

    def _handle_new_conversation(self, data, timestamp):
        conv_id = data.get('id')
        if Conversation.objects.filter(id=conv_id).exists():
            return Response({'error': 'Conversa já existe'}, status=status.HTTP_400_BAD_REQUEST)

        Conversation.objects.create(id=conv_id, status=ConversationStatus.OPEN)
        return Response({'message': 'Conversa criada'}, status=status.HTTP_201_CREATED)

    def _handle_new_message(self, data, timestamp):
        conv_id = data.get('conversation_id')
        msg_id = data.get('id')
        content = data.get('content')
        ts = parse_datetime(timestamp)

        if not all([conv_id, msg_id, content, ts]):
            return Response({'error': 'Dados de mensagem inválidos'}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.filter(id=conv_id).first()

        if conversation and conversation.is_closed:
            return Response({'error': 'Conversa está fechada'}, status=status.HTTP_400_BAD_REQUEST)

        if not conversation:
            pass

        Message.objects.create(
            id=msg_id,
            conversation_id=conv_id,
            type=MessageType.INBOUND,
            content=content,
            timestamp=ts
        )

        # eu usei o apply_async com countdown=5 em vez de .delay() para permitir o agendamento
        # da task com um pequeno atraso. Isso dá tempo para outras mensagens chegarem e serem agrupadas,
        # conforme a regra de negócio que permite até 5 segundos entre mensagens.
        process_message_group.apply_async(args=[conv_id], countdown=5)

        return Response({'message': 'Mensagem recebida'}, status=status.HTTP_202_ACCEPTED)

    def _handle_close_conversation(self, data):
        conv_id = data.get('id')
        conversation = Conversation.objects.filter(id=conv_id).first()

        if not conversation:
            return Response({'error': 'Conversa não existe'}, status=status.HTTP_400_BAD_REQUEST)

        if conversation.status == ConversationStatus.CLOSED:
            return Response({'error': 'Conversa já está fechada'}, status=status.HTTP_400_BAD_REQUEST)

        conversation.status = ConversationStatus.CLOSED
        conversation.save()

        return Response({'message': 'Conversa fechada'}, status=status.HTTP_200_OK)