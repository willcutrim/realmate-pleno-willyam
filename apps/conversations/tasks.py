from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import Message, Conversation
from .choices import MessageType
from datetime import timedelta


@shared_task
def process_message_group(conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return

    if conversation.is_closed:
        return

    now = timezone.now()
    five_seconds_ago = now - timedelta(seconds=5)

    messages = Message.objects.filter(
        conversation_id=conversation_id,
        type=MessageType.INBOUND,
        timestamp__gte=five_seconds_ago
    ).order_by('timestamp')

    if not messages.exists():
        return

    content = "Mensagens recebidas:\n" + "\n".join([str(msg.id) for msg in messages])

    Message.objects.create(
        conversation=conversation,
        type=MessageType.OUTBOUND,
        content=content,
        timestamp=now
    )
