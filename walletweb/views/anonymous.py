import logging

from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic as genericviews
from django.contrib import messages
from django.urls import reverse

from walletweb.forms import ContactMeForm
from moneytracker import settings

logger = logging.getLogger('moneytracker')


class AnonymousHome(genericviews.TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            return super().get(request, *args, **kwargs)


class ContactMeFormView(genericviews.FormView):
    form_class = ContactMeForm

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        message = form.cleaned_data['message']

        logger.info(f"Contact {name}:{email} saying {message} ")

        try:
            send_mail('Contact from MoneyTracker', message, settings.DEFAULT_FROM_EMAIL, ['alaa@codedemigod.com'])

            if self.request.user.is_authenticated:
                return render(self.request, 'web/contactme_submitted.html')
            else:
                return render(self.request, 'contactme_submitted.html')
        except Exception as ex:
            logger.exception(ex)
            messages.error(self.request, 'Problem in submitting contact form')
            return HttpResponseRedirect(reverse('home'))

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return 'web/contactme.html'

        return 'contactme.html'
