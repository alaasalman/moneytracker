import factory
from factory.django import DjangoModelFactory

from walletweb import models

DEFAULT_PASSWORD = 'default_123_password'


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = models.Currency

    sign = factory.Sequence(lambda n: '${0}'.format(n))
    name = factory.Sequence(lambda n: 'Currency {0}'.format(n))
    rate = factory.Faker('pyfloat')


class MTUserFactory(DjangoModelFactory):
    class Meta:
        model = models.WalletyUser

    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', DEFAULT_PASSWORD)


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = models.UserProfile

    display_currency = factory.SubFactory(CurrencyFactory)


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = models.Account

    name = factory.Faker('word')
    currency = factory.SubFactory(CurrencyFactory)
    user = factory.SubFactory(MTUserFactory)


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = models.Transaction

    account = factory.SubFactory(AccountFactory)
    amount = factory.Faker('pyfloat')
    description = factory.Faker('sentence', nb_words=10, variable_nb_words=True)
    date = factory.Faker('date_time_between', start_date='-7d', end_date='+7d')
    currency = factory.SubFactory(CurrencyFactory)
    user = factory.SubFactory(MTUserFactory)
