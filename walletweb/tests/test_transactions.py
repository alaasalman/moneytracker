from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from walletweb import models
from . import factories
from .utilities import MTTestCase, transactionforuser


class TestTransactions(MTTestCase):
    """
    Test transaction-related functionality.
    """

    def test_transaction_list(self):
        """
        User can list their transactions
        """
        response = self.client.get(reverse('transaction_list_all'))

        self.assertVisitedPageWithExpectedText(response, 'web/transaction/transaction_list.html')

    def test_transaction_add(self):
        """
        User can add a transaction
        """
        response = self.client.get(reverse('transaction_add'))

        self.assertVisitedPageWithExpectedText(response, 'web/transaction/transaction_add.html')

        potential_transaction = factories.TransactionFactory.build(account=self.account_first)

        add_response = self.client.post(reverse('transaction_add'), {
            'account': potential_transaction.account.id,
            'amount': potential_transaction.amount,
            'description': potential_transaction.description,
            'date': potential_transaction.date.date().isoformat(),
            'currency': self.account_first.currency.id
        }, follow=True)

        self.assertARedirectThenSuccess(add_response, 'transaction_list_all')

    def test_transaction_edit(self):
        """
        User can edit their transactions
        """
        some_user_transaction = transactionforuser(user=self.first_test_user)

        response = self.client.get(reverse('transaction_edit', args=[some_user_transaction.id]))

        # correct template is used
        self.assertVisitedPageWithExpectedText(response, 'web/transaction/transaction_edit.html')

        # edit template is showing requested transaction
        self.assertContains(response, f'value="{some_user_transaction.description}"')

        edit_response = self.client.post(reverse('transaction_edit', args=[some_user_transaction.id]), {
            'amount': some_user_transaction.amount,
            'description': f'{some_user_transaction.description}_mod',
            'date': some_user_transaction.date,
            'currency': some_user_transaction.currency.id
        }, follow=True)

        self.assertARedirectThenSuccess(edit_response, 'transaction_list_all')

    def test_transaction_delete(self):
        """
        User can delete their transactions
        """
        some_user_transaction = transactionforuser(user=self.first_test_user)

        # ensure that GET'ing the delete page shows a confirmation prompt
        response = self.client.get(reverse('transaction_delete', args=[some_user_transaction.id]))
        # correct template that shows confirmation form
        self.assertVisitedPageWithExpectedText(response,
                                               'web/transaction/transaction_confirm_delete.html',
                                               contains_text="Yes")

        # POST'ing the page does the actual delete
        post_response = self.client.post(reverse('transaction_delete', args=[some_user_transaction.id]), follow=True)

        self.assertARedirectThenSuccess(post_response, 'transaction_list_all')

        # assert that the object no longer exists in the database
        with self.assertRaises(ObjectDoesNotExist):
            models.Transaction.objects.get(pk=some_user_transaction.id)

    def test_transaction_edit_own(self):
        """
        User can only edit their own transactions
        """
        second_user_transaction = transactionforuser(self.second_test_user)

        # try to edit a transaction belonging to second user while logged in as first user
        response = self.client.get(reverse('transaction_edit', args=[second_user_transaction.id]))
        # expect a 404
        self.assertEqual(response.status_code, 404)

    def test_transaction_delete_own(self):
        """
        User can only delete their own transactions
        """
        second_user_transaction = transactionforuser(self.second_test_user)

        # first user is logged in so he shouldn't be able to delete a transaction for second user
        response = self.client.get(reverse('transaction_delete', args=[second_user_transaction.id]))
        # expect a 404 for a transaction that isn't theirs
        self.assertEqual(response.status_code, 404)

# test transactions - with/without filter
