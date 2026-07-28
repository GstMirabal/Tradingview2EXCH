from django.contrib import admin

from .models import BinanceParams


class BinanceParamsAdmin(admin.ModelAdmin):
    """Admin display configuration for the BinanceParams model."""

    list_display = ('exchange', 'symbol', 'side', 'type', 'size')


admin.site.register(BinanceParams, BinanceParamsAdmin)
