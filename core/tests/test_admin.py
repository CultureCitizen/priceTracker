from urllib.parse import ParseResultBytes
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

import logging

logger = logging.getLogger('django_test')
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

logger.warning('>>> test_log')


class AdminSiteTests(TestCase):

    # Create users for testing  : admin, user1
    def setUp(self):
        base = get_user_model().objects
        self.client = Client()
        self.admin_user = base.create_superuser(
            email='admin@londonappdev.com',
            password='passwordAdmin1',
            username='admin')
        self.client.force_login(self.admin_user)
        self.user = base.create_user(
            email='user1@londonappdev.com',
            password='passwordUser1',
            username='Test user fullname')

    def test_users_listed(self):
        """Test that users are listed"""
        # this urls are defined in the django documentation. They map a variable to URL
        # /admin/core/user/id/
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        logger.warning(">>> list users url:"+url)

        self.assertContains(res, self.user.username)
        self.assertContains(res, self.user.email)


class EmailVerificationTest(APITestCase):
    # djoser user management tests

    # endpoints for tests
    register_url = "/auth/users/"
    activate_url = "/auth/users/activation/"
    login_url = "/auth/token/login/"
    user_details_url = "/auth/users/"
    resend_verification_url = "/auth/users/resend_activation/"

    # user infofmation
    user_data = {
        "email": "test@example.com",
        "username": "test_user",
        "password": "verysecret"
    }
    login_data = {
        "email": "test@example.com",
        "password": "verysecret"
    }

    def test_register_with_email_verification(self):
        # register the new user
        response = self.client.post(
            self.register_url, self.user_data, format="json")

        url = self.register_url
        logger.warning(">>> register user url:" + url)
        # expected response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # expected one email to be send
        self.assertEqual(len(mail.outbox), 1)

        # parse email to get uid and token
        email_lines = mail.outbox[0].body.splitlines()
        # you can print email to check it
        logger.warning(">>> mail subject: "+mail.outbox[0].subject)
        logger.warning(">>> mail body:"+mail.outbox[0].body)

        # get the url of the activation link
        activation_link = [l for l in email_lines if "/activate/" in l][0]
        uid, token = activation_link.split("/")[-2:]

        # verify email
        data = {"uid": uid, "token": token}
        response = self.client.post(self.activate_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # login to get the authentication token
        response = self.client.post(
            self.login_url, self.login_data, format="json")
        self.assertTrue("auth_token" in response.json())
        token = response.json()["auth_token"]

        # set token in the header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        # get user details
        response = self.client.get(self.user_details_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["email"], self.user_data["email"])
        self.assertEqual(
            response.json()[0]["username"], self.user_data["username"])

    def test_register_resend_verification(self):
        # register the new user
        response = self.client.post(
            self.register_url, self.user_data, format="json")
        # expected response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # expected one email to be send
        self.assertEqual(len(mail.outbox), 1)

        # login to get the authentication token
        response = self.client.post(
            self.login_url, self.login_data, format="json")
        self.assertTrue("auth_token" in response.json())
        token = response.json()["auth_token"]

        # set token in the header
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        # try to get user details
        response = self.client.get(self.user_details_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # clear the auth_token in header
        self.client.credentials()
        # resend the verification email
        data = {"email": self.user_data["email"]}
        response = self.client.post(
            self.resend_verification_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # there should be two emails in the outbox
        self.assertEqual(len(mail.outbox), 2)

        # parse the last email
        email_lines = mail.outbox[1].body.splitlines()
        activation_link = [l for l in email_lines if "/activate/" in l][0]
        uid, token = activation_link.split("/")[-2:]

        # verify the email
        data = {"uid": uid, "token": token}
        response = self.client.post(self.activate_url, data, format="json")
        # email verified
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_resend_verification_wrong_email(self):
        # register the new user
        response = self.client.post(
            self.register_url, self.user_data, format="json")
        # expected response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # resend the verification email but with WRONG email
        data = {"email": self.user_data["email"]+"_this_email_is_wrong"}
        response = self.client.post(
            self.resend_verification_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_with_wrong_uid_token(self):
        # register the new user
        response = self.client.post(
            self.register_url, self.user_data, format="json")
        # expected response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # verify the email with wrong data
        data = {"uid": "wrong-uid", "token": "wrong-token"}
        response = self.client.post(self.activate_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
