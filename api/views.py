from datetime import date, timedelta, datetime
import math
import json
import collections
import logging

from django.db.models import Sum, F

from rest_framework import generics
from rest_framework import permissions
from rest_framework import authentication
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters

from api import serializers
from api import filters as api_filters
from walletweb import models


logger = logging.getLogger('moneytracker')


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication,
                              authentication.SessionAuthentication]
    queryset = models.Transaction.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        'amount': ['lte', 'gte'],
        'date': ['lte', 'gte']
    }

    def get_queryset(self):
        request = self.request
        transaction_qs = super().get_queryset().filter(user=request.user)
        transaction_qs_filtered = api_filters.TransactionFilter(self.request.GET, queryset=transaction_qs)
        return transaction_qs_filtered.qs

    @action(detail=False, url_path='chart-data-monthly')
    def chart_data_monthly(self, request):
        transaction_qs = self.get_queryset()

        trans_sum_dict = collections.defaultdict(float)

        for trans in transaction_qs:
            trans_month = trans.date.month
            trans_year = trans.date.year

            key = datetime(trans_year, trans_month, 1)
            key = key.strftime('%Y-%m')

            trans_sum_dict[key] += trans.amount

        trans_keys_sorted_list = sorted(trans_sum_dict.keys())

        # if len(trans_sum_sorted_list) == 0:
        # no data, render empty chart
        # return HttpResponse(json.dumps(chart_dict), content_type='application/json')

        return Response({
            'label': "Monthly Sums",
            'labels': trans_keys_sorted_list,
            'data': [trans_sum_dict[trans_sum_key] for trans_sum_key in trans_keys_sorted_list]
        })

    @action(detail=False, url_path='chart-data-yearly')
    def chart_data_yearly(self, request):
        transaction_qs = self.get_queryset()

        trans_sum_dict = collections.defaultdict(float)

        for trans in transaction_qs:
            trans_year = trans.date.year

            key = datetime(trans_year, 1, 1)
            key = key.strftime('%Y')

            trans_sum_dict[key] += trans.amount

        trans_keys_sorted_list = sorted(trans_sum_dict.keys())

        return Response({
            'label': "Yearly Sums",
            'labels': trans_keys_sorted_list,
            'data': [trans_sum_dict[trans_sum_key] for trans_sum_key in trans_keys_sorted_list]
        })

    @action(detail=False, url_path='chart-data-pie')
    def chart_data_pie(self, request):
        transaction_qs = self.get_queryset()
        trans_sum_dict = collections.defaultdict(float)

        for trans in transaction_qs:
            if trans.tags.count() >= 1:
                key = trans.tags.first().name
            else:
                key = 'Untagged'

            trans_sum_dict[key] += math.fabs(trans.amount)

        return Response({
            'label': "Pie Data",
            'labels': trans_sum_dict.keys(),
            'data': trans_sum_dict.values()
        })


class AccountListView(generics.ListAPIView):
    serializer_class = serializers.AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication,
                              authentication.SessionAuthentication]

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context['user'] = self.request.user

        return context

    def get_queryset(self):
        user = self.request.user
        return models.Account.objects.filter(user=user)


class CurrencyListView(generics.ListAPIView):
    serializer_class = serializers.CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication,
                              authentication.SessionAuthentication]

    def get_queryset(self):
        return models.Currency.objects.all()


class TagListView(generics.ListAPIView):
    serializer_class = serializers.TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    authentication_classes = [authentication.TokenAuthentication,
                              authentication.SessionAuthentication]

    def get_queryset(self):
        return models.Tag.objects.filter(user=self.request.user)
