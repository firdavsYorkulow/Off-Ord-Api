from .models import User, UserConfirmation, NEW, CODE_VERIFIED, DONE, PHOTO_DONE
from rest_framework import exceptions
from django.core.validators import FileExtensionValidator
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.generics import get_object_or_404
from shared.utility import check_email_or_phone, send_email, send_phone_code, check_user_type
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken


class SignupSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignupSerializer, self).__init__(*args, **kwargs)
        self.fields['phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "id",
            'auth_status',
        )
        extra_kwargs = {
            'auth_status': {'read_only': True, 'required': False}
        }

    def create(self, validated_data):
        user = super(SignupSerializer, self).create(validated_data)
        code = user.create_verify_code()
        send_email(user.phone_number, code)
        # send_phone_code(user.phone_number, code)
        print(code)
        user.save()
        return user

    def validate(self, data):
        super(SignupSerializer, self).validate(data)
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == "phone":
            data = {
                "phone_number": user_input,
            }
        else:
            data = {
                "success": False,
                "message": "You must send email or phone number"
            }
            raise ValidationError(data)
        return data

    def validate_telephone_number(self, value):
        value = value.lower()
        if value and User.objects.filter(phone_number=value).exists():
            data = {
                "success": False,
                "message": "Ushbu telefon raqam allaqachon baza mavjud"
            }
            raise ValidationError(data)
        return value

    def to_representation(self, instance):
        data = super(SignupSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data


class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    bio = serializers.CharField(write_only=True, required=True),
    work_type = serializers.CharField(write_only=True, required=True)
    location = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get("password", None)
        confirm_password = data.get("confirm_password", None)

        if password != confirm_password:
            raise ValidationError({
                "success": False,
                "message": "Sizning parolingiz va tasdiqlash parolingiz bir biriga mos emas"
            })

        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Username uzunligi 5 va 30 oraligida bo'lishi kerak"
                }
            )
        if username.isdigit():
            raise ValidationError(
                {
                    "success": False,
                    "message": "Username faqat sonlardan iborat bo'lmasligi talab etiladi"
                }
            )
        return username

    def validate_first_name(self, first_name):
        if len(first_name) < 5 or len(first_name) > 30:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Ismingiz uzunligi 5 va 30 oralig'ida bo'lishi kerak"
                }
            )

        if first_name.isdigit():
            raise ValidationError(
                {
                    "success": False,
                    "message": "Ismingiz faqat raqamlardan tashkil topmasligi kerak."
                }
            )
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) < 5 or len(last_name) > 30:
            raise ValidationError({
                "success": False,
                "message": "Familiyangiz uzunligi 5 va 30 oraligida bo'lishi kerak"
            })

        if last_name.isdigit():
            raise ValidationError(
                {
                    "success": False,
                    "message": "Familiyangiz faqat raqamlardan tashkil topmasligi kerak ."
                }
            )
        return last_name

    def validate_work_type(self, work_type):
        if len(work_type) > 40 or len(work_type) < 4:
            raise ValidationError({
                "success": False,
                "message": "Kasbingiz uzunligi 4 va 40 oraligida bo'lishis kerak."
            })
        if work_type.isdigit():
            raise ValidationError({
                "success": False,
                "message": "Kasbingiz faqat raqamlardan tashkil topmasligi kerak."
            })
        return work_type

    def validate_location(self, location):
        if len(location) > 40 or len(location) < 5:
            raise ValidationError({
                "success": False,
                "message": "Joylashuvingiz uzungligi 5 va 40 oraligida bo'lishi kerak"
            })
        if location.isdigit():
            raise ValidationError({
                "success": False,
                "message": "Joylashuvingiz faqat raqamdan tashkil topmasligi kerak."
            })
        return location

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.bio = validated_data.get("bio", instance.bio)
        instance.work_type = validated_data.get("work_type", instance.work_type)
        instance.location = validated_data.get("location", instance.location)
        instance.password = validated_data.get("password", instance.password)
        instance.username = validated_data.get("username", instance.username)

        if validated_data.get("password"):
            instance.set_password(validated_data.get("password"))

        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status == DONE

        instance.save()
        return instance


class ChangePhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField(validators=[FileExtensionValidator(allowed_extensions=[
        "jpg", "jpeg", "png"
    ])])

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
            instance.auth_status = PHOTO_DONE
            instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)

    def auth_validate(self, data):
        user_input = data.get('userinput')
        if check_user_type(user_input) == "username":
            username = user_input
        elif check_user_type(user_input) == "phone":
            user = self.get_user(phone_number=user_input)
            username = user.username
        else:
            data = {
                "success": False,
                "message": "Siz username yoki telefon raqamingizni kiritishingiz kerak"
            }
            raise ValidationError(data)
        authentication_kwargs = {
            self.username_field: username,
            'password': data['password']
        }
        current_user = User.objects.filter(username__iexact=username).first()  # None
        if current_user is not None and current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Siz hali to'liq ro'yxatdan o'tmagansiz."
                }
            )
        user = authenticate(**authentication_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Kechirasiz, login yoki parolingiz xato kiritildi. Iltimos tekshirib qaytadan kiriting."
                }
            )

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, PHOTO_DONE]:
            raise PermissionDenied("Kechirasiz siz login qila olmaysiz. Ruxsatingiz yo'q!")
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        data['full_name'] = self.user.full_name
        return data

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError(
                {
                    "success": False,
                    "message": "Aktiv akkaunt topilmadi"
                }
            )
        return users.first()


class LoginRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token_instance = AccessToken(data['access'])
        user_id = access_token_instance['user_id']
        user = get_object_or_404(User, id=user_id)
        update_last_login(None, user)
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        email_or_phone = attrs.get('email_or_phone')
        if email_or_phone is None:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Telefon raqam kiritilishi shart."
                }
            )
        user = User.objects.filter(Q(phone_number=email_or_phone))
        if not user.exists():
            raise NotFound(detail="Foydalanuvchi topilmadi!")
        attrs['user'] = user.first()
        return attrs


class ResetPasswordSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=8, required=True, write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "password",
            "confirm_password"
        )

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get("confirm_password")
        if password != confirm_password:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Parollaringiz qiymatlari bir-biriga mos emas."
                }
            )
        if password:
            validate_password(password)
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop("password")
        instance.set_password(password)
        return super(ResetPasswordSerializer, self).update(instance, validated_data)

    # def validate(self, attrs):


