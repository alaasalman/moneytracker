from random import randint

from django.urls import reverse
from django.db.models import ObjectDoesNotExist

from walletweb import models
from . import factories
from .utilities import MTTestCase


class TestAccounts(MTTestCase):
    """
    Test account-related functionality. Two test users are created, but only the first
    one is logged-in.
    """
    def setUp(self):
        # set up an active test user and log them in
        first_test_user = factories.MTUserFactory(is_active=True)
        first_test_user_profile = factories.UserProfileFactory(user=first_test_user)
        self.first_test_user = first_test_user

        login_response = self.client.login(username=first_test_user.email, password=factories.DEFAULT_PASSWORD)

        if not login_response:
            self.skipTest("Could not log in")

        # setup a second test user but do not log them in
        second_test_user = factories.MTUserFactory(is_active=True)
        second_test_user_profile = factories.UserProfileFactory(user=second_test_user)

        # set up a test account and some transactions for first user
        account_first = factories.AccountFactory(user=first_test_user)
        self.account_first = account_first

        for i in range(randint(1, 20)):
            factories.TransactionFactory(account=account_first)

        # set up an account and some transactions for second user
        account_second = factories.AccountFactory(user=second_test_user)
        self.account_second = account_second

        for i in range(randint(1, 10)):
            factories.TransactionFactory(account=account_second)

    def test_account_list(self):
        """
        User can list their accounts successfully
        """
        response = self.client.get(reverse('account_list'))
        # successfully navigate to account listing page
        self.assertEqual(response.status_code, 200)

        # check that it is using the expected template
        self.assertTemplateUsed(response, 'web/account/account_list.html')
        # and that it is at least showing the first account created in the setup stage
        self.assertContains(response, self.account_first.name)
        # but not the account created for the second user
        self.assertNotContains(response, self.account_second.name)

    def test_account_add(self):
        """
        User can add a new account using an existing currency
        """
        response = self.client.get(reverse('account_add'))

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'web/account/account_add.html')

        potential_newaccount = factories.AccountFactory.build()
        # get first currency, whatever it is to assign it to new account
        first_currency = models.Currency.objects.first()

        add_response = self.client.post(reverse('account_add'), {
            'name': potential_newaccount.name,
            'currency': first_currency.id
        }, follow=True)

        # redirect to account listing after successful addition
        self.assertRedirects(add_response, reverse('account_list'))

        # success message is shown
        self.assertSuccessMessageShown(add_response)
        # and account name exists somewhere on the page - safely assumes it was the result of the previous addition
        self.assertContains(add_response, potential_newaccount.name)

    def test_account_edit(self):
        """
        User can edit their accounts
        """
        response = self.client.get(reverse('account_edit', args=[self.account_first.id]))

        # check that edit is using expected template
        self.assertTemplateUsed(response, 'web/account/account_edit.html')

        # edit tempalate is showing account requested account
        self.assertContains(response, f'value="{self.account_first.name}"')

        edit_response = self.client.post(reverse('account_edit', args=[self.account_first.id]), {
            'name': f'{self.account_first.name}_mod',
            'currency': self.account_first.currency.id
        }, follow=True)

        # redirect to account listing after successful edit
        self.assertRedirects(edit_response, reverse('account_list'))
        # and show a success message being a successful edit
        self.assertSuccessMessageShown(edit_response)

    def test_account_delete(self):
        """
        User can delete his accounts
        """
        # create an account for the test user
        some_account = factories.AccountFactory(user=self.first_test_user)

        # ensure that GET'ing the delete page shows a confirmation prompt
        response = self.client.get(reverse('account_delete', args=[some_account.id]))
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Yes")

        # POST'ing the page does the actual delete
        post_response = self.client.post(reverse('account_delete', args=[some_account.id]), follow=True)

        # redirect to account listing after successful delete operation
        self.assertRedirects(post_response, reverse('account_list'))
        # and show a success message
        self.assertSuccessMessageShown(post_response)

        # assert that the object no longer exists in the database
        with self.assertRaises(ObjectDoesNotExist):
            models.Account.objects.get(pk=some_account.id)

    def test_account_edit_own(self):
        """
        User can only edit their own accounts
        """
        # try to edit account belonging to second user while logged in as first user
        response = self.client.get(reverse('account_edit', args=[self.account_second.id]))
        # expect a 404
        self.assertEqual(response.status_code, 404)

    def test_account_delete_own(self):
        """
        User can only delete their own account
        """
        # first user is logged in so he shouldn't be able to delete account for second user
        response = self.client.get(reverse('account_delete', args=[self.account_second.id]))
        # expect a 404 for an account that isn't theirs
        self.assertEqual(response.status_code, 404)
