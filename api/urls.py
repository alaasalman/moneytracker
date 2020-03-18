from django.conf.urls import url, include
from rest_framework import routers

from api import views

app_name = 'api'

router = routers.SimpleRouter()
router.register(r'transaction', views.TransactionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    # url(r'transaction/chart/monthly$',
    #     views.TransactionChartMonthlyDataView.as_view(),
    #     name='api-transaction-chart-data-monthly'
    #     ),
    url(r'account/$',
        views.AccountListView.as_view(),
        name='api-account-list'
        ),

    url(r'currency/$',
        views.CurrencyListView.as_view(),
        name='api-currency-list'
        ),

    url(r'tag/$',
        views.TagListView.as_view(),
        name='api-tag-list')
]
