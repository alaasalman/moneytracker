import django_filters

from walletweb import models

class TransactionFilter(django_filters.FilterSet):
    class Meta:
        model = models.Transaction
        fields = {
            'amount': ['lte', 'gte'],
            'date': ['lte', 'gte']
        }
