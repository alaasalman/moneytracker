import hashlib

import math
from collections import defaultdict
from decimal import Decimal

from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.contrib.postgres import fields as postgresfields
from django.core import mail
from django.db import models
from django.db.models import F
from django.db.models import Sum
from django.conf import settings
from django.utils.text import slugify

from taggit.managers import TaggableManager
from taggit.models import Tag as TaggitTag


class MTUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name='', last_name=''):
        user = self.model()

        if not email:
            raise ValueError('An email address must be specified')

        user.email = email

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.first_name = first_name or 'MT User'
        user.last_name = last_name or ''

        user.save()

        return user

    def create_superuser(self, email, password, first_name, last_name):
        user = self.create_user(email, password, first_name, last_name)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save()

        return user


class WalletyUser(AbstractBaseUser,
                  PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50,
                                  blank=True)
    last_name = models.CharField(max_length=50,
                                 blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = MTUserManager()

    def get_short_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        mail.send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        db_table = 'walletweb_walletyuser'

    def __str__(self):
        return self.email


class MTModel(models.Model):
    created_at = models.DateTimeField(verbose_name='Created at',
                                      auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Updated at',
                                      auto_now=True)

    class Meta:
        abstract = True


class UserProfile(MTModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_currency = models.ForeignKey('Currency', on_delete=models.CASCADE)

    class Meta:
        db_table = 'walletweb_userprofile'

    def __str__(self):
        return 'Profile for {0}'.format(self.user)


class Currency(MTModel):
    sign = models.CharField(verbose_name='Currency Sign',
                            max_length=5)
    name = models.CharField(verbose_name='Currency Name',
                            max_length=100)
    rate = models.FloatField(verbose_name='Rate to USD',
                             default=1.0)

    class Meta:
        db_table = 'walletweb_currency'

    def __str__(self):
        return self.name


class Account(MTModel):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             on_delete=models.SET_NULL)
    currency = models.ForeignKey(Currency,
                                 verbose_name='Default Account Currency',
                                 null=True,
                                 on_delete=models.SET_NULL)

    @property
    def balance(self):
        # fetch display currency set by user
        display_currency = self.user.userprofile.display_currency

        account_transactions = Transaction.objects.filter(account=self.id)
        # calculate account balance using the display currency rate
        trans_sum = account_transactions.aggregate(trans_sum=Sum(F('amount') * display_currency.rate))[
                        'trans_sum'] or 0

        return trans_sum

    def __str__(self):
        return 'Account %s' % self.name

    class Meta:
        unique_together = ('name', 'user')
        db_table = 'walletweb_account'


class TransactionManager(models.Manager):
    def made_spent_breakdown_for_daterange(self, user, from_date, to_date):
        """
        Returns the total made and total spent for specified user and date range.
        :param user: For specified user
        :param from_date: Start from date
        :param to_date: Ending at date
        :return: tuple (made, spent)
        """
        # for transactions during a certain date range
        transactions_forrange = Transaction.objects.filter(user=user,
                                                            date__gte=from_date,
                                                            date__lte=to_date)

        # breakdown transactions for date range by sign
        positive_transactions = transactions_forrange.filter(amount__gte=0)
        negative_transactions = transactions_forrange.filter(amount__lte=0)

        # sum them up
        total_made = \
            positive_transactions.aggregate(trans_sum=Sum(F('amount') * F('currency__rate')))[
                'trans_sum'] or 0
        total_spent = \
            negative_transactions.aggregate(trans_sum=Sum(F('amount') * F('currency__rate')))[
                'trans_sum'] or 0

        return total_made, total_spent

    def tag_total_for_daterange(self, user, from_date, to_date):
        """
        Returns a dictionary of grouping by tag and their summed transactions amounts.
        :param user: For specified user
        :param from_date: Start from date
        :param to_date: Ending at date
        :return: dict[Tag] = tag total amount
        """

        tags_withtotal = TaggitTag.objects.filter(transaction__user=user, transaction__date__gte=from_date,
                                                  transaction__date__lte=to_date).annotate(
            tag_total=Sum(F('transaction__amount') * F('transaction__currency__rate')))

        tag_total_dict = {tag_object: tag_object.tag_total for tag_object in tags_withtotal}

        # add special tagg called "untagged" to sum up transactions without tags
        untagged_tag = TaggitTag(id=0, name='Untagged', slug='untagged')
        untagged_user_transactions = Transaction.objects.filter(user=user,
                                                                date__gte=from_date,
                                                                date__lte=to_date,
                                                                tags__isnull=True)

        tag_total_dict[untagged_tag] = untagged_user_transactions.aggregate(
            tag_total=Sum(F('amount') * F('currency__rate')))['tag_total']

        return tag_total_dict


class Transaction(MTModel):
    account = models.ForeignKey(Account,
                                null=True,
                                blank=True,
                                related_name='transactions',
                                on_delete=models.SET_NULL)
    amount = models.FloatField(verbose_name='Amount', default=0.0)
    description = models.CharField(max_length=255, blank=True, verbose_name='Description')
    date = models.DateField()
    recurringparent = models.IntegerField(null=True, blank=True)
    currency = models.ForeignKey(Currency,
                                 null=True,
                                 on_delete=models.SET_NULL)
    signature = models.CharField(verbose_name='Transaction Signature',
                                 max_length=150,
                                 null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                             on_delete=models.SET_NULL)

    tags = TaggableManager(blank=False)
    extra = postgresfields.JSONField(verbose_name='Extra Information',
                                     null=True)
    objects = TransactionManager()

    class Meta:
        ordering = ['-date', '-id']
        db_table = 'walletweb_transaction'

    def __str__(self):
        return 'Transaction for %s' % self.description

    def save(self, *args, **kwargs):
        if self.signature is None:
            self.signature = Transaction.sign_transaction(self)

        super().save(*args, **kwargs)

    @property
    def amountwithuniformcurrency(self):
        if self.currency:
            return self.amount * self.currency.rate

        return self.amount

    @property
    def absoluteamount(self):
        return math.fabs(self.amount)

    @staticmethod
    def sign_transaction(transaction, extra=''):
        # generate transaction signature by hashing (amount, description, date and any extra attributes from caller)
        hasher = hashlib.sha256()
        hasher.update(
            '{0}{1}{2}_{3}'.format(transaction.amount, transaction.description, transaction.date.isoformat(), extra).encode())

        return hasher.hexdigest()


class Tag(MTModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    words = postgresfields.ArrayField(models.CharField(max_length=100), blank=True, default=list)
    slug = models.SlugField(null=True)

    def __str__(self):
        return 'Tag %s for User %s' % (self.name, self.user)

    class Meta:
        unique_together = ['user', 'slug']
        db_table = 'walletweb_tag'

    @property
    def transactions(self):
        """
        Returns all user transactions associated with this tag.
        :return: QuerySet[Transaction]
        """
        return Transaction.objects.filter(tags__slug=self.slug,
                                          user=self.user).all()

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)


# no longer used after introducing taggit
class TransactionTag(MTModel):
    transaction = models.ForeignKey(Transaction,
                                    related_name='transactiontags',
                                    on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag,
                            related_name='tagtransactions',
                            on_delete=models.CASCADE)

    class Meta:
        db_table = 'walletweb_transactiontag'

    def __str__(self):
        return 'Tag %s for Trans %s' % (self.tag, self.transaction)


class RecurringTransaction(MTModel):
    REPEAT_DAILY = 1
    REPEAT_WEEKLY = 2
    REPEAT_MONTHLY = 3
    REPEAT_YEARLY = 4
    REPEAT_TYPE = (
        (REPEAT_DAILY, 'Daily'),
        (REPEAT_WEEKLY, 'Weekly'),
        (REPEAT_MONTHLY, 'Monthly'),
        (REPEAT_YEARLY, 'Yearly')
    )

    account = models.ForeignKey(Account,
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name='Amount',
                               default=0.0)
    description = models.CharField(max_length=255,
                                   blank=True,
                                   verbose_name='Description')
    date = models.DateField(auto_now_add=True)
    repeatevery = models.IntegerField(verbose_name='Repeat Every',
                                      default=1)
    repeattype = models.IntegerField(verbose_name='Repeat Type',
                                     choices=REPEAT_TYPE,
                                     default=REPEAT_WEEKLY)
    lastdone = models.DateField(blank=True,
                                null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True,
                             on_delete=models.CASCADE)

    class Meta:
        db_table = 'walletweb_recurringtransaction'

    def __str__(self):
        return 'Recurring transaction for %s' % self.description


class FileUpload(MTModel):
    UPLOAD_TRANSACTIONS_CBA = 1
    UPLOAD_TRANSACTIONS_ING = 2
    UPLOAD_TYPE = (
        (UPLOAD_TRANSACTIONS_CBA, 'CBA Export'),
        (UPLOAD_TRANSACTIONS_ING, 'ING Export')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=250,
                            verbose_name='Stored Name')
    uploadtype = models.IntegerField(verbose_name='Upload Type',
                                     choices=UPLOAD_TYPE,
                                     default=UPLOAD_TRANSACTIONS_CBA)
    processed = models.BooleanField(verbose_name='Is Processed',
                                    default=False)
    account = models.ForeignKey(Account,
                                null=True,
                                blank=True,
                                related_name='uploads',
                                on_delete=models.SET_NULL)

    class Meta:
        db_table = 'walletweb_fileupload'

    def __str__(self):
        return f'{self.id}'
