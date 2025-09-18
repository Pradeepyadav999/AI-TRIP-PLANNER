from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection

class Command(BaseCommand):
    help = 'Create a superuser with all required fields without requiring migrations to be run'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Check if the auth_user table exists (old Django User model)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user';"
            )
            auth_user_exists = cursor.fetchone() is not None

        if auth_user_exists:
            # Create table for our custom user model if it doesn't exist
            with connection.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts_customuser (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    password VARCHAR(128) NOT NULL,
                    last_login DATETIME NULL,
                    is_superuser BOOL NOT NULL,
                    username VARCHAR(150) NOT NULL UNIQUE,
                    first_name VARCHAR(150) NOT NULL,
                    last_name VARCHAR(150) NOT NULL,
                    is_staff BOOL NOT NULL,
                    is_active BOOL NOT NULL,
                    date_joined DATETIME NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(254) NOT NULL UNIQUE,
                    gender VARCHAR(1) NULL,
                    date_of_birth DATE NULL,
                    preferred_language VARCHAR(2) NOT NULL,
                    travel_preferences VARCHAR(20) NOT NULL,
                    travel_history TEXT NULL,
                    budget_range VARCHAR(10) NOT NULL,
                    current_latitude REAL NULL,
                    current_longitude REAL NULL,
                    profile_picture VARCHAR(100) NULL,
                    account_status VARCHAR(10) NOT NULL,
                    is_verified BOOL NOT NULL
                );
                """)

            # Create a superuser
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='adminpassword',
                    full_name='Administrator',
                    preferred_language='EN',
                    travel_preferences='adventure',
                    budget_range='medium',
                    account_status='active',
                    is_verified=True
                )
                self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
            else:
                self.stdout.write(self.style.WARNING('Superuser already exists.'))
        else:
            self.stdout.write(self.style.ERROR('auth_user table does not exist. Run migrations first.')) 