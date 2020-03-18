from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from walletweb import models


class TransactionResource(resources.ModelResource):

    class Meta:
        model = models.Transaction
        fields = ('date', 'description', 'amount', 'id')


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_filter = [
        ('user', admin.RelatedOnlyFieldListFilter),
    ]


@admin.register(models.Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    list_filter = [
        ('account', admin.RelatedOnlyFieldListFilter)
    ]
    date_hierarchy = 'date'
    resource_class = TransactionResource


@admin.register(models.RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_filter = [
        ('account', admin.RelatedOnlyFieldListFilter),
        'repeattype'
    ]


@admin.register(models.WalletyUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'last_login']


@admin.register(models.Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['sign', 'rate']


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_filter = [('user', admin.RelatedOnlyFieldListFilter)]
    list_display = ['user', 'name']


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(models.FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['user', 'uploadtype', 'created_at']


@admin.register(models.TransactionTag)
class TransactionTagAdmin(admin.ModelAdmin):
    pass
