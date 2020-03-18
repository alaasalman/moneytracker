import factory
from factory.django import DjangoModelFactory

from walletweb import models


class UserFactory(DjangoModelFactory):
    class Meta:
        model = models.WalletyUser

    email = factory.Faker('email')


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = models.Currency

    sign = factory.Sequence(lambda n: '${0}'.format(n))
    name = factory.Sequence(lambda n: 'Currency {0}'.format(n))
    rate = factory.Faker('pyfloat')


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = models.Account

    name = factory.Faker('word')
    currency = factory.SubFactory(CurrencyFactory)
    user = factory.SubFactory(UserFactory)


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = models.Transaction

    account = factory.SubFactory(AccountFactory)
    amount = factory.Faker('pyfloat')
    description = factory.Faker('sentence', nb_words=10, variable_nb_words=True)
    date = factory.Faker('date_time_between', start_date='-7d', end_date='+7d')
