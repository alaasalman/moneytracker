import hashlib
from rest_framework import serializers

from walletweb import models


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = ['amount', 'description', 'date', 'account', 'currency']

    def validate_account(self, val: models.Account):
        context = self.context
        user = context.get('user')

        if val.user != user:
            raise serializers.ValidationError('This account does not belong to you')

        return val

    def validate(self, attrs):
        context = self.context
        user = context.get('user')
        amount = attrs.get('amount')
        description = attrs.get('description')
        date = attrs.get('date')
        currency = attrs.get('currency')
        account = attrs.get('account')

        # TODO refactor
        # check if transaction is already inserted
        hasher = hashlib.sha256()
        hasher.update('{0}{1}{2}'.format(amount, description, date).encode())
        sig = hasher.hexdigest()  # signature for transaction to be inserted

        transaction_exists = models.Transaction.objects.filter(account__user=user, signature=sig).exists()

        if transaction_exists:
            raise serializers.ValidationError('This transaction has been inserted before')

        return attrs


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = ['id', 'name', 'currency']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ['id', 'sign', 'name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ['name', 'slug']
