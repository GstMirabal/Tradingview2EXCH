from django.contrib import admin

from .models import Webhook


class WebhookAdmin(admin.ModelAdmin):
    """Admin display configuration for the Webhook model."""

    list_display = ('symbol', 'exchange', 'time', 'interval', 'size', 'side',
                     'price', 'order_id', 'market_position', 'market_prev_position', 'type')
    date_hierarchy = 'time'


admin.site.register(Webhook, WebhookAdmin)
