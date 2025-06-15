class ConversationStatus:
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'

    CHOICES = [
        (OPEN, 'Aberta'),
        (CLOSED, 'Fechada'),
    ]


class MessageType:
    INBOUND = 'INBOUND'
    OUTBOUND = 'OUTBOUND'

    CHOICES = [
        (INBOUND, 'Recebida'),
        (OUTBOUND, 'Enviada'),
    ]
