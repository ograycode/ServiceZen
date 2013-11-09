"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse


class TestAuthViews(TestCase):
    def test_login_page_load(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)