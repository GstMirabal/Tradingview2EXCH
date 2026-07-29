from django.urls import path

from .views import BinanceParamsView, BinanceStatusView

urlpatterns = [
    path('binance-params/', BinanceParamsView.as_view(), name='binance_params'),
    path('status/', BinanceStatusView.as_view(), name='binance_status'),
]
