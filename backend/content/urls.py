from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path("get-all-contents/", GetAllContent.as_view(), name="get_all_content"),
    path("get-content/<int:pk>/", GetContent.as_view(), name="get_content_by_id"),

]
