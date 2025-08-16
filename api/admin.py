import secrets
import string
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import ApiKey, Log


class ApiKeyAdminForm(forms.ModelForm):
    """Custom form for API key creation"""

    api_key_input = forms.CharField(
        max_length=64,
        required=False,
        help_text="Leave blank to auto-generate a secure API key",
        widget=forms.TextInput(
            attrs={'placeholder': 'Auto-generate (recommended)'})
    )

    class Meta:
        model = ApiKey
        fields = ['user', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Editing existing key
            self.fields.pop('api_key_input', None)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not self.instance.pk:  # New instance only
            api_key = self.cleaned_data.get(
                'api_key_input') or self._generate_api_key()
            instance.set_key(api_key)
            instance._generated_key = api_key

        if commit:
            instance.save()
        return instance

    def _generate_api_key(self):
        """Generate secure 32-character API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    form = ApiKeyAdminForm
    list_display = ['user', 'key_preview_display', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user']

    class Media:
        css = {
            'all': ('api/admin_styles.css',)
        }
        js = ('api/admin_scripts.js',)

    def get_fieldsets(self, request, obj=None):
        """Dynamic fieldsets based on context"""
        if obj and self._has_generated_key(request, obj):
            return self._get_key_display_fieldsets()
        elif obj:
            return self._get_edit_fieldsets()
        else:
            return self._get_add_fieldsets()

    def get_readonly_fields(self, request, obj=None):
        """Dynamic readonly fields"""
        base_fields = ['key_hash', 'encrypted_key',
                       'key_preview', 'created_at']

        if obj and self._has_generated_key(request, obj):
            return base_fields + ['display_generated_key', 'user']
        elif obj:
            return base_fields
        else:
            return base_fields

    def key_preview_display(self, obj):
        """Display masked key preview"""
        return f"****{obj.key_preview}"
    key_preview_display.short_description = 'Key Preview'

    def display_generated_key(self, obj):
        """Display generated API key with copy functionality"""
        generated_key = self._get_generated_key(obj)
        if not generated_key:
            return '<p>API key will appear here after creation</p>'

        return format_html(
            '<div id="key-box" class="key-display">'
            '<h3>Your API Key</h3>'
            '<p><strong>Copy this key - it cannot be retrieved again!</strong></p>'
            '<code class="api-key-code">{}</code>'
            '<button type="button" onclick="copyKey(\'{}\', this)" class="copy-btn">Copy</button>'
            '<button type="button" onclick="hideKeyBox()" class="hide-btn">Done</button>'
            '</div>',
            generated_key, generated_key
        )

    display_generated_key.short_description = 'Generated API Key'

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Store request for session access"""
        self._current_request = request
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """Save model and handle session storage"""
        if not change and hasattr(obj, '_generated_key'):
            generated_key = obj._generated_key

        super().save_model(request, obj, form, change)

        if not change and 'generated_key' in locals():
            request.session[f'generated_key_{obj.pk}'] = generated_key
            request.session.modified = True
            messages.success(
                request, f'API Key created for "{obj.user}". Copy it from below!')

    def response_add(self, request, obj, post_url_override=None):
        """Redirect to change view to show generated key"""
        if '_continue' not in request.POST and '_addanother' not in request.POST:
            return HttpResponseRedirect(reverse('admin:api_apikey_change', args=[obj.pk]))
        return super().response_add(request, obj, post_url_override)

    def response_change(self, request, obj):
        """Clean up session on navigation"""
        if '_continue' not in request.POST:
            session_key = f'generated_key_{obj.pk}'
            request.session.pop(session_key, None)
            request.session.modified = True
        return super().response_change(request, obj)

    # Helper methods
    def _has_generated_key(self, request, obj):
        """Check if object has generated key in session"""
        return request.session.get(f'generated_key_{obj.pk}') is not None

    def _get_generated_key(self, obj):
        """Get generated key from session or object"""
        if hasattr(self, '_current_request'):
            return self._current_request.session.get(f'generated_key_{obj.pk}')
        return getattr(obj, '_generated_key', None)

    def _get_key_display_fieldsets(self):
        """Fieldsets for displaying generated key"""
        return (
            ('Your New API Key', {
                'fields': ('display_generated_key',),
                'description': 'Copy your API key now - it cannot be retrieved later!'
            }),
            ('Key Details', {'fields': ('user', 'is_active')}),
            ('System Info', {
                'fields': ('key_hash', 'encrypted_key', 'key_preview', 'created_at'),
                'classes': ('collapse',)
            }),
        )

    def _get_edit_fieldsets(self):
        """Fieldsets for editing existing key"""
        return (
            (None, {'fields': ('user', 'is_active')}),
            ('System Info', {
                'fields': ('key_hash', 'encrypted_key', 'key_preview', 'created_at'),
                'classes': ('collapse',)
            }),
        )

    def _get_add_fieldsets(self):
        """Fieldsets for adding new key"""
        return (
            (None, {'fields': ('user', 'api_key_input', 'is_active')}),
            ('System Info', {
                'fields': ('key_hash', 'encrypted_key', 'key_preview', 'created_at'),
                'classes': ('collapse',)
            }),
        )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'national_id', 'valid', 'api_key_used']
    list_filter = ['valid', 'timestamp']
    search_fields = ['national_id', 'api_key_used']
    readonly_fields = ['timestamp', 'national_id',
                       'valid', 'extracted_data', 'error', 'api_key_used']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True
