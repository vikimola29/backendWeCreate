# Create your models here.
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django_rest_passwordreset.signals import reset_password_token_created

from .managers import MyUserManager


# Create your models here.


class MyUser(AbstractBaseUser):
    ADMIN = "Admin"
    CLIENT = "Client"

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (CLIENT, 'Client'),
    )
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CLIENT)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    registered_date = models.DateTimeField(default=timezone.now, blank=True, null=True)

    REQUIRED_FIELDS = ['name']
    USERNAME_FIELD = 'email'

    objects = MyUserManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        return

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    class Meta:
        ordering = ['-email']

    def __str__(self):
        return f"{self.name} - {self.company_name} - {self.email}"


class Project(models.Model):
    PENDING = 'Pending'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'

    PROJECT_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    PAID = 'Paid'
    NOT_PAID = 'Not Paid'

    PAYMENT_STATUS_CHOICES = [
        (PAID, 'Paid'),
        (NOT_PAID, 'Not Paid'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    client = models.ForeignKey(MyUser, on_delete=models.CASCADE, default="wecreate.designs.srl@hotmail.com")
    status = models.CharField(max_length=50, choices=PROJECT_STATUS_CHOICES, default=PENDING, blank=True, null=True)
    finish_due_date = models.DateField(blank=True, null=True)
    batch_price = models.IntegerField(blank=True, null=True)
    monthly_price = models.IntegerField(blank=True, null=True)
    batch_payment_due_date = models.DateField(blank=True, null=True)
    monthly_payment_due_date = models.DateField(blank=True, null=True)
    batch_payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default=NOT_PAID, blank=True,
                                            null=True)
    monthly_payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default=NOT_PAID,
                                              blank=True, null=True)
    registered_date = models.DateField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.client.email}"


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    message = models.TextField(null=False, blank=False, default="Message")

    def __str__(self):
        if self.name:
            return self.name + '\n\n ' + self.message
        else:
            return self.message


class NewsletterUser(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Newsletter(models.Model):
    EMAIL_STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Publish', 'Publish'),
    )
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    email = models.ManyToManyField(NewsletterUser)
    status = models.CharField(max_length=10, choices=EMAIL_STATUS_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
