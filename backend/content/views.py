from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
import requests
from django.conf import settings
import logging
from django_redis import get_redis_connection
import random
from user.permissions import IsVerifiedTeam
import json
