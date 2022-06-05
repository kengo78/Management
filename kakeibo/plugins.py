from .seaborn_color import sns_paired
from typing import Literal
from datetime import datetime
import numpy as np
import pandas as pd
from django_pandas.io import read_frame
from django.db.models import Sum
from .models import Payment, Income, PaymentCategory, IncomeCategory
from django.conf import settings


class MonthPagerMixin:
    """テンプレートの月送りページング機能を提供するMixin"""

    def get_current_month(self):
        """アクセスされている月を返す"""
        month = int(self.kwargs.get('month'))
        year = int(self.kwargs.get('year'))
        return datetime(year=year, month=month, day=1)

    @staticmethod
    def get_prev_month(date):
        """前月を返す"""
        if date.month == 1:
            return date.replace(year=date.year - 1, month=12, day=1)
        else:
            return date.replace(month=date.month - 1, day=1)

    @staticmethod
    def get_next_month(date):
        """次月を返す"""
        if date.month == 12:
            return date.replace(year=date.year + 1, month=1, day=1)
        else:
            return date.replace(month=date.month + 1, day=1)

    def get_month_pager_data(self):
        current_month = self.get_current_month()
        month_pager_data = {
            'current_month': current_month,
            'prev_month': self.get_prev_month(current_month),
            'next_month': self.get_next_month(current_month)
        }
        return month_pager_data


class BaseDashPageMixin:
    """dashboard系のページの共通機能を提供する"""

    @staticmethod
    def get_df_pivot(df, index, values):
        """querysetからpivot集計したdfを返す"""
        return pd.pivot_table(df, index=index, values=values, aggfunc=np.sum)

    @staticmethod
    def get_index_list_from_pivot(df_pivot):
        """pivotからindexの値をリストにして返す"""
        return list(df_pivot.index.values)

    @staticmethod
    def get_value_list_from_pivot(df_pivot, col_name=None):
        """pivotからvalueの値をリストにして返す"""
        if col_name:
            return [val for val in df_pivot[col_name].values]
        else:
            return [val[0] for val in df_pivot.values]

    @staticmethod
    def add_month_col_to_df(df):
        """dfにmonth列を与えて返す"""
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.strftime('%Y-%m')
        return df

    @staticmethod
    def get_color_map(category_model, donut_graph_labels):
        """
        ドーナッツグラフデータに渡すcolormapリストを作成して返す
        表示されるカテゴリは月によって変わる。
        そのため先にカテゴリ全データから、{category名:rgb値}という辞書を作る
        グラフラベルをkeyに辞書から値を取得することで、カテゴリによって色が変わらない
        """

        color_palette = sns_paired()
        color_dict = {}
        for i, category in enumerate(category_model.objects.all()):
            color_dict[category.name] = color_palette[i]

        return [color_dict.get(category) for category in donut_graph_labels]

    @staticmethod
    def get_sum_amount(queryset):
        """querysetのamountの合計を返す"""
        return queryset.aggregate(Sum('amount'))['amount__sum']

    @staticmethod
    def calc_composition_ratio(amount, total):
        """構成比を返す"""
        return round(100 * (amount / total), 1)

    @staticmethod
    def calc_diff_ratio(current_amount, past_amount):
        """増減率を計算して返す"""
        if current_amount and past_amount:
            return round(100 * (current_amount / past_amount - 1), 2)
        elif current_amount:
            return None
        elif past_amount:
            return -100.0
        else:
            return None


