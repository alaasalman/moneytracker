from import_export import resources

from walletweb import models


class TransactionResource(resources.ModelResource):

    class Meta:
        model = models.Transaction
        fields = ('amount', 'description', 'date')
