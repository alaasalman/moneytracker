import json

from django.contrib import messages
from django.contrib.auth import mixins
from django.db.models import Max
from django.http import HttpResponse
from django.urls import reverse
from django.views import generic as genericviews

from taggit.models import Tag

from walletweb import models
from walletweb.forms import AccountForm
from walletweb.models import Account


class AccountListView(mixins.LoginRequiredMixin,
                      genericviews.ListView):
    template_name = 'web/account/account_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account_list'] = models.Account.objects.filter(user=self.request.user)
        context['display_currency_sign'] = self.request.user.userprofile.display_currency.sign

        return context

    def get_queryset(self):
        user = self.request.user

        return models.Account.objects.filter(user=user).annotate(last_transaction_date=Max('transactions__date'))


class AccountCreateView(mixins.LoginRequiredMixin,
                        genericviews.CreateView):
    form_class = AccountForm
    template_name = 'web/account/account_add.html'

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        self.object.user = user
        afm_resp = super().form_valid(form)

        messages.success(self.request, 'Account created')

        return afm_resp

    def form_invalid(self, form):
        afi_resp = super().form_invalid(form)
        messages.error(self.request, 'Problem in creating account')

        return afi_resp

    def get_success_url(self):
        return reverse('account_list')


class AccountUpdateView(mixins.LoginRequiredMixin,
                        genericviews.UpdateView):
    form_class = AccountForm
    template_name = 'web/account/account_edit.html'

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(user=user)

    def get_success_url(self):
        messages.success(self.request, 'Account updated')
        return reverse('account_list')

    def form_invalid(self, form):
        aufi_resp = super().form_invalid(form)
        messages.error(self.form, 'Problem in updating account')

        return aufi_resp


class AccountDeleteView(mixins.LoginRequiredMixin,
                        genericviews.DeleteView):
    model = Account
    template_name = 'web/account/account_confirm_delete.html'

    def get_queryset(self):
        user = self.request.user

        return Account.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['returnurl'] = self.get_success_url()

        return context

    def delete(self, request, *args, **kwargs):
        adel_resp = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Account deleted')

        return adel_resp

    def get_success_url(self):
        return reverse('account_list')


class AccountTagsView(mixins.LoginRequiredMixin,
                      genericviews.View):
    def get(self, request, *args, **kwargs):
        user = request.user
        tags = list(Tag.objects.filter(transaction__user=user).distinct().values_list("name", flat=True))
        return HttpResponse(json.dumps(tags))
