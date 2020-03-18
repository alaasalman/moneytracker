import logging

from django import forms

from taggit.forms import TagField

from registration.forms import RegistrationForm
from walletweb import models

logger = logging.getLogger('moneytracker')


class RecurringTransactionForm(forms.ModelForm):
    amount = forms.CharField(widget=forms.TextInput(attrs={'class': 'text-input'}), label='Amount')
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'text-input'}), label='Description')

    class Meta:
        model = models.RecurringTransaction
        fields = ['account', 'amount', 'description',
                  'repeatevery', 'repeattype']


class TransactionForm(forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = models.Transaction
        fields = ['account', 'amount', 'description',
                  'date', 'currency', 'tags']
        norender = ['tags']


class TransactionUploadForm(forms.Form):
    csvfile = forms.FileField()
    uploadtype = forms.ChoiceField(choices=models.FileUpload.UPLOAD_TYPE)
    account = forms.ModelChoiceField(queryset=models.Account.objects.none())


class AccountForm(forms.ModelForm):
    name = forms.CharField(max_length=255, label="Name", help_text="name of your account")
    currency = forms.Select()

    class Meta:
        model = models.Account
        fields = ['name', 'currency']


class MTRegistrationForm(RegistrationForm):
    class Meta:
        model = models.WalletyUser
        fields = ['email', 'first_name', 'last_name']


class TagForm(forms.ModelForm):
    text = forms.CharField(label="Tag text")

    class Meta:
        model = models.Tag
        fields = ['name']


class ContactMeForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    email = forms.EmailField(label='Your email address', max_length=200)
    message = forms.CharField(label='Your message', widget=forms.Textarea())
