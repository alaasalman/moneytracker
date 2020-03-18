"""
URL Configuration
"""

from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.urls import path

from registration.backends.hmac.views import RegistrationView

from walletweb.forms import MTRegistrationForm
from walletweb.views import anonymous
from walletweb.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class=MTRegistrationForm),
        name='registration_register'),

    url(r'^accounts/',
        include('registration.backends.hmac.urls')),

    url(r'^wallet/',
        include('walletweb.urls')),

    url(r'^$',
        anonymous.AnonymousHome.as_view(),
        name='home'),

    url(r'^about/$',
        TemplateView.as_view(template_name='about.html'),
        name='about'),

    url(r'^contactme/$',
        anonymous.ContactMeFormView.as_view(),
        name='contactme'),

    url(r'^api/',
        include('api.urls', namespace='api')
        ),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap')
]
