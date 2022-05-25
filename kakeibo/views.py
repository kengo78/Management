from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.views.generic import TemplateView, CreateView
from django.contrib import messages
from .models import Payment, PaymentCategory, Income, IncomeCategory, PaymentCard
from .forms import PaymentSearchForm, IncomeSearchForm,PaymentCreateForm, IncomeCreateForm
from django.urls import reverse_lazy
import numpy as np
import pandas as pd
from django_pandas.io import read_frame
from .plotly import GraphGenerator
from django.contrib.auth import login


# class SignUp(CreateView):
#     form_class = SignUpForm
#     template_name = 'kakeibo/signup.html'
#     success_url = reverse_lazy('kakeibo:payment_list')
    
#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, usre)
#         self.object = user
#         return HttpResponseRedirect(self.get_success_url())
    
class Toppage(generic.TemplateView):
    template_name = 'kakeibo/toppage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # search formを渡す
        # # これから表示する年月
        # year = int(self.kwargs.get('year'))
        # month = int(self.kwargs.get('month'))
        # context['year_month'] = f'{year}年{month}月'

        # # 前月と次月をコンテキストに入れて渡す
        # if month == 1:
        #     prev_year = int(year) - 1
        #     prev_month = 12
        # else:
        #     prev_year = int(year)
        #     prev_month = int(month) - 1

        # if month == 12:
        #     next_year = int(year) + 1
        #     next_month = 1
        # else:
        #     next_year = int(year)
        #     next_month = int(month) + 1
        # context['prev_year'] = prev_year
        # context['prev_month'] = prev_month
        # context['next_year'] = next_year
        # context['next_month'] = next_month
        # queryset = Payment.objects.filter(date__year=year)
        # queryset = queryset.filter(date__month=month)
        # # クエリセットが何もない時はcontextを返す
        # # 後の工程でエラーになるため
        objects = Payment.objects.all()
        total = 0
        for object in objects:
            total += object.price
        context['total'] = total
        # if not queryset:
        #     return context
        return context
    
    
    

class PaymentList(generic.ListView):
    template_name = 'kakeibo/payment_list.html'
    model = Payment
    ordering = '-date'
    paginate_by = 5
    
    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = form = PaymentSearchForm(self.request.GET or None)

        if form.is_valid():
            year = form.cleaned_data.get('year')
            # 何も選択されていないときは0の文字列が入るため、除外
            if year and year != '0':
                queryset = queryset.filter(date__year=year)

            # 何も選択されていないときは0の文字列が入るため、除外
            month = form.cleaned_data.get('month')
            if month and month != '0':
                queryset = queryset.filter(date__month=month)
                
            card_type = form.cleaned_data.get('c_type')
            if card_type:
                queryset = queryset.filter(card_type=card_type)

            # 〇〇円以上の絞り込み
            greater_than = form.cleaned_data.get('greater_than')
            if greater_than:
                queryset = queryset.filter(price__gte=greater_than)
            
            # 〇〇円以下の絞り込み
            less_than = form.cleaned_data.get('less_than')
            if less_than:
                queryset = queryset.filter(price__lte=less_than)
            
            # キーワードの絞り込み
            key_word = form.cleaned_data.get('key_word')
            if key_word:
                # 空欄で区切り、順番に絞る、and検索
                if key_word:
                    for word in key_word.split():
                        queryset = queryset.filter(description__icontains=word)
            
            # カテゴリでの絞り込み
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # search formを渡す
        context['search_form'] = self.form

        return context
    
class IncomeList(generic.ListView):
    template_name = 'kakeibo/income_list.html'
    model = Income
    ordering = '-date'
    paginate_by = 5
    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = form = IncomeSearchForm(self.request.GET or None)

        if form.is_valid():
            year = form.cleaned_data.get('year')
            if year and year != '0':
                queryset = queryset.filter(date__year=year)

            month = form.cleaned_data.get('month')
            if month and month != '0':
                queryset = queryset.filter(date__month=month)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = self.form

        return context
    
class PaymentCreate(generic.CreateView):
    "支出登録"
    template_name = 'kakeibo/register.html'
    model = Payment
    form_class = PaymentCreateForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '支出登録'
        return context
    def get_success_url(self):
        return reverse_lazy('kakeibo:payment_list')
    
class IncomeCreate(generic.CreateView):
    """収入登録"""
    template_name = 'kakeibo/register.html'
    model = Income
    form_class = IncomeCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '収入登録'
        return context

    def get_success_url(self):
        return reverse_lazy('kakeibo:income_list')
    
