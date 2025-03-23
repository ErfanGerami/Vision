from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import TeamMember
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TeamRegisterView(APIView):
    def post(self, request):
        recaptcha_response = request.data.get('g-recaptcha-response')
        if not recaptcha_response:
            return Response({'error': 'Captcha is required'}, status=status.HTTP_400_BAD_REQUEST)

        secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
        google_url = 'https://www.google.com/recaptcha/api/siteverify'
        r = requests.post(google_url, data={
            'secret': secret_key,
            'response': recaptcha_response
        })
        result = r.json()
        if not result.get('success'):
            return Response({'error': 'Invalid captcha'}, status=status.HTTP_400_BAD_REQUEST)

        team_name = request.data.get('username')
        team_password = request.data.get('password')

        if not team_name or not team_password:
            return Response({'error': 'username and password is required'}, status=status.HTTP_400_BAD_REQUEST)
        if (Team.objects.filter(username=team_name).exists()):
            return Response({'error': 'Team with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user_model = get_user_model()
        team = user_model.objects.create_user(
            username=team_name, password=team_password)
        refresh = RefreshToken.for_user(team)

        members_data = request.data.get('members', [])
        if len(members_data) != 3:
            return Response({'error': 'Exactly 3 members are required'}, status=status.HTTP_400_BAD_REQUEST)

        for member in members_data:
            # team.delete works because members will cascade
            if (not member.get('first_name') or not member.get('last_name') or not member.get('email') or not member.get('phone_number')):
                team.delete()
                return Response({'error': 'All member fields are required'}, status=status.HTTP_400_BAD_REQUEST)
            if (TeamMember.objects.filter(email=member.get('email')).exists()):
                team.delete()
                return Response({'error': f"Member with email {member.get('email')} already exists"}, status=status.HTTP_400_BAD_REQUEST)
            TeamMember.objects.create(
                team=team,
                first_name=member.get('first_name', ''),
                last_name=member.get('last_name', ''),
                email=member.get('email', ''),
                phone_number=member.get('phone_number', ''),
            )

        return Response({
            'team': team_name,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)


class GetCaptchaView(APIView):
    def get(self, request):
        new_captcha = CaptchaStore.generate_key()
        key = new_captcha.hashkey
        image_url = captcha_image_url(key)
        return Response({'captcha_key': key, 'captcha_image_url': image_url})


class GetStaffView(generics.ListAPIView):
    serializer_class = StaffSerializer
    queryset = StaffTeam.objects.all()


class GetTeamView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return [self.request.user]


class GetRecaptchaSiteKey(APIView):
    def get(self, request):
        site_key = settings.RECAPTCHA_SITE_KEY
        logger.info(f"Providing site key: {site_key}")
        return Response({'site_key': site_key})


def registration_test(request):
    return render(request, 'test.html')
