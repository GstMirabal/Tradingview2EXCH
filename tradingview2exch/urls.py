"""
URL configuration for APIRest_Connector project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Import the Django admin module for the admin panel.
from django.contrib import admin
# Import the 'path' and 'include' functions to define URLs.
from django.urls import path, include, re_path
# Import the necessary modules for Swagger
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import os
import toml

# Read the config.toml file
config_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'config.toml')
config = toml.load(config_path)

# Configure the Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="RESTApi_TradingviewToBinance",
        default_version="1.0.0",
        description="This API allows connecting and automating signals sent from TradingView to echange, facilitating the execution of trading strategies efficiently and without manual intervention.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="gst.mirabal@gmail.com"),
        license=openapi.License(name="OPEN License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
router = DefaultRouter()
# router.register(r'alertas', AlertaRecibida)  # Si tienes un ViewSet para Alerta

urlpatterns = [
    # Define the URL path '/admin/' which will be associated with the Django admin panel.
    path('admin/', admin.site.urls),

    # Define the URL path '/Webhook_Receiver/' and include its URLs using 'include'.
    # The URLs defined in 'Webhook_Receiver.urls' will be added to this base path.
    path('Webhook_Receiver/', include('Webhook_Receiver.urls')),

    # Define the URL path '/Binance_Connector/' and include its URLs using 'include'.
    # The URLs defined in 'Binance_Connector.urls' will be added to this base path.
    path('Binance_Connector/', include('Binance_Connector.urls')),

    # Add URLs for Swagger documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
