import pytest
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from .models import CustomUser
from .serializers import (
    CustomUserSerializer,
    RegisterSerializer,
    TokenObtainPairSerializer
)


class CustomUserTest(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password'
        )

        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.email, 'sample_email@gmail.com')
        self.assertTrue(user.check_password('test_password'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_no_email(self):

        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username='test_user',
                password='test_password',
                email=None
            )
        self.assertEqual(str(context.exception), "The email field cannot be None")

    def test_create_user_no_password(self):

        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username='test_user',
                email='sample_email@gmail.com',
                password=None
            )
            self.assertEqual(str(context.exception), "The password field cannot be None")

    def test_create_user_duplicate_email(self):
        CustomUser.objects.create_user(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password'
        )

        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username='test_user',
                email='sample_email@gmail.com',
                password='test_password'
            )
        self.assertEqual(str(context.exception), "The email address 'sample_email@gmail.com' is already in use")

    def test_create_superuser(self):
        user = CustomUser.objects.create_superuser(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password'
        )

        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.email, 'sample_email@gmail.com')
        self.assertTrue(user.check_password('test_password'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_no_is_staff(self):

        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_superuser(
                username='test_user',
                email='sample_email@gmail.com',
                password='test_password',
                is_staff=None
            )
        self.assertEqual(str(context.exception), "Superuser must have is_staff=True.")

    def test_create_superuser_no_is_superuser(self):

        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_superuser(
                username='test_user',
                email='sample_email@gmail.com',
                password='test_password',
                is_superuser=None
            )
        self.assertEqual(str(context.exception), "Superuser must have is_superuser=True.")

    def test_password_is_hasher(self):
        user = CustomUser.objects.create_user(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password'
        )

        self.assertNotEqual(user.password, "securepassword123")
        self.assertTrue(user.password.startswith("pbkdf2"))


@pytest.mark.django_db
class TestCustomUserSerializer:
    def test_custom_user_serializer(self):

        user = CustomUser.objects.create_user(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password'
        )

        serializer = CustomUserSerializer(user)

        assert serializer.data["username"] == "test_user"
        assert serializer.data["email"] == "sample_email@gmail.com"


@pytest.mark.django_db
class TestRegisterSerializer:
    def test_register_serializer_success(self):

        data = {
            "username": "test_user",
            "email": "sample_email@gmail.com",
            "password": "test_password",
            "password2": "test_password"
        }

        serializer = RegisterSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()
        assert user.username == "test_user"
        assert user.email == "sample_email@gmail.com"

    def test_register_serializer_password_do_not_match(self):

        data = {
            "username": "test_user",
            "email": "sample_email@gmail.com",
            "password": "test_password1",
            "password2": "test_password"
        }

        serializer = RegisterSerializer(data=data)

        assert not serializer.is_valid()
        assert "Passwords do not match" in serializer.errors["non_field_errors"]

    def test_register_serializer_username_already(self):
        CustomUser.objects.create_user(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password'
        )

        data = {
            "username": "test_user",
            "email": "sample@gmail.com",
            "password": "test_password",
            "password2": "test_password"
        }

        serializer = RegisterSerializer(data=data)

        assert not serializer.is_valid()
        assert _("Пользователь с таким именем уже существует.") in serializer.errors["username"]  # NOT LIKE THIS

    def test_register_serializer_email_already(self):
        CustomUser.objects.create_user(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password'
        )

        data = {
            "username": "test_user1",
            "email": "sample_email@gmail.com",
            "password": "test_password",
            "password2": "test_password"
        }

        serializer = RegisterSerializer(data=data)

        assert not serializer.is_valid()
        assert _("пользователь с таким Адрес электронной почты уже существует.") in serializer.errors["email"]  # NOT LIKE THIS


@pytest.mark.django_db
class TestTokenObtainPairSerializer:
    def test_token_obtain_pair_serializer_success(self):

        CustomUser.objects.create_user(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password'
        )

        data = {
            "username": "test_user",
            "password": "test_password"
        }

        serializer = TokenObtainPairSerializer(data=data)

        assert serializer.is_valid()
        tokens = serializer.validated_data

        assert "access" in tokens
        assert "refresh" in tokens

        # Узнать про черный список в JWT

    def test_token_obtain_pair_serializer_invalid(self):
        data = {
            "username": "test_user",
            "password": "test_password"
        }

        serializer = TokenObtainPairSerializer(data=data)

        assert not serializer.is_valid()
        assert "Invalid username or password" in serializer.errors["non_field_errors"]

    def test_token_obtain_pair_serializer_inactive_user(self):
        CustomUser.objects.create_user(
            username='test_user',
            email='sample_email@gmail.com',
            password='test_password',
            is_active=False
        )

        data = {
            "username": "test_user",
            "password": "test_password"
        }

        serializer = TokenObtainPairSerializer(data=data)

        assert not serializer.is_valid()
        assert "Invalid username or password" in serializer.errors["non_field_errors"]
        