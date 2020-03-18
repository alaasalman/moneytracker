from django.db.models import Q
from django_filters import rest_framework as filters

from walletweb import models


class TransactionFilter(filters.FilterSet):
    tags__have = filters.CharFilter(name='tags', method='tags_have_filter')

    class Meta:
        model = models.Transaction
        fields = {
            'amount': ['lte', 'gte'],
            'date': ['lte', 'gte'],
            'description': ['icontains']
        }

    def tags_have_filter(self, queryset, name, value):
        if ',' in value:
            tags = value.split(',')
        else:
            tags = [value]

        transaction_list = queryset.filter(Q(tags__slug__in=tags) | Q(tags__name__in=tags))

        return transaction_list
