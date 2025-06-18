from celery import shared_task
from django.utils import timezone
from .models import Message, Conversation
from .choices import MessageType

@shared_task
def process_message_group(conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return

    if conversation.is_closed:
        return

    inbound_messages = Message.objects.filter(
        conversation_id=conversation_id,
        type=MessageType.INBOUND
    ).order_by('timestamp')

    if not inbound_messages.exists():
        return

    latest_inbound = inbound_messages.last()
    tempo_desde_ultima_msg = (timezone.now() - latest_inbound.timestamp).total_seconds()

    if tempo_desde_ultima_msg < 5:
        # Reagenda para rodar novamente
        process_message_group.apply_async(args=[conversation_id], countdown=2)
        return

    content = "Mensagens agrupadas:\n" + "\n".join([
        f"- {m.content}" for m in inbound_messages
    ])

    Message.objects.create(
        conversation=conversation,
        type=MessageType.OUTBOUND,
        content=content,
        timestamp=timezone.now()
    )

    inbound_messages.delete()
