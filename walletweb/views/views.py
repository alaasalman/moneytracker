from datetime import date, timedelta, datetime
import logging
from os import path
import uuid

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views import generic as genericviews
from django.db.models import Sum, F
from django.contrib import messages
from django.contrib.auth import mixins
from django.urls import reverse

from moneytracker import settings
from walletweb.forms import TransactionForm, ContactMeForm, TransactionUploadForm, TagForm
from walletweb.models import Transaction, Account, Tag, FileUpload
from walletweb.filters import TransactionFilter


logger = logging.getLogger('moneytracker')

CHART_DAILY = 0
CHART_WEEKLY = 1
CHART_MONTHLY = 2
CHART_YEARLY = 3
CHART_PIE = 4
CHART_TYPE = (
    (CHART_DAILY, 'Daily'),
    (CHART_WEEKLY, 'Weekly'),
    (CHART_MONTHLY, 'Monthly'),
    (CHART_YEARLY, 'Yearly'),
    (CHART_PIE, 'Pie')
)


class Dashboard(mixins.LoginRequiredMixin,
                genericviews.TemplateView):
    template_name = 'web/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        display_currency = user.userprofile.display_currency
        date_today = date.today()

        # for transactions this month, get total made and spent
        current_month_start = date_today.replace(day=1)
        total_made_thismonth, total_spent_thismonth = Transaction.objects.made_spent_breakdown_for_daterange(user,
                                                                                                             current_month_start,
                                                                                                             date_today)

        context['total_made_thismonth'] = total_made_thismonth * display_currency.rate
        context['total_spent_thismonth'] = total_spent_thismonth * display_currency.rate

        # for transactions last month, do the same
        last_month_end = date_today - timedelta(days=date_today.day)
        last_month_start = last_month_end.replace(day=1)

        total_made_lastmonth, total_spent_lastmonth = Transaction.objects.made_spent_breakdown_for_daterange(user,
                                                                                                             last_month_start,
                                                                                                             last_month_end)
        context['total_made_lastmonth'] = total_made_lastmonth * display_currency.rate
        context['total_spent_lastmonth'] = total_spent_lastmonth * display_currency.rate

        # breakdown by tag for this month
        tag_total_dict_thismonth = Transaction.objects.tag_total_for_daterange(user, current_month_start, date_today)

        # apply display currency
        for tag_object, tag_total in tag_total_dict_thismonth.items():
            tag_total_dict_thismonth[tag_object] = (tag_total or 0) * display_currency.rate

        # and last month
        tag_total_dict_lastmonth = Transaction.objects.tag_total_for_daterange(user, last_month_start, last_month_end)

        # apply display currency
        for tag_object, tag_total in tag_total_dict_lastmonth.items():
            tag_total_dict_lastmonth[tag_object] = (tag_total or 0) * display_currency.rate

        context['tag_total_dict_thismonth'] = tag_total_dict_thismonth
        context['tag_total_dict_lastmonth'] = tag_total_dict_lastmonth

        context['display_currency_sign'] = display_currency.sign
        context['this_month'] = date_today.strftime('%B')
        context['last_month'] = date_today.replace(month=date_today.month - 1).strftime('%B')

        return context


