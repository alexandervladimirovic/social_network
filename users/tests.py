from django.test import TestCase

from users.models import CustomUser


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
        