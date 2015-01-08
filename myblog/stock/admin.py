from django.contrib import admin
from .models import  Operations

class operationStockAdmin(admin.ModelAdmin):
    search_fields = ('owner','stockId', 'operation', 'time')
    fields = ('owner','stockId', 'costPrice','stockCount',  'operation', 'time', 'info')
    list_display = ('owner','stockId','stockCount', 'costPrice',  'operation', 'time', 'info')

admin.site.register(Operations, operationStockAdmin)