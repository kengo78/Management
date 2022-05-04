from django.urls import path
from . import views

app_name = 'kakeibo'

urlpatterns = [
    path('', views.PaymentList.as_view(), name='payment_list'),
    path('income_list/', views.IncomeList.as_view(), name='income_list'),
    path('payment_create/', views.PaymentCreate.as_view(), name='payment_create'),
    path('income_create/', views.IncomeCreate.as_view(), name='income_create'),
]
