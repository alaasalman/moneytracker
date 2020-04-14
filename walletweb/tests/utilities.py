from random import randint

from django.urls import reverse
from django.test import TestCase, modify_settings
from django.contrib.messages import constants

from walletweb import models
from . import factories


def transactionforuser(user):
    """
    Return a transaction for specified user. There's no guarantee that any specific transaction is returned.
    :param user: Specific MT user
    :return: A user transaction
    """
    return models.Transaction.objects.filter(user=user).first()


# remove django-axes as an auth backend for this test, it doesn't play nice with the client
# plus it isn't needed for tests
@modify_settings(AUTHENTICATION_BACKENDS={
    'remove': 'axes.backends.AxesBackend'
})
class MTTestCase(TestCase):
    """
    Utility class with some useful additions specific to MoneyTracker
    """

    def setUp(self):
        """
        Two test users are created, but only the first one is logged-in.
        """
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
        self.second_test_user = second_test_user

        # set up a test account and some transactions for first user
        account_first = factories.AccountFactory(user=first_test_user)
        self.account_first = account_first

        for i in range(randint(1, 20)):
            factories.TransactionFactory(account=account_first, user=first_test_user)

        # set up an account and some transactions for second user
        account_second = factories.AccountFactory(user=second_test_user)
        self.account_second = account_second

        for i in range(randint(1, 10)):
            factories.TransactionFactory(account=account_second, user=second_test_user)

    def assertMessageShown(self, response, message_type=constants.SUCCESS):
        """
        Asserts that a message is shown on the template using Django's messaging system.
        A message type can be specified, it defaults to a success message.
        :param response: Response result to check
        :param message_type: One of django.contrib.messages.constants for message types
        """
        self.assertIn('messages', response.context)
        messages_list = list(response.context['messages'])
        self.assertEquals(len(messages_list), 1)

        first_message = messages_list[0]
        self.assertEquals(first_message.level, message_type)

    def assertVisitedPageWithExpectedText(self,
                                          response,
                                          template_used=None,
                                          contains_text=None,
                                          notcontains_text=None):
        """
        Assert that the response is a result of a successful page visit(code 200) and that the
        page we're on optionally contains some text but optionally does not contain some other text.
        :param response: Response result to check
        :param template_used: Full template path
        :param contains_text: Text that should be on page
        :param notcontains_text: Text that should not exist
        :return: None
        """
        # successfully navigated to page
        self.assertEqual(response.status_code, 200)

        if template_used:
            # check that it is using the expected template
            self.assertTemplateUsed(response, template_used)

        if contains_text:
            # and that the response contains some expected text fragment
            self.assertContains(response, contains_text)

        if notcontains_text:
            # and does not contain another text fragment
            self.assertNotContains(response, notcontains_text)

    def assertARedirectThenSuccess(self, response, url_name):
        """
        Assert that a redirect has happened and that a success message is then shown afterwards.
        :param response: Response to check
        :param url_name: Url name. Will be reversed.
        :return:
        """
        # a redirect should've happened to url_name
        self.assertRedirects(response, reverse(url_name))
        # and a success message is shown
        self.assertMessageShown(response, message_type=constants.SUCCESS)

    def printBodyContainer(self, response):
        content = str(response.content)

        print(content[content.find('"container">'):content.find('<footer')])
