import threading
from django.core.mail import send_mail
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import *
from rest_framework import generics
from captcha.helpers import captcha_image_url
import requests
from django.conf import settings
import logging
import random


class EmailThread(threading.Thread):
    def __init__(self, subject, message, from_email, recipient_list):
        self.subject = subject
        self.message = message
        self.from_email = from_email
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        send_mail(self.subject, self.message,
                  self.from_email, self.recipient_list)
        print("sent")


def email(redis_conn, team):
    expiration_time = getattr(settings, 'REDIS_EXPIRATION', 300)
    verification_code = random.randint(100000, 999999)
    mail = TeamMember.objects.get(leader=True, team=team).email
    redis_conn.set(team.id, verification_code, ex=expiration_time)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'default@example.com')
    print(mail)

    EmailThread("Verification Code", f"Your verification code: {verification_code}\n It will be expired within {expiration_time/60} minutes ", from_email,
                [mail]).start()


def check_captcha(request):
    recaptcha_response = request.data.get('g-recaptcha-response')
    if not recaptcha_response:
        return False, Response({'error': 'Captcha is required'}, status=status.HTTP_400_BAD_REQUEST)

    secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
    google_url = 'https://www.google.com/recaptcha/api/siteverify'
    r = requests.post(google_url, data={
        'secret': secret_key,
        'response': recaptcha_response
    })
    result = r.json()
    if not result.get('success'):
        False, Response({'error': 'Invalid captcha'},
                        status=status.HTTP_400_BAD_REQUEST)
    return True, None
