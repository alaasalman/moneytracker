from django.test import TestCase

from . import factories


class TestAccounts(TestCase):
    def test_account_list(self):
        account = factories.AccountFactory()

        self.assertEqual(True, True)

    def test_transaction_list(self):
        tranaction = factories.TransactionFactory()

        self.assertEqual(True, True)
