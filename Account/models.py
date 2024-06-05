from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


class User(AbstractUser):    
    username = None
    phone = models.CharField(
        unique=True,
        max_length=17,
        validators=[
            RegexValidator(
                regex=r'^998[0-9]{2}[0-9]{7}$',
                # message="Only Uzbekistan numbers are confirmed"
            )
        ]
    )
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)
    expiration_time = models.DateTimeField(null=True, blank=True)
    new_phone_temp = models.CharField(max_length=17, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'