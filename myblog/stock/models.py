#coding:utf-8
from django.db import models

# Create your models here.
class OwnerStocks(models.Model):
    stockId = models.CharField(max_length=20, verbose_name=u'股票代码')

    costPrice = models.FloatField(default=0, verbose_name=u'成本价')
    stockCount = models.IntegerField(default=0, verbose_name=u'持有股数')
    first_buy_time = models.DateTimeField(u'初次购买时间')
    owner = models.CharField(max_length=20, verbose_name=u'所有者', default=u'master')

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', auto_now=True)

    def __unicode__(self):
        return self.stockId