from django.urls import path
from .views import CreateUserApiView, VerifyApiView, GetNewVerification, ChangeUserInformationView, \
    ChangeUserPhotoView, LoginView, LoginRefreshView, LogoutView, ForgotPasswordView, ResetPasswordView


urlpatterns = [
    path('login/', LoginView.as_view()),
    path('login/refresh/', LoginRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('signup/', CreateUserApiView.as_view()),
    path('verify/', VerifyApiView.as_view()),
    path('new-verify/', GetNewVerification.as_view()),
    path('change-user/', ChangeUserInformationView.as_view()),
    path('change-user-photo/', ChangeUserPhotoView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view())
]