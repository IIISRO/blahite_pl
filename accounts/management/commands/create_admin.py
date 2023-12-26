from django.core.management.base import BaseCommand
from accounts.models import User
class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Create Admin')
        parser.add_argument('password', type=str, help='Create Admin')


    def handle(self, *args, **kwargs):
        email = kwargs['email']
        password = kwargs['password']
        try:
            new_admin = User(email=email, is_staff = True, is_superuser = True)
            new_admin.set_password(password)
            new_admin.save()
        except AssertionError:
            return AssertionError


