from django.contrib import admin
from .models import OwnerStocks, Operations

class masterStockAdmin(admin.ModelAdmin):
    search_fields = ('owner','stockId', 'costPrice')
    fields = ('owner','stockId', 'costPrice','stockCount', 'first_buy_time')
    list_display = ('owner','stockId','stockCount', 'costPrice', 'first_buy_time')


class operationStockAdmin(admin.ModelAdmin):
    search_fields = ('owner','stockId', 'operation', 'time')
    fields = ('owner','stockId', 'costPrice','stockCount',  'operation', 'time')
    list_display = ('owner','stockId','stockCount', 'costPrice',  'operation', 'time')

admin.site.register(OwnerStocks, masterStockAdmin)
admin.site.register(Operations, operationStockAdmin)