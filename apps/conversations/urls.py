from django.urls import path
from .views import ConversationDetailView, WebhookView, ConversationListView

urlpatterns = [
    path('conversations/<uuid:id>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('messages/', ConversationListView.as_view(), name='message-list'),
    path('webhook/', WebhookView.as_view(), name='webhook'),
]