class PaymentUpdate(generic.UpdateView):
    """支出更新"""
    template_name = 'kakeibo/register.html'
    model = Payment
    form_class = PaymentCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '支出更新'
        return context

    def get_success_url(self):
        return reverse_lazy('kakeibo:payment_list')

    # def form_valid(self, form):
    #     self.object = payment = form.save()
    #     messages.info(self.request,
    #                   f'支出を更新しました\n'
    #                   f'日付:{payment.date}\n'
    #                   f'カテゴリ:{payment.category}\n'
    #                   f'金額:{payment.price}円')
    #     return redirect(self.get_success_url())
    
class IncomeUpdate(generic.UpdateView):
    """収入更新"""
    teplate_name = 'kakeibo/register.html'
    model = Income
    form_class = IncomeCreateForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '収入更新'
        return context
    
    def get_success_url(self):
        return reverse_lazy('kakeibo:income_list')
    
class PaymentDelete(generic.DeleteView):
    """支出削除"""
    template_name = 'kakeibo/delete.html'
    model = Payment
    
    def get_success_url(self):
        return reverse_lazy('kakeibo:payment_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '支出削除確認'
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = payment = self.get_object()

        payment.delete()
        messages.info(self.request,
                      f'支出を削除しました\n'
                      f'日付:{payment.date}\n'
                      f'カテゴリ:{payment.category}\n'
                      f'金額:{payment.price}円')
        return redirect(self.get_success_url())
    
class IncomeDelete(generic.DeleteView):
    """収入削除"""
    template_name = 'kakeibo/delete.html'
    model = Income

    def get_success_url(self):
        return reverse_lazy('kakeibo:income_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '収入削除確認'
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = income = self.get_object()
        income.delete()
        messages.info(self.request,
                        f'収入を削除しました\n'
                        f'日付:{income.date}\n'
                        f'カテゴリ:{income.category}\n'
                        f'金額:{income.price}円')
        return redirect(self.get_success_url())
    
class MonthDashboard(generic.TemplateView):
    """月間支出ダッシュボード"""
    template_name = 'kakeibo/month_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # これから表示する年月
        year = int(self.kwargs.get('year'))
        month = int(self.kwargs.get('month'))
        context['year_month'] = f'{year}年{month}月'

        # 前月と次月をコンテキストに入れて渡す
        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1

        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1
        context['prev_year'] = prev_year
        context['prev_month'] = prev_month
        context['next_year'] = next_year
        context['next_month'] = next_month
        queryset = Payment.objects.filter(date__year=year)
        queryset = queryset.filter(date__month=month)
        # クエリセットが何もない時はcontextを返す
        # 後の工程でエラーになるため
        if not queryset:
            return context

        df = read_frame(queryset,
                        fieldnames=['date', 'price','card_type', 'category'])

        # グラフ作成クラスをインスタンス化
        gen = GraphGenerator()

        # pieチャートの素材を作成
        df_pie = pd.pivot_table(df, index='category', values='price', aggfunc=np.sum)
        pie_labels = list(df_pie.index.values)
        pie_values = [val[0] for val in df_pie.values]
        plot_pie = gen.month_pie(labels=pie_labels, values=pie_values)
        context['plot_pie'] = plot_pie

        # テーブルでのカテゴリと金額の表示用。
        # {カテゴリ:金額,カテゴリ:金額…}の辞書を作る
        context['table_set'] = df_pie.to_dict()['price']

        # totalの数字を計算して渡す
        context['total_payment'] = df['price'].sum()

        # 日別の棒グラフの素材を渡す
        df_bar = pd.pivot_table(df, index='date', values='price', aggfunc=np.sum)
        dates = list(df_bar.index.values)
        heights = [val[0] for val in df_bar.values]
        plot_bar = gen.month_daily_bar(x_list=dates, y_list=heights)
        context['plot_bar'] = plot_bar
        
        df_pie_type = pd.pivot_table(df, index='card_type', values='price', aggfunc=np.sum)
        pie_type_labels = list(df_pie_type.index.values)
        pie_values = [val[0] for val in df_pie_type.values]
        plot_type_pie = gen.month_pie(labels=pie_type_labels, values=pie_values)
        context['plot_type_pie'] = plot_type_pie
        return context
    

# class Rest(generic.TemplateView):
#     """予算残高の計算と表示"""
