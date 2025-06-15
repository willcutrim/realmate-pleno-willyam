from django.urls import path
from .views import ConversationDetailView, WebhookView

urlpatterns = [
    path('conversations/<uuid:id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('webhook/', WebhookView.as_view(), name='webhook'),
]
