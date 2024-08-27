# This script configures the display and management of the 'Alerta' model in the Django admin panel.

# Import the admin module from Django for the admin panel.
from django.contrib import admin
# Import the 'binanceParams' model from the models.py file in the same directory.
from .models import binanceParams

# Define a class 'binanceAdmin' to customize the display of the 'Alerta' model in the admin panel


class binanceAdmin(admin.ModelAdmin):
    # Define the fields to display in the object list in the admin panel.
    list_display = ('exchange', 'symbol', 'side', 'type', 'size')


# Register the 'binanceParams' model with the 'binancesAdmin' class in the Django admin panel.
# This applies the customizations defined in 'binanceAdmin' to the 'binanceParams' model.
admin.site.register(binanceParams, binanceAdmin)
