from random import randint

from django.urls import reverse
from django.db.models import ObjectDoesNotExist

from walletweb import models
from . import factories
from .utilities import MTTestCase


class TestAccounts(MTTestCase):
    """
    Test MT account-related functionality.
    """

    def test_account_list(self):
        """
        User can list their accounts successfully
        """
        response = self.client.get(reverse('account_list'))

        # successfully navigate to account listing page
        # showing, at least, the first account created in the setup stage
        # but not the account created for the second user
        self.assertVisitedPageWithExpectedText(response, 'web/account/account_list.html',
                                               contains_text=self.account_first.name,
                                               notcontains_text=self.account_second.name)

    def test_account_add(self):
        """
        User can add a new account using an existing currency
        """
        response = self.client.get(reverse('account_add'))

        self.assertVisitedPageWithExpectedText(response, 'web/account/account_add.html')

        potential_newaccount = factories.AccountFactory.build()
        # get first currency, whatever it is to assign it to new account
        first_currency = models.Currency.objects.first()

        add_response = self.client.post(reverse('account_add'), {
            'name': potential_newaccount.name,
            'currency': first_currency.id
        }, follow=True)

        # redirect to account listing after successful addition
        self.assertARedirectThenSuccess(add_response, 'account_list')

        # and account name exists somewhere on the page - safely assumes it was the result of the previous addition
        self.assertContains(add_response, potential_newaccount.name)

    def test_account_edit(self):
        """
        User can edit their accounts
        """
        response = self.client.get(reverse('account_edit', args=[self.account_first.id]))

        # correct template is used
        self.assertVisitedPageWithExpectedText(response, 'web/account/account_edit.html')

        # edit tempalate is showing account requested account
        self.assertContains(response, f'value="{self.account_first.name}"')

        edit_response = self.client.post(reverse('account_edit', args=[self.account_first.id]), {
            'name': f'{self.account_first.name}_mod',
            'currency': self.account_first.currency.id
        }, follow=True)

        # redirect to account listing after successful edit
        self.assertARedirectThenSuccess(edit_response, 'account_list')

    def test_account_delete(self):
        """
        User can delete his accounts
        """
        # create an account for the test user
        some_account = factories.AccountFactory(user=self.first_test_user)

        # ensure that GET'ing the delete page shows a confirmation prompt
        response = self.client.get(reverse('account_delete', args=[some_account.id]))
        # correct template that shows confirmation form
        self.assertVisitedPageWithExpectedText(response, 'web/account/account_confirm_delete.html', contains_text="Yes")

        # POST'ing the page does the actual delete
        post_response = self.client.post(reverse('account_delete', args=[some_account.id]), follow=True)

        # redirect to account listing after successful delete operation
        self.assertARedirectThenSuccess(post_response, 'account_list')

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
