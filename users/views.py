from django.utils.datetime_safe import datetime
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from .models import User
from .serializers import LoginSerializer, SignupSerializer, ChangeUserInformation, ChangePhotoSerializer, \
    LoginRefreshSerializer, LogoutSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from shared.utility import send_email, check_email_or_phone
from .models import NEW, CODE_VERIFIED, DONE, User
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ObjectDoesNotExist


class CreateUserApiView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = SignupSerializer


class VerifyApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        code = request.data.get('code')

        self.check_verify(user, code)
        return Response(
            data={
                "success": True,
                "auth_status": user.auth_status,
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token']
            }
        )

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                "success": False,
                "message": "Tasdiqlash kodingiz xato yoki eskirgan"
            }
            raise ValidationError(data)
        else:
            verifies.update(is_confirmed=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()
        return True


class GetNewVerification(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        self.check_verification(user)
        # try:
        code = user.create_verify_code()
        send_email(user.phone_number, code)
        # except:
        #     data = {
        #         "message": "Email yoki telefon raqamingiz xato"
        #     }
        #     raise ValidationError(data)

        return Response(
            data={
                "success": True,
                "message": "Tasdiqlash kodingiz qaytadan yuborildi."
            }
        )

    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                "message": "Kodingiz hali ishlatish uchun yaroqli, iltimos kutib turing"
            }
            raise ValidationError(data)


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeUserInformation
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        data = {
            "success": True,
            "message": "Malumotlaringiz muvaffaqiytali yangilandi.",
            "auth_status": self.request.user.auth_status,
        }
        return Response(data, status=200)

    def partial_update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).partial_update(request, *args, **kwargs)
        data = {
            "success": True,
            "message": "Malumotlaringiz muvaffaqiyatli yangilandi.",
            "auth_status": self.request.user.auth_status,
        }
        return Response(
            data=data,
            status=200
        )


class ChangeUserPhotoView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        serializer = ChangePhotoSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            serializer.update(user, serializer.validated_data)
            return Response(
                {
                    "success": True,
                    "message": "Rasm muvaffaqiyatli almashtirildi."
                },
                status=200
            )
        return Response(
            serializer.errors, status=400
        )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRefreshView(TokenRefreshView):
    serializer_class = LoginRefreshSerializer


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        try:
            refresh_token = self.request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            data = {
                "success": True,
                "message": "You are logget out"
            }
            return Response(
                data=data,
                status=205
            )
        except TokenError:
            return (Response(status=404))


class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        email_or_phone = serializer.validated_data.get('email_or_phone')
        user = serializer.validated_data.get('user')
        if check_email_or_phone(email_or_phone) == "phone":
            code = user.create_verify_code()
            send_email(email_or_phone, code)
        return Response(
            {
                "success": True,
                "message": "Tasdiqlash kodi muvaffaqiyatli yuborildi!",
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token'],
                "user_status": user.auth_status,
            }, status=200
        )




class ResetPasswordView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResetPasswordSerializer
    http_method_names = ['put', 'patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super(ResetPasswordView, self).update(request, *args, **kwargs)
        try:
            user = User.objects.get(id=response.data.get('id'))
        except ObjectDoesNotExist as e:
            raise NotFound(detail="Foydalanuvchi topilmadi")
        return Response(
            {
                "success": True,
                "message": "Parolingiz muvaffaqiyatli o'zgartirildi.",
                "access": user.token()['access'],
                "refresh": user.token()['refresh_token']
            }
        )
