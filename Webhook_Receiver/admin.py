# This script configures the display and management of the 'Alerta' model in the Django admin panel.

# Import the admin module from Django for the admin panel.
from django.contrib import admin
# Import the 'Alerta' model from the models.py file in the same directory.
from .models import webhook

# Define a class 'AlertaAdmin' to customize the display of the 'Alerta' model in the admin panel.


class webhookAdmin(admin.ModelAdmin):
    # Define the fields to display in the object list in the admin panel.
    list_display = ('symbol', 'exchange', 'time', 'interval', 'size', 'side',
                    'price', 'orderId', 'marketPosition', 'marketPrevPosition', 'type')
    # Add a date hierarchy for easy navigation by date.
    date_hierarchy = 'time'


# Register the 'Alerta' model with the 'AlertaAdmin' class in the Django admin panel.
# This applies the customizations defined in 'AlertaAdmin' to the 'Alerta' model.
admin.site.register(webhook, webhookAdmin)
