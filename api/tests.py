import json

from django.utils.http import urlencode

from rest_framework.reverse import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from walletweb.tests import factories


class MTTestCase(APITestCase):
    failure_status_code_list = [400, 403, 404]

    def post(self, url, data=None, qparams=None):
        query_params = ''
        if qparams:
            query_params = '?{0}'.format(urlencode(qparams))

        response = self.client.post(url + query_params, data, format='json')
        self.response = response
        return response

    def get(self, url, qparams=None):
        response = self.client.get(url, qparams)
        self.response = response
        return response

    def put(self, url, data=None, qparams=None):
        query_params = ''
        if qparams:
            query_params = '?{0}'.format(urlencode(qparams))

        response = self.client.put(url + query_params, data, format='json')
        self.response = response
        return response

    def delete(self, url, data=None, qparams=None):
        query_params = ''
        if qparams:
            query_params = '?{0}'.format(urlencode(qparams))

        response = self.client.delete(url + query_params, data)
        self.response = response
        return response

    def printResponse(self):
        if self.response:
            print(self.response.content)

    def getResponseAsObject(self):
        if self.response and self.response.content:
            return json.loads(self.response.content.decode('utf-8'))
        else:
            return None

    def assertResponseCodeIs400(self):
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    def assertResponseCodeIs200(self):
        if self.response.status_code in self.failure_status_code_list:
            self.printResponse()
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def assertResponseCodeIs201(self):
        if self.response.status_code in self.failure_status_code_list:
            self.printResponse()
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def assertResponseCodeIs403(self):
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)

    def assertResponseCodeIs404(self):
        self.assertEqual(self.response.status_code, status.HTTP_404_NOT_FOUND)

    def assertResponseCodeIs204(self):
        self.assertEqual(self.response.status_code, status.HTTP_204_NO_CONTENT)

    def setTestUser(self, user):
        """
        Sets user to impersonate when issuing requests to server.
        :param user: User to impersonate when issuing requests to server
        :return: None
        """
        token, created = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class MTAPITest(MTTestCase):
    def setUp(self):
        user = factories.MTUserFactory(is_active=True)
        self.user = user
        self.setTestUser(user)

    # def test_transaction_add(self):
    #     account = factories.AccountFactory(user=self.user)
    #
    #     transaction_create_url = reverse('api-transaction-create')
    #
    #     self.post(transaction_create_url, data={
    #         'amount': 10,
    #         'description': 'test',
    #         'date': '2016-12-26',
    #         'account': 1
    #     })
    #
    #     self.assertResponseCodeIs201()
