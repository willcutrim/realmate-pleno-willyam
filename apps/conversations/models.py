from django.db import models
from common.models import BaseModel

from .choices import ConversationStatus, MessageType


class Conversation(BaseModel):
    status = models.CharField(
        max_length=10,
        choices=ConversationStatus.CHOICES,
        default=ConversationStatus.OPEN,
    )

    class Meta:
        app_label = 'conversations'
        verbose_name = 'Conversa'
        verbose_name_plural = 'Conversas'

    def __str__(self):
        return f'Conversation {self.id} ({self.status})'
    
    @property
    def is_closed(self):
        return self.status == ConversationStatus.CLOSED


class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    type = models.CharField(
        max_length=10,
        choices=MessageType.CHOICES,
        default=MessageType.INBOUND
    )
    content = models.TextField()
    timestamp = models.DateTimeField()

    class Meta:
        app_label = 'conversations'
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'

    def __str__(self):
        return f'Message {self.id} ({self.type})'