class TransactionListView(mixins.LoginRequiredMixin,
                          genericviews.ListView):
    template_name = 'web/transaction/transaction_list.html'
    context_object_name = 'transaction_list'
    paginate_by = 15

    account = None
    from_date = ''
    to_date = ''
    tag = ''
    tags = []
    rule_list = ''
    rule_value_list = ''
    sortby = 'date'
    sortbydirection = 'desc'

    def get_queryset(self):
        request = self.request
        user = request.user
        transaction_list = Transaction.objects.filter(user=user)
        user_accounts = Account.objects.filter(user=user)
        empty_transaction_list = Transaction.objects.none()

        transaction_filter = TransactionFilter(request.GET, queryset=transaction_list)
        transaction_list = transaction_filter.qs

        from_date_param = request.GET.get('date__gte', '')
        try:
            from_date = datetime.strptime(from_date_param, '%Y-%m-%d').date()
        except ValueError:
            from_date = date.today().replace(month=1, day=1)

        self.from_date = from_date.isoformat()

        to_date_param = request.GET.get('date__lte', '')
        try:
            to_date = datetime.strptime(to_date_param, '%Y-%m-%d').date()
        except ValueError:
            to_date = date.today()

        self.to_date = to_date.isoformat()

        # filter transactions via the default filters - no default in the filters file
        transaction_list = transaction_list.filter(date__gte=self.from_date, date__lte=self.to_date)

        if request.GET.get('account') or self.kwargs.get('account'):
            logger.info('looking at account')
            account_id = request.GET.get('account') or self.kwargs['account']

            self.account = get_object_or_404(user_accounts, pk=account_id)
            transaction_list = transaction_list.filter(account=self.account)

        if request.GET.get('tags__have'):
            self.tags = request.GET.get('tags__have').split(',')

        if self.tags:
            transaction_list = transaction_list.filter(Q(tags__slug__in=self.tags) | Q(tags__name__in=self.tags))

        qfilter = Q()
        qexclude = Q()

        for g_param in request.GET.keys():
            rule_value = request.GET.get(g_param, '')

            if g_param == 'description__has':
                qfilter &= Q(description__icontains=rule_value)
            elif g_param == "description__hasnot":
                qexclude |= Q(description__icontains=rule_value)
            elif g_param == "tag_isnot":
                qexclude |= Q(transactiontags__tag__text__icontains=rule_value)

        transaction_list = transaction_list.filter(qfilter).exclude(qexclude)

        self.sortbydirection = request.GET.get('sortbydirection')

        if self.sortbydirection == 'desc':
            sortbysign = '-'
        elif self.sortbydirection == 'asc':
            sortbysign = ''
        else:
            sortbysign = '-'

        self.sortby = request.GET.get('sortby')

        if self.sortby == 'date':
            transaction_list = transaction_list.order_by('{0}date'.format(sortbysign))
        elif self.sortby == 'amount':
            transaction_list = transaction_list.order_by('{0}amount'.format(sortbysign))

        return transaction_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account'] = self.account
        context['from_date'] = self.from_date
        context['to_date'] = self.to_date
        context['tags__have'] = list(Tag.objects.filter(user=self.request.user, name__in=self.tags).values('slug', 'name'))

        context['sortby'] = self.sortby
        context['sortbydirection'] = self.sortbydirection
        transaction_list = self.object_list
        cumulative_balance = transaction_list.aggregate(Sum('amount'))['amount__sum'] or 0

        context['cumulative_balance'] = cumulative_balance or 0
        context['display_currency_sign'] = self.request.user.userprofile.display_currency.sign

        return context


class TransactionCreateView(mixins.LoginRequiredMixin,
                            genericviews.CreateView):
    form_class = TransactionForm
    template_name = 'web/transaction/transaction_add.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_form(self):
        tform = super().get_form(self.form_class)
        request = self.request
        tform.fields['account'].queryset = Account.objects.filter(user=request.user)

        return tform

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        self.object.user = user

        tfm_resp = super().form_valid(form)
        messages.success(self.request, 'Transaction created')

        return tfm_resp

    def form_invalid(self, form):
        tfi_resp = super().form_invalid(form)
        messages.error(self.request, 'Problem in creating transaction')

        return tfi_resp

    def get_success_url(self):
        trans_obj = self.object

        return reverse('transaction_list_all')


class TransactionUpdateView(mixins.LoginRequiredMixin,
                            genericviews.UpdateView):
    form_class = TransactionForm
    template_name = 'web/transaction/transaction_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags_value'] = list(self.object.tags.values('slug', 'name'))
        return context

    def get_form(self, form_class=None):
        tform = super().get_form()
        req = self.request
        tform.fields['account'].queryset = Account.objects.filter(user=req.user)

        return tform

    def get_queryset(self):
        user = self.request.user

        return Transaction.objects.filter(user=user)

    def get_success_url(self):
        return reverse('transaction_list_all')

    def form_invalid(self, form):
        tfi_resp = super().form_invalid(form)
        messages.error(self.request, 'Problem in updating transaction')

        return tfi_resp

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        self.object.user = user

        tfm_resp = super().form_valid(form)
        messages.success(self.request, 'Transaction updated')

        return tfm_resp


class TransactionDeleteView(mixins.LoginRequiredMixin,
                            genericviews.DeleteView):
    template_name = 'web/transaction/transaction_confirm_delete.html'

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(user=user)

    def get_success_url(self):
        return reverse('transaction_list_all')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['returnurl'] = self.get_success_url()

        return context

    def delete(self, request, *args, **kwargs):
        logger.info(f"Deleting transaction")
        tdel_resp = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Transaction deleted')

        return tdel_resp


class TransactionChartView(mixins.LoginRequiredMixin,
                           genericviews.TemplateView):
    template_name = 'web/transaction_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        req = self.request

        context['periodicity'] = req.GET.get('periodicity') or CHART_TYPE[CHART_MONTHLY]
        context['periodicities'] = CHART_TYPE

        from_date_param = req.GET.get('date__gte', '')
        try:
            from_date = datetime.strptime(from_date_param, '%Y-%m-%d').date()
        except ValueError:
            from_date = date.today().replace(month=1, day=1)

        from_date = from_date.isoformat()

        to_date_param = req.GET.get('date__lte', '')
        try:
            to_date = datetime.strptime(to_date_param, '%Y-%m-%d').date()
        except ValueError:
            to_date = date.today()

        to_date = to_date.isoformat()

        tags = []

        if req.GET.get('tags__have'):
            tags = req.GET.get('tags__have').split(',')

        context['tags__have'] = list(Tag.objects.filter(user=req.user, name__in=tags).values('slug', 'name'))

        context['from_date'] = from_date
        context['to_date'] = to_date


        return context


