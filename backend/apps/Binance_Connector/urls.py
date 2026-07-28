from django.urls import path

from .views import BinanceParamsView, BinanceStatusView

urlpatterns = [
    path('binanceParams/', BinanceParamsView.as_view(), name='binance_params'),
    path('status/', BinanceStatusView.as_view(), name='binance_status'),
]
