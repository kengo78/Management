from django.db import models


class PaymentCategory(models.Model):#支払い
    name = models.CharField('カテゴリ名', max_length=32)
    def __str__(self):
        return self.name

class PaymentCard(models.Model):
    c_type = models.CharField('カード名', max_length=20)
    def __str__(self):
        return self.c_type

class Payment(models.Model):
    date = models.DateField('日付')
    price = models.IntegerField('金額')
    card_type = models.ForeignKey(PaymentCard, on_delete=models.PROTECT, verbose_name='カード')
    category = models.ForeignKey(PaymentCategory, on_delete=models.PROTECT, verbose_name='カテゴリ')
    description = models.TextField('摘要', null=True, blank=True)


class IncomeCategory(models.Model):
    name = models.CharField('カテゴリ名', max_length=32)

    def __str__(self):
        return self.name


class Income(models.Model):
    date = models.DateField('日付')
    price = models.IntegerField('金額')
    category = models.ForeignKey(IncomeCategory, on_delete=models.PROTECT, verbose_name='カテゴリ')
    description = models.TextField('摘要', null=True, blank=True)
    
#合計額表示用