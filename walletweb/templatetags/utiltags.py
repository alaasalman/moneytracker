import re

from django import template
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.safestring import mark_safe
from django.urls import reverse

from walletweb.models import Account, Transaction, Tag
from moneytracker.settings import STATIC_URL

register = template.Library()


@register.inclusion_tag('web/pager.html', takes_context=True)
def show_pager(context):
    page = None
    params = {}
    paramsencoded = ''
    prevlink = ''
    nextlink = ''
    firstlink = ''
    lastlink = ''
    pagelinks = []

    if 'request' in context:
        params = context['request'].GET.copy()

        if 'page' in params:
            del (params['page'])

        paramsencoded = params.urlencode()

    if 'page_obj' in context:
        page = context['page_obj']
        paginator = page.paginator
        pagerange = paginator.page_range
        cp = page.number
        cpindex = page.number - 1
        psstart = 1
        psstartindex = 0
        psend = pagerange[-1]
        psendindex = pagerange[-1] - 1
        startindex = 0
        endindex = psendindex
        numpagestoshow = 5
        numpagesontheside = 2

        if paginator.num_pages == 1:
            return {}

        if paginator.num_pages > numpagestoshow:
            # total number of pages gt than pagination limit
            # calculate start and ending page index
            startindex = cpindex - numpagesontheside
            endindex = cpindex + numpagesontheside

            if startindex < 0:
                # start index jumped past zero
                endindex += (startindex * -1)  # add negative pages to end of list
                startindex = 0  # start at beginning
            elif endindex > psendindex:
                # end index jumped past last index
                startindex -= (endindex - psendindex)
                endindex = psendindex

        for i in range(startindex, endindex + 1):
            link = {}
            pagenum = pagerange[i]

            if paramsencoded:
                link['href'] = "%s&page=%s" % (paramsencoded, pagenum)
            else:
                link['href'] = "page=%s" % pagenum

            if pagenum == page.number:
                link['class'] = "pagination-link is-current"
            else:
                link['class'] = "pagination-link"

            link['value'] = pagenum
            link['title'] = pagenum

            pagelinks.append(link)

        if paramsencoded:
            if page.has_previous():
                prevlink = "%s&page=%s" % (paramsencoded, page.previous_page_number())
            if page.has_next():
                nextlink = "%s&page=%s" % (paramsencoded, page.next_page_number())

            if psend - cp > numpagesontheside:
                # pages remain to show on the right, so show last link
                lastlink = "%s&page=%s" % (paramsencoded, pagerange[-1])

            if cp > numpagesontheside + 1:
                # current page gt than pagination limit so show first link
                firstlink = "%s&page=1" % paramsencoded

        else:
            if page.has_previous():
                prevlink = "page=%s" % page.previous_page_number()

            if page.has_next():
                nextlink = "page=%s" % page.next_page_number()

            if psend - cp > numpagesontheside:
                lastlink = "page=%s" % pagerange[-1]

            if cp > numpagesontheside + 1:
                firstlink = "page=1"

    return {
        'page_obj': page,
        'params': paramsencoded,
        'prevlink': prevlink,
        'nextlink': nextlink,
        'firstlink': firstlink,
        'lastlink': lastlink,
        'pagelinks': pagelinks,
        'STATIC_URL': STATIC_URL
        }


@register.inclusion_tag('web/account/account_list_partial.html', takes_context=True)
def show_account_list(context):
    user = context['user']
    account_list = context['account_list']
    paginator = Paginator(account_list, 5)

    # first page by default
    try:
        page = int(context['request'].GET.get('page', 1))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        accounts_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        accounts_page = paginator.page(paginator.num_pages)

    context['STATIC_URL'] = STATIC_URL
    context['page_obj'] = accounts_page
    context['paginator'] = paginator

    return context


@register.simple_tag(takes_context=True)
def highlight_if_active(context, view_name):
    """
    Sets the bulma class to highlight link if the link is the one we're currently on.
    :param context:
    :param view_name:
    :return: css class 'active' or empty
    """

    request = context.request
    view_path = reverse(view_name)

    if re.search(view_path, request.path):
        return 'is-active'

    return ''


@register.inclusion_tag('web/transaction/transaction_filter_partial.html', takes_context=True)
def transaction_filter(context):
    user = context['user']
    account_list = Account.objects.filter(user=user)
    tags = [tag.text for tag in Tag.objects.filter(user=user)]

    context['accounts'] = account_list
    context['tags'] = tags

    return context


@register.filter(name='colorize_amount', needs_autoescape=False)
def colorize_amount(value, csign=None):
    """
    Colorize amount sent in as value depending on the sign of the number.
    :param value: Amount
    :param csign: Optional currency sign to show before amount
    :return: Span element with the positive amount colored according to original value
    """
    currency_sign = csign

    if csign is None:
        # if no sign provided, use empty string
        currency_sign = ''

    if value < 0:
        return mark_safe('<span style=\"color:orangered\">{0}{1:,.2f}</span>'.format(currency_sign, value * -1))
    else:
        return mark_safe('<span style=\"color:forestgreen\">{0}{1:,.2f}</span>'.format(currency_sign, value))
