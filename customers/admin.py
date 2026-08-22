from django.contrib import admin
from .models import Customer, Payment

admin.site.register(Customer)
admin.site.register(Payment)