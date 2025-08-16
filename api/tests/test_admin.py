from django.contrib.admin.sites import AdminSite
from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from api.admin import ApiKeyAdmin
from api.models import ApiKey


class ApiKeyAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ApiKeyAdmin(ApiKey, self.site)
        self.factory = RequestFactory()

    def _setup_request(self, request):
        """Helper to set up request with required middleware"""
        # Enable session
        session_middleware = SessionMiddleware(lambda r: None)
        session_middleware.process_request(request)
        request.session.save()

        # Enable messages
        message_middleware = MessageMiddleware(lambda r: None)
        message_middleware.process_request(request)

        # Set messages storage (required for testing)
        setattr(request, '_messages', FallbackStorage(request))

        return request

    def test_save_model_generates_key(self):
        request = self.factory.get('/')
        request = self._setup_request(request)

        form = self.admin.get_form(request)()
        form.cleaned_data = {'user': 'test', 'api_key_input': ''}
        obj = form.save(commit=False)
        self.admin.save_model(request, obj, form, change=False)

        # Verify key was generated
        self.assertTrue(obj.key_hash)
        self.assertTrue(request.session.get(f'generated_key_{obj.pk}'))

        # Verify message was added
        messages = list(request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn('API Key created', str(messages[0]))

    def test_save_model_with_custom_key(self):
        """Test saving with custom API key"""
        request = self.factory.get('/')
        request = self._setup_request(request)

        custom_key = "custom_test_key_123456789012"
        form = self.admin.get_form(request)()
        form.cleaned_data = {'user': 'test', 'api_key_input': custom_key}
        obj = form.save(commit=False)
        self.admin.save_model(request, obj, form, change=False)

        # Verify custom key was used
        self.assertTrue(obj.key_hash)
        self.assertEqual(request.session.get(
            f'generated_key_{obj.pk}'), custom_key)

    def test_save_model_edit_existing(self):
        """Test editing existing key doesn't regenerate"""
        # Create existing key
        api_key = ApiKey.objects.create(user="existing_user", is_active=True)
        api_key.set_key("existing_key_123456789012")
        api_key.save()

        request = self.factory.get('/')
        request = self._setup_request(request)

        form = self.admin.get_form(request, api_key)()
        form.instance = api_key
        form.cleaned_data = {'user': 'updated_user', 'is_active': False}

        original_key_hash = api_key.key_hash
        self.admin.save_model(request, api_key, form, change=True)

        # Key hash should remain the same
        self.assertEqual(api_key.key_hash, original_key_hash)
        # No generated key in session for edits
        self.assertIsNone(request.session.get(f'generated_key_{api_key.pk}'))

    def test_get_fieldsets_add(self):
        request = self.factory.get('/')
        fieldsets = self.admin.get_fieldsets(request)
        self.assertIn('api_key_input', [
            f for fs in fieldsets for f in fs[1]['fields']])

    def test_get_fieldsets_edit(self):
        """Test fieldsets for editing existing key"""
        api_key = ApiKey.objects.create(user="test_user", is_active=True)
        api_key.set_key("test_key_123456789012")
        api_key.save()

        request = self.factory.get('/')
        request = self._setup_request(request)

        fieldsets = self.admin.get_fieldsets(request, api_key)
        # Should not have api_key_input field for editing
        fields = [f for fs in fieldsets for f in fs[1]['fields']]
        self.assertNotIn('api_key_input', fields)
        self.assertIn('user', fields)
        self.assertIn('is_active', fields)

    def test_key_preview_display(self):
        """Test key preview display method"""
        api_key = ApiKey.objects.create(user="test_user", is_active=True)
        api_key.set_key("test_key_123456789012")
        api_key.save()

        preview = self.admin.key_preview_display(api_key)
        self.assertTrue(preview.startswith('****'))
        self.assertEqual(len(preview), 8)  # 4 stars + 4 characters
