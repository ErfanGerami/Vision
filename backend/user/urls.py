from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path('register/', TeamRegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('staff/', GetStaffView.as_view(), name='get_staff'),
    path('team/', GetTeamView.as_view(), name='get_team'),
    path('captcha/', GetCaptchaView.as_view(), name='captcha'),
    path('recaptcha-site-key/', GetRecaptchaSiteKey.as_view(),
         name='recaptcha_site_key'),
    path('registration-test/', registration_test,
         name='registration_test'),  # Add this line
]
