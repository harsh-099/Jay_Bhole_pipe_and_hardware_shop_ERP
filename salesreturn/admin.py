from django.contrib import admin
from .models import SaleReturn, SaleReturnItem


admin.site.register(SaleReturn)

admin.site.register(SaleReturnItem)