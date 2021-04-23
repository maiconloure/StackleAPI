from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.mail import send_mail
from django.conf import settings
from django.core import validators
from django.contrib.auth import get_user_model
import uuid
import re
from django.utils.translation import ugettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
                raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class Notification(models.Model):
    updates = models.JSONField(blank=True, null=True)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True, 
    validators=[ validators.RegexValidator(re.compile('^[\w.@+-]+$'), _('Enter a valid username.'), _('invalid'))], blank=True, null=True)
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    user_icon = models.URLField(max_length=255, blank=True, null=True)
    user_bio = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    user_chat_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    following = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followers')
    friends = models.ManyToManyField('User', symmetrical=True)
    address = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    online = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    notifications = models.ForeignKey(Notification, related_name='notifications_id', on_delete=models.CASCADE, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')

    def __str__(self):
        return self.username

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_followers(self):
        # return "\n".join([user.username for user in self.following.all()])
        return [user.username for user in self.following.all()]

    def get_friends(self):
        # return "\n".join([friend.username for friend in self.friends.all()])
        return [friend.username for friend in self.friends.all()]
    


class Friend_Request(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)