class MonthlyBalanceMixin(MonthPagerMixin, BaseDashPageMixin):
    """月間収支ページのcontextを作成するMixin"""

    def get_table_items(self, categories, values, total):
        """
        [{'category':カテゴリ名,
        'amount':金額,
        'composition_ratio':構成比},...]
        というリストを作って返す
        """
        items = []
        for category, amount in zip(categories, values):
            composition_ratio = self.calc_composition_ratio(amount, total)
            items.append({'category': category,
                          'amount': amount,
                          'composition_ratio': composition_ratio})

        return items

    def get_monthly_balance_data(self):
        """contextデータを作成して返す"""

        # 月送りページング部分の取得
        data = self.get_month_pager_data()
        current = data['current_month']

        # querysetを絞りこむ
        qs_payment = Payment.objects.filter(date__year=current.year,
                                            date__month=current.month)
        if not qs_payment:
            return data

        # ドーナッツチャートのラベルを作成
        df = read_frame(qs_payment, fieldnames=['category', 'amount'])
        df_pivot = self.get_df_pivot(df, index='category', values='amount')
        categories = self.get_index_list_from_pivot(df_pivot)
        amounts = self.get_value_list_from_pivot(df_pivot)

        # 収支情報の作成
        qs_income = Income.objects.filter(date__year=current.year,
                                          date__month=current.month)
        total_payment = self.get_sum_amount(qs_payment)
        total_income = self.get_sum_amount(qs_income)
        if total_income:
            balance = total_income - total_payment
        else:
            balance = -total_payment

        # テーブル部分の作成
        table_items = self.get_table_items(categories, amounts, total_payment)

        # カラーマップの作成
        color_map = self.get_color_map(category_model=PaymentCategory,
                                       donut_graph_labels=categories)
        data.update({
            'donut_chart_labels': categories,
            'donut_chart_values': amounts,
            'total_payment': total_payment,
            'total_income': total_income,
            'table_items': table_items,
            'balance': balance,
            'color_map': color_map
        })
        return data


class BalanceTransitionMixin(BaseDashPageMixin):
    """収支推移ページのcontextを作成するMixin"""

    def get_labels_max(self):
        """
        支出、収入モデルの年月データから最大長のラベルを返す
        Todo:ここも改善の余地がある
        """

        # 支出の月データ
        df_payment = read_frame(Payment.objects.all(), fieldnames=['date'])
        df_payment = self.add_month_col_to_df(df_payment)
        df_payment = df_payment.drop_duplicates(subset='month')

        # 収入の月データ
        df_income = read_frame(Income.objects.all(), fieldnames=['date'])
        df_income = self.add_month_col_to_df(df_income)
        df_income = df_income.drop_duplicates(subset='month')

        # mergeして月でソート
        df_merge = pd.merge(df_income, df_payment, on='month', how='outer')
        df_merge = df_merge.sort_values('month')
        return [val for val in df_merge['month'].values]

    def get_amount(self, queryset, labels_max):
        """querysetを受け取り、年月に対応するamountをyieldして返す"""
        df = read_frame(queryset,
                        fieldnames=['date', 'amount'])
        df = self.add_month_col_to_df(df)
        df_pivot = self.get_df_pivot(df, index='month', values='amount')

        # {'month':amount}という辞書になる
        dic = df_pivot.to_dict()['amount']

        # 最大長のラベルを繰り返し、辞書から値をセットしていく
        for label in labels_max:
            yield dic.get(label, 0)

    def get_balance_transition_data(self, form):
        """contextデータを作成して返す"""
        labels_max = self.get_labels_max()
        qs_payment = Payment.objects.all()
        qs_income = Income.objects.all()

        graph_visible = None
        if form.is_valid():
            payment_category = form.cleaned_data.get('payment_category')
            if payment_category:
                qs_payment = qs_payment.filter(category=payment_category)
            income_category = form.cleaned_data.get('income_category')
            if income_category:
                qs_income = qs_income.filter(category=income_category)

            graph_visible = form.cleaned_data.get('graph_visible')

        # forms.pyで表示グラフ名を定義
        payments = None
        incomes = None
        if graph_visible == 'All':
            if qs_payment:
                payments = [amount for amount in self.get_amount(qs_payment, labels_max)]
            if qs_income:
                incomes = [amount for amount in self.get_amount(qs_income, labels_max)]

        if not graph_visible or graph_visible == 'Payment':
            if qs_payment:
                payments = [amount for amount in self.get_amount(qs_payment, labels_max)]

        if not graph_visible or graph_visible == 'Income':
            if qs_income:
                incomes = [amount for amount in self.get_amount(qs_income, labels_max)]

        return {
            'labels': labels_max,
            'payments': payments,
            'incomes': incomes
        }


