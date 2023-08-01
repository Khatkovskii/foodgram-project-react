from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import DateTimeField

class User(AbstractUser):
    '''Кастомная модель пользователя'''
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    
    GUEST = 'guest'
    AUTHORIZED = 'authorized'
    ADMIN = 'admin'
    
    CHOICE_ROLE = (
        (GUEST, 'гость'),
        (AUTHORIZED, 'авторизованный'),
        (ADMIN, 'админ'),
    )
    
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='e-mail',
        help_text='Впишите ваш e-mail'
    )
    
    role = models.CharField(
        max_length=20,
        default='anon',
        choices=CHOICE_ROLE,
        verbose_name='Статус пользователя в системе'
    )
    
    @property
    def is_admin(self):
        '''Проверка на администратора'''
        return self.role == self.ADMIN or self.is_superuser
    
    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self) -> str:
        return self.username

