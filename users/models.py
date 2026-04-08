# ----------------------------------------------------------------------
# Merhaba! Bunu inceleyen kişiye selamlar, ben Yakup :)
# Users model: Öğretmen/öğrenci rollerine sahip özel kullanıcı modeli
# ----------------------------------------------------------------------

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'Öğretmen'),
        ('student', 'Öğrenci'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student', verbose_name='Rol')
    bio = models.TextField(blank=True, verbose_name='Hakkında')

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
