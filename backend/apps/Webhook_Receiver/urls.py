from django.urls import path

from .views import WebhookReceivedView

urlpatterns = [
    path('webhook/', WebhookReceivedView.as_view(), name='webhook_received'),
]
