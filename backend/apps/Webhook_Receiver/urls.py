from django.urls import path  # Imports the 'path' function to define URLs.
# Imports the 'alertaRecibida' view from the views.py file in the same directory.
from .views import webhookReceived

# List of URLs and their corresponding views.
urlpatterns = [
    # Defines a URL path '/Alerta/' that will be associated with the 'alertaRecibida' view.
    # When this URL is accessed, the corresponding method (GET or POST) of the 'alertaRecibida' view will be executed.
    path('webhook/', webhookReceived.as_view(), name='webhook_Received')
]
