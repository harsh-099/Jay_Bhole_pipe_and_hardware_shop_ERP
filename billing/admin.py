from django.contrib import admin
from .models import Bill, BillItem

admin.site.register(Bill)
admin.site.register(BillItem)