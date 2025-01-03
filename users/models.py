import logging
from typing import Any, Optional

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.core.files.images import get_image_dimensions


logger = logging.getLogger(__name__)


def validate_avatar(image) -> None:
    """
    Валидатор для проверки аватара.
    Проверяет формат файла и размер изображения.
    """
    max_width = 800
    max_height = 800

    max_image_size = 5 * 1024 * 1024

    if image.size > max_image_size:
        logger.error('Avatar file size must not exceed 5MB')
        raise ValidationError(_("Avatar file size must not exceed 5MB"))

    try:
        width, height = get_image_dimensions(image)

        if width is None or height is None:
            logger.error('Invalid file image')
            raise ValidationError(_("Invalid file image"))

        if width > max_width or height > max_height:
            logger.error('Avatar dimensions must not exceed 800x800 pixels')
            raise ValidationError(_("Avatar dimensions must not exceed 800x800 pixels"))

    except Exception as e:
        logger.error('Invalid image file')
        raise ValidationError(_("Invalid image file")) from e


class CustomUserManager(UserManager):
    """
    Менеджер для модели CustomUser.
    """

    @staticmethod
    def _validate_email(email: str) -> None:

        email_validator = EmailValidator()

        try:
            email_validator(email)
        except ValidationError as e:
            logger.error('Invalid email address')
            raise ValueError(_("Invalid email address")) from e

    def create_user(
        self,
        username: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        **extra_fields: Any,
    ) -> "CustomUser":
        """
        Создает и сохраняет нового пользователя с заданными параметрами.

        Параметры:
        - username: Имя пользователя.
        - email: Электронная почта пользователя.
        - password: Пароль пользователя.
        - **extra_fields: Дополнительные поля для создания пользователя.
        """

        if email is None:
            logger.error('The email field cannot be None')
            raise ValueError(_("The email field cannot be None"))

        if password is None:
            logger.error('The password field cannot be None')
            raise ValueError(_("The password field cannot be None"))

        self._validate_email(email)

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)

        try:
            user.save(using=self._db)
        except IntegrityError as e:
            logger.error("The email address '{%s}' is already in use", email)
            raise ValueError(_(f"The email address '{email}' is already in use")) from e

        return user

    def create_superuser(
        self,
        username: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        **extra_fields: Any,
    ) -> "CustomUser":
        """
        Создает и возвращает суперпользователя с заданными параметрами.

        Параметры:
        - username: Имя пользователя для суперпользователя.
        - email: Адрес электронной почты суперпользователя.
        - password: Пароль для суперпользователя.
        - **extra_fields: Дополнительные поля для создания суперпользователя.

        Примечания:
        Этот метод вызывает метод create_user, но устанавливает параметры 'is_staff' и 'is_superuser' в True.
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            logger.error("Superuser must have is_staff=True.")
            raise ValueError(_("Superuser must have is_staff=True."))

        if extra_fields.get("is_superuser") is not True:
            logger.error("Superuser must have is_superuser=True.")
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Модель пользователя с дополнительными полями: аватар и биография.

    Атрибуты:
    avatar: Поле для изображения аватара пользователя.
    bio: Поле для биографии пользователя.
    """

    avatar = models.ImageField(
        _("Avatars"),
        upload_to="avatars/",
        null=True,
        blank=True,
        validators=[validate_avatar],
    )
    bio = models.TextField(_("Biography"), null=True, blank=True)  # type: ignore[var-annotated]
    email = models.EmailField(_("Email address"), unique=True, blank=False, null=False)

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.username
