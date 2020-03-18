from django.conf.urls import url

import walletweb.views.account_views
import walletweb.views.recurring_views
from walletweb.views import views

urlpatterns = [
    url(r'home/$',
        views.Dashboard.as_view(),
        name='dashboard'),

    url(r'rtransaction/list/$',
        walletweb.views.recurring_views.RecurringTransactionListView.as_view(),
        name='rtransaction_list'),

    url(r'rtransaction/add/$',
        walletweb.views.recurring_views.RecurringTransactionCreateView.as_view(),
        name='rtransaction_add'),

    url(r'rtransaction/edit/(?P<pk>\d+)/$',
        walletweb.views.recurring_views.RecurringTransactionUpdateView.as_view(),
        name='rtransaction_edit'),

    url(r'rtransaction/delete/(?P<pk>\d+)/$',
        walletweb.views.recurring_views.RecurringTransactionDeleteView.as_view(),
        name='rtransaction_delete'),

    url(r'transaction/list/(?P<account>\d+)/$',
        views.TransactionListView.as_view(),
        name='transaction_list'),

    url(r'transaction/list/$',
        views.TransactionListView.as_view(),
        name='transaction_list_all'),

    url(r'transaction/add/$',
        views.TransactionCreateView.as_view(),
        name='transaction_add'),

    url(r'transaction/upload/$',
        views.TransactionUploadView.as_view(),
        name='transaction-upload'),

    url(r'account/list/$',
        walletweb.views.account_views.AccountListView.as_view(),
        name='account_list'),

    url(r'account/add/$',
        walletweb.views.account_views.AccountCreateView.as_view(),
        name='account_add'),

    url(r'account/delete/(?P<pk>\d+)/$',
        walletweb.views.account_views.AccountDeleteView.as_view(),
        name='account_delete'),

    url(r'transaction/delete/(?P<pk>\d+)/$',
        views.TransactionDeleteView.as_view(),
        name='transaction_delete'),

    url(r'transaction/upload/delete/(?P<pk>\d+)/$',
        views.TransactionUploadDeleteView.as_view(),
        name='transaction_upload_delete'),

    url(r'account/edit/(?P<pk>\d+)/$',
        walletweb.views.account_views.AccountUpdateView.as_view(),
        name='account_edit'),

    url(r'transaction/edit/(?P<pk>\d+)/$',
        views.TransactionUpdateView.as_view(),
        name='transaction_edit'),

    url(r'transaction/chart/$',
        views.TransactionChartView.as_view(),
        name='transaction_chart'),

    url(r'tag/list/$',
        views.TagListView.as_view(),
        name='tag_list'),

    url(r'tag/add/$',
        views.TagCreateView.as_view(),
        name='tag_add'),

    url(r'tag/edit/(?P<pk>\d+)/$',
        views.TagUpdateView.as_view(),
        name='tag_edit'),

    url(r'tag/delete/(?P<pk>\d+)/$',
        views.TagDeleteView.as_view(),
        name='tag_delete'),
]
