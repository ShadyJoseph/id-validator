import secrets
import string
from django.core.management.base import BaseCommand
from api.models import ApiKey


class Command(BaseCommand):
    help = 'Create a new API key'

    def add_arguments(self, parser):
        parser.add_argument(
            'user', type=str, help='User identifier for the API key')
        parser.add_argument('--length', type=int, default=32,
                            help='Length of the API key')

    def handle(self, *args, **options):
        user = options['user']
        length = options['length']

        # Generate secure random API key
        alphabet = string.ascii_letters + string.digits
        api_key = ''.join(secrets.choice(alphabet) for _ in range(length))

        # Create API key object
        key_obj = ApiKey(user=user)
        key_obj.set_key(api_key)
        key_obj.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created API key for user "{user}":\n'
                f'API Key: {api_key}\n'
                f'Store this key securely - it cannot be retrieved again!'
            )
        )