class TransactionUploadView(mixins.LoginRequiredMixin,
                            genericviews.FormView):
    template_name = 'web/transaction/transaction_upload.html'
    form_class = TransactionUploadForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['uploaded_file_list'] = FileUpload.objects.filter(user=user)

        return context

    def get_success_url(self):
        return reverse('transaction_list_all')

    def get_form(self, form_class=None):
        uploadform = super().get_form(form_class=form_class)

        uploadform.fields['account'].queryset = Account.objects.filter(user=self.request.user)

        return uploadform

    def form_invalid(self, form):
        logger.info(f"Invalid upload submission")
        fi_resp = super().form_invalid(form)
        messages.error(self.request, 'Problem in uploading transactions file')
        logger.info(fi_resp)
        return fi_resp

    def form_valid(self, form):
        user = self.request.user

        csv_file = form.files['csvfile']
        # create random, unique file name
        csv_stored_name = f'{user.id}_{uuid.uuid4()}.csv'
        csv_fullpath_destination = path.join(settings.MEDIA_ROOT, csv_stored_name)

        # store for offline processing
        with open(csv_fullpath_destination, 'wb+') as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)

        logger.info(f"User {user.email} uploaded file {csv_stored_name}")

        fupload = FileUpload()
        fupload.user = user
        fupload.name = csv_fullpath_destination
        fupload.uploadtype = form.data.get('uploadtype')
        account_id = form.data.get('account')
        fupload.account = get_object_or_404(Account, pk=account_id)
        fupload.save()

        fv_resp = super().form_valid(form)
        messages.success(self.request, 'Transactions file uploaded and will be processed in a few minutes')

        return fv_resp


class TagListView(mixins.LoginRequiredMixin,
                  genericviews.ListView):
    template_name = 'web/tag/tag_list.html'
    context_object_name = 'tag_list'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user

        return Tag.objects.filter(user=user).distinct()


class TagCreateView(mixins.LoginRequiredMixin,
                    genericviews.CreateView):
    form_class = TagForm
    template_name = 'web/tag/tag_add.html'

    def form_valid(self, form):
        self.object = form.save()
        user = self.request.user
        self.object.user = user

        tfm_resp = super().form_valid(form)
        messages.success(self.request, 'Tag created')

        return tfm_resp

    def form_invalid(self, form):
        tfi_resp = super().form_invalid(form)
        messages.error(self.request, 'Problem in creating tag')

        return tfi_resp

    def get_success_url(self):
        return reverse('tag_list')


class TagUpdateView(mixins.LoginRequiredMixin,
                    genericviews.UpdateView):
    form_class = TagForm
    template_name = 'web/tag/tag_edit.html'

    def get_queryset(self):
        user = self.request.user
        return Tag.objects.filter(user=user)

    def get_success_url(self):
        messages.success(self.request, 'Tag updated')
        return reverse('tag_list')

    def form_invalid(self, form):
        aufi_resp = super().form_invalid(form)
        messages.error(self.form, 'Problem in updating tag')

        return aufi_resp


class TagDeleteView(mixins.LoginRequiredMixin,
                    genericviews.DeleteView):
    template_name = 'web/tag/tag_confirm_delete.html'

    def get_queryset(self):
        user = self.request.user
        return Tag.objects.filter(user=user)

    def get_success_url(self):
        return reverse('tag_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['returnurl'] = self.get_success_url()

        return context

    def delete(self, request, *args, **kwargs):
        logger.info(f"Deleting tag")
        tdel_resp = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Tag deleted')

        return tdel_resp


class TransactionUploadDeleteView(mixins.LoginRequiredMixin,
                                  genericviews.DeleteView):
    template_name = 'web/transaction/transaction_confirm_upload_delete.html'

    def get_queryset(self):
        user = self.request.user

        return FileUpload.objects.filter(user=user)

    def get_success_url(self):
        return reverse('transaction_list_all')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['returnurl'] = self.get_success_url()

        return context

    def delete(self, request, *args, **kwargs):
        logger.info(f"Deleting uploaded file record")
        uploaded_file = self.get_object()
        user = self.request.user
        # delete transactions created from upload
        Transaction.objects.filter(user=user, extra__fromupload=uploaded_file.id).delete()
        # then delete the file record itself, leaving the record on disk
        tdel_resp = super().delete(request, *args, **kwargs)
        messages.success(self.request, 'Uploaded transactions and file deleted')

        return tdel_resp
