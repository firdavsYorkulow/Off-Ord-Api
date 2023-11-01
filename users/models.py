from django.db import models
import uuid
import random
from datetime import datetime, timedelta
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from shared.models import BaseModel
from rest_framework_simplejwt.tokens import RefreshToken

# Create your models here.

NEW, CODE_VERIFIED, DONE, PHOTO_DONE, LOCATION_DONE = ('new', 'code_verified', 'done', 'photo_done', 'location_done')

(TASHKENT, ANDIJAN, BUKHARA, FERGANA, JIZZAKH, NAMANGAN, NAVOIY, QASHQADARYO, SAMARQAND, SIRDARYO, SURXONDARYO, XORAZM,
 KARAKALPAKSTAN) = ("tashkent", "andijon", "bukhara", "fergana", "jizzakh", "namangan", "navoiy", "qashqadaryo",
                    "samarqand", "sirdaryo", "surxondaryo", "xorazm", "karakalpakstan")


class User(AbstractUser, BaseModel):
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE),
        (LOCATION_DONE, LOCATION_DONE)
    )
    CITIES = (
        (TASHKENT, TASHKENT),
        (ANDIJAN, ANDIJAN),
        (BUKHARA, BUKHARA),
        (FERGANA, FERGANA),
        (JIZZAKH, JIZZAKH),
        (NAMANGAN, NAMANGAN),
        (NAVOIY, NAVOIY),
        (QASHQADARYO, QASHQADARYO),
        (SAMARQAND, SAMARQAND),
        (SIRDARYO, SIRDARYO),
        (SURXONDARYO, SURXONDARYO),
        (XORAZM, XORAZM),
        (KARAKALPAKSTAN, KARAKALPAKSTAN)
    )

    auth_status = models.CharField(max_length=32, choices=AUTH_STATUS, default=NEW)
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    work_type = models.CharField(max_length=60, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to="user_photos/", null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    location = models.CharField(max_length=50, choices=CITIES, default=TASHKENT)

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self):
        code = ''.join([str(random.randint(0, 10000) % 10) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            code=code
        )
        return code

    def check_username(self):
        if not self.username:
            temp_username = f'instagram-{uuid.uuid4().__str__().split("-")[-1]}'
            while User.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.randint(0, 9)}"
            self.username = temp_username

    def check_pass(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}"
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith("pbkdf2_sha256"):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }

    def save(self, *args, **kwargs):
        # if not self.pk:
        self.clean()
        super(User, self).save(*args, **kwargs)

    def clean(self):
        self.check_username()
        self.check_pass()
        self.hashing_password()


PHONE_EXPIRE = 2


class UserConfirmation(BaseModel):
    code = models.CharField(max_length=4)
    user = models.ForeignKey('users.User', models.CASCADE, related_name="verify_codes")
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation, self).save(*args, **kwargs)
