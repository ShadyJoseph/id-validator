from django.test import TestCase, RequestFactory, override_settings
from django.core.management import call_command
from django.contrib.admin.sites import AdminSite
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from io import StringIO

from api.models import ApiKey, Log
from api.admin import ApiKeyAdmin


class NationalIDViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('national_id')
        self.test_key = "test_key_12345678901234567890"

        self.api_key = ApiKey.objects.create(user="testuser", is_active=True)
        self.api_key.set_key(self.test_key)
        self.api_key.save()

    def auth(self, key=None):
        """Helper to set API key credentials"""
        self.client.credentials(HTTP_X_API_KEY=key or self.test_key)

    def post_id(self, nid):
        """Helper to post national_id payload"""
        return self.client.post(self.url, {"national_id": nid}, format='json')

    def test_post_without_api_key(self):
        response = self.client.post(
            self.url, {"national_id": "30307020102113"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_with_invalid_api_key(self):
        self.auth("invalid_key")
        response = self.post_id("30307020102113")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_valid_national_id(self):
        self.auth()
        response = self.post_id("30307020102113")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['birth_year'], 2003)
        self.assertEqual(response.data['gender'], 'Male')
        self.assertEqual(response.data['governorate'], 'Cairo')

    def test_post_invalid_national_id(self):
        self.auth()
        response = self.post_id("40307020102113")  # Invalid century
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valid'])
        self.assertIn('error', response.data)

    def test_post_invalid_request_data(self):
        self.auth()
        response = self.post_id("123")  # Too short
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valid'])

    def test_post_missing_national_id(self):
        self.auth()
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valid'])

    def test_request_creates_log(self):
        initial_count = Log.objects.count()
        self.auth()
        self.post_id("30307020102113")
        self.assertEqual(Log.objects.count(), initial_count + 1)
        log = Log.objects.latest('timestamp')
        self.assertEqual(log.national_id, "30307020102113")
        self.assertTrue(log.valid)


@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PERMISSION_CLASSES': [],
        'DEFAULT_THROTTLE_CLASSES': ['api.throttling.ApiKeyRateThrottle'],
        'DEFAULT_THROTTLE_RATES': {'api_key': '2/minute'}
    },
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
def test_rate_limiting(self):
    from rest_framework.settings import reload_api_settings
    reload_api_settings()  # <- forces DRF to pick up override_settings

    self.auth()
    self.assertEqual(self.post_id(
        "30307020102113").status_code, status.HTTP_200_OK)
    self.assertEqual(self.post_id(
        "30307020102113").status_code, status.HTTP_200_OK)
    self.assertEqual(self.post_id("30307020102113").status_code,
                     status.HTTP_429_TOO_MANY_REQUESTS)


class ApiKeyAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ApiKeyAdmin(ApiKey, self.site)
        self.factory = RequestFactory()

    def _prepare_request(self):
        request = self.factory.get('/')
        SessionMiddleware(lambda r: None).process_request(request)
        request.session.save()
        MessageMiddleware(lambda r: None).process_request(request)
        return request

    def test_save_model_generates_key(self):
        request = self._prepare_request()
        form = self.admin.get_form(request)()
        form.cleaned_data = {'user': 'test', 'api_key_input': ''}
        obj = form.save(commit=False)
        self.admin.save_model(request, obj, form, change=False)
        self.assertTrue(obj.key_hash)
        self.assertTrue(request.session.get(f'generated_key_{obj.pk}'))

    def test_get_fieldsets_add(self):
        request = self.factory.get('/')
        fieldsets = self.admin.get_fieldsets(request)
        fields = [f for _, opts in fieldsets for f in opts['fields']]
        self.assertIn('api_key_input', fields)


class CreateApiKeyCommandTest(TestCase):
    def test_command_creates_key(self):
        out = StringIO()
        call_command('create_api_key', 'testuser', stdout=out)
        self.assertIn('Successfully created API key', out.getvalue())
        self.assertEqual(ApiKey.objects.count(), 1)
        self.assertEqual(ApiKey.objects.first().user, 'testuser')
