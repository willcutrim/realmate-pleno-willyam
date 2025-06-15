from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.http import Http404

from .serializers import ConversationSerializer
from .models import Conversation
from .models import Conversation
from .business import WebhookService


class ConversationDetailView(generics.RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return super().get_object()

        except Http404:
            raise NotFound(detail="Conversa não encontrada.")

class WebhookView(APIView):
    def post(self, request):
        event_type = request.data.get('type')
        timestamp = request.data.get('timestamp')
        data = request.data.get('data')

        if not event_type or not data or not timestamp:
            return Response({'error': 'Payload inválido'}, status=status.HTTP_400_BAD_REQUEST)

        match event_type:
            case 'NEW_CONVERSATION':
                body, code = WebhookService.create_conversation(data, timestamp)
                return Response(body, status=code)

            case 'NEW_MESSAGE':
                body, code = WebhookService.handle_new_message(data, timestamp)
                return Response(body, status=code)

            case 'CLOSE_CONVERSATION':
                body, code = WebhookService.close_conversation(data)
                return Response(body, status=code)

            case _:
                return Response({'error': 'Tipo desconhecido'}, status=status.HTTP_400_BAD_REQUEST)