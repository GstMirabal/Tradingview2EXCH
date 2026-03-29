from django.urls import path
from .views import binanceParams

# Define the URL pattern for the Params view.
urlpatterns = [
    # Maps the URL '/Params/' to the Params view.
    # When this URL is accessed, the corresponding method (e.g., POST) of the Params view will be executed.
    path('binanceParams/', binanceParams.as_view(), name='binanceParams'),
]
