from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models

USER = 'user'
ADMIN = 'admin'
ROLE_CHOICES = [
    (USER, 'Пользователь'),
    (ADMIN, 'Администратор'),
]


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(),),
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        choices=ROLE_CHOICES,
        max_length=20,
        default=USER,
    )
    avatar = models.ImageField(
        verbose_name='Аватар пользователя',
        upload_to='users/avatars',
        null=True,
        blank=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.username and not self.email:
            raise ValueError(
                'Должно быть установлено имя пользователя и email.'
            )
        super().save(*args, **kwargs)


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Подписан'
    )

    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe'
            )
        ]

    def __str__(self):
        return f'{self.user.email} подписан на {self.author.email}'

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
