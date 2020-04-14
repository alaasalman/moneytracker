from django.test import TestCase, modify_settings
from django.contrib.messages import constants


# remove django-axes as an auth backend for this test, it doesn't play nice with the client
# plus it isn't needed for tests
@modify_settings(AUTHENTICATION_BACKENDS={
    'remove': 'axes.backends.AxesBackend'
})
class MTTestCase(TestCase):
    """
    Utility class with some useful additions specific to MoneyTracker
    """
    def assertSuccessMessageShown(self, response):
        self.assertIn('messages', response.context)
        messages_list = list(response.context['messages'])
        self.assertEquals(len(messages_list), 1)

        first_message = messages_list[0]
        self.assertEquals(first_message.level, constants.SUCCESS)
