from django.contrib import admin
from .models import OwnerStocks

class masterStockAdmin(admin.ModelAdmin):
    search_fields = ('owner','stockId', 'costPrice')
    fields = ('owner','stockId', 'costPrice','stockCount', 'first_buy_time')
    list_display = ('owner','stockId','stockCount', 'costPrice', 'first_buy_time')


admin.site.register(OwnerStocks, masterStockAdmin)