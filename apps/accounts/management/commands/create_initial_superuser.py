import os
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = "Create initial superuser from environment variables"

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        phone = os.getenv("DJANGO_SUPERUSER_PHONE")
        full_name = os.getenv("DJANGO_SUPERUSER_FULL_NAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, phone, password]):
            self.stdout.write(self.style.ERROR("Missing superuser env variables"))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING("Superuser already exists"))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            phone=phone,
            full_name=full_name,
            password=password,
        )

        user.role = User.ROLE_ADMIN
        user.is_staff = True
        user.is_active = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f"✅ Superuser created: {user.username}"))
