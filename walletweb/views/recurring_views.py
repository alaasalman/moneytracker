from django.contrib import messages
from django.contrib.auth import mixins
from django.urls import reverse
from django.views import generic as genericviews

from walletweb.forms import RecurringTransactionForm
from walletweb.models import Account, RecurringTransaction


class RecurringTransactionCreateView(mixins.LoginRequiredMixin,
                                     genericviews.CreateView):
    form_class = RecurringTransactionForm
    template_name = 'web/rtransaction/rtransaction_add.html'

    def get_form(self):
        rtform = super().get_form(self.form_class)
        req = self.request
        rtform.fields['account'].queryset = Account.objects.filter(user=req.user)

        return rtform

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        self.object.user = user

        rtfm_resp = super().form_valid(form)
        messages.success(self.request, 'Recurring transaction created')

        return rtfm_resp

    def form_invalid(self, form):
        rtfmi_resp = super().form_invalid(form)
        messages.error(self.request, 'Problem in creating recurring transaction')

        return rtfmi_resp

    def get_success_url(self):
        return reverse('rtransaction_list')


class RecurringTransactionListView(mixins.LoginRequiredMixin,
                                   genericviews.ListView):
    context_object_name = 'recurring_transaction_list'
    paginate_by = 10
    template_name = 'web/rtransaction/rtransaction_list.html'

    def get_queryset(self):
        req = self.request
        user = req.user

        rec_transes = RecurringTransaction.objects.filter(user=user)

        return rec_transes


class RecurringTransactionUpdateView(mixins.LoginRequiredMixin,
                                     genericviews.UpdateView):
    form_class = RecurringTransactionForm
    template_name = 'web/rtransaction/rtransaction_edit.html'

    def get_queryset(self):
        user = self.request.user

        return RecurringTransaction.objects.filter(user=user)

    def get_success_url(self):
        messages.success(self.request, 'Recurring Transaction updated')

        return reverse('rtransaction_list')

    def form_invalid(self, form):
        rtf_resp = super().form_invalid(form)
        messages.error(self.request, 'Problem in updating recurring transaction')
        return rtf_resp


class RecurringTransactionDeleteView(mixins.LoginRequiredMixin,
                                     genericviews.DeleteView):
    template_name = 'web/rtransaction/recurringtransaction_confirm_delete.html'

    def get_queryset(self):
        user = self.request.user
        return RecurringTransaction.objects.filter(user=user)

    def get_success_url(self):
        return reverse('rtransaction_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['returnurl'] = self.get_success_url()

        return context

    def delete(self, request, *args, **kwargs):
        rtdel_resp = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Recurring transaction deleted')

        return rtdel_resp
