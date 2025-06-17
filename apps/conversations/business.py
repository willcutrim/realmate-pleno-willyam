import time
from datetime import datetime, timezone

from django.utils.dateparse import parse_datetime
from rest_framework import status

from .models import Conversation, Message, ConversationStatus, MessageType
from .tasks import process_message_group


class WebhookService:

    @staticmethod
    def create_conversation(data, timestamp):
        conv_id = data.get('id')
        if Conversation.objects.filter(id=conv_id).exists():
            return {'error': 'Conversa já existe'}, status.HTTP_400_BAD_REQUEST

        Conversation.objects.create(id=conv_id, status=ConversationStatus.OPEN)
        return {'message': 'Conversa criada'}, status.HTTP_201_CREATED

    @staticmethod
    def handle_new_message(data, timestamp):
        conv_id = data.get('conversation_id')
        msg_id = data.get('id')
        content = data.get('content')
        ts = parse_datetime(timestamp)

        if not all([conv_id, msg_id, content, ts]):
            return {'error': 'Dados de mensagem inválidos'}, status.HTTP_400_BAD_REQUEST

        max_wait = 6
        waited = 0

        conversation = Conversation.objects.filter(id=conv_id).first()
        message = Message.objects.filter(id=msg_id).exists()

        while not conversation and waited < max_wait:
            time.sleep(1)
            waited += 1
            conversation = Conversation.objects.filter(id=conv_id).first()

        if not conversation:
            return {'error': 'Conversa não encontrada após 6s'}, status.HTTP_400_BAD_REQUEST

        if conversation.is_closed:
            return {'error': 'Conversa está fechada'}, status.HTTP_400_BAD_REQUEST

        if message:
            return {'message': 'Mensagem já recebida'}, status.HTTP_200_OK

        Message.objects.create(
            id=msg_id,
            conversation_id=conv_id,
            type=MessageType.INBOUND,
            content=content,
            timestamp=ts
        )

        process_message_group.apply_async(args=[conv_id], countdown=5)

        return {'message': 'Mensagem recebida'}, status.HTTP_202_ACCEPTED

    @staticmethod
    def close_conversation(data):
        conv_id = data.get('id')
        conversation = Conversation.objects.filter(id=conv_id).first()

        if not conversation:
            return {'error': 'Conversa não existe'}, status.HTTP_400_BAD_REQUEST

        if conversation.is_closed:
            return {'error': 'Conversa já está fechada'}, status.HTTP_400_BAD_REQUEST

        conversation.status = ConversationStatus.CLOSED
        conversation.save()

        return {'message': 'Conversa fechada'}, status.HTTP_200_OK
