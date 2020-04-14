from django.urls import reverse
from django.core import mail

from moneytracker import settings
from walletweb import models
from . import factories
from .utilities import MTTestCase


class TestAuthAccounts(MTTestCase):

    def setUp(self):
        # bypass the MTTestCase setUp otherwise any redirections will lead to user-specific pages
        pass

    def test_can_visit_register_page(self):
        """
        User can navigate to registration page and the registration template is used that shows a form
        showing at least an email and password fields.
        """
        response = self.client.get(reverse('mt_registration_register'))

        # first up, response is 200
        self.assertEqual(response.status_code, 200)
        # then the registration template is used
        self.assertTemplateUsed(response, 'django_registration/registration_form.html')
        # and registration template has sensible fields
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_register_user(self):
        """
        User can can use the registration form and registration actually creates a user
        """
        # create a mock user
        potential_newuser = factories.MTUserFactory.build()

        response = self.client.post(reverse('mt_registration_register'), {
            'email': potential_newuser.email,
            'password1': potential_newuser.password,
            'password2': potential_newuser.password,
        })

        # check that the registration returns a redirect to login url defined by our settings
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, settings.LOGIN_REDIRECT_URL)

        # check that the user actually got created
        stored_newuser = models.WalletyUser.objects.get(email=potential_newuser.email)
        self.assertEquals(stored_newuser.email, potential_newuser.email)

        # check that an activation email got sent to the user
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to[0], potential_newuser.email)
        self.assertRegex(mail.outbox[0].subject, ".*activate.*")

    def test_can_visit_login_page(self):
        """
        User can visit the login page and it displays the expected login form

        """
        response = self.client.get(reverse('login'))

        # correct response code
        self.assertEqual(response.status_code, 200)

        # then the login template is used
        self.assertTemplateUsed(response, 'registration/login.html')

        # and template has expected login fields
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_user_canlogin(self):
        """
        User can login properly and be redirected to dashboard
        """
        # first create a test user that is active
        newuser = factories.MTUserFactory(is_active=True)
        # don't forget to create their profile explicitly, signals won't be emitted
        newuser_profile = factories.UserProfileFactory(user=newuser)

        # then make sure they can login
        response = self.client.post(reverse('login'), {
            'username': newuser.email,
            'password': factories.DEFAULT_PASSWORD
        }, follow=True)

        self.assertEquals(response.status_code, 200)
        # and that the new user gets redirected to their dashboard
        self.assertRedirects(response, reverse('dashboard'))

    def test_user_canlogout(self):
        """
        Logged-in user can log out properly.
        """
        # create an active test user
        newuser = factories.MTUserFactory(is_active=True)
        newuser_profile = factories.UserProfileFactory(user=newuser)
        login_response = self.client.login(username=newuser.email, password=factories.DEFAULT_PASSWORD)

        # user can login via Django's auth
        self.assertTrue(login_response)

        # user can then logout
        response = self.client.get(reverse('logout'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/logged_out.html')
