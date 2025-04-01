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
from django_redis import get_redis_connection
import random
from .permissions import IsVerifiedTeam
from .helpers import *
import json
from django.conf import settings

redis_conn = get_redis_connection("default")


class TeamRegisterView(APIView):
    def post(self, request):
        if (not settings.REGISTER_PERMITED):
            return Response({'error': 'Registration is closed'}, status=status.HTTP_400_BAD_REQUEST)
        result, res = check_captcha(request=request)
        if (not result):
            return res

        team_name = request.data.get('username')
        team_password = request.data.get('password')

        if not team_name or not team_password:
            return Response({'error': 'username and password is required'}, status=status.HTTP_400_BAD_REQUEST)
        if (Team.objects.filter(username=team_name).exists()):
            return Response({'error': 'Team with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user_model = get_user_model()
        team = user_model.objects.create_user(
            username=team_name, password=team_password
        )
        refresh = RefreshToken.for_user(team)

        payment = request.data.get("payment")
        if not payment or payment == '':
            team.delete()
            return Response({'error': 'team payment number is requiered'}, status=status.HTTP_400_BAD_REQUEST)
        if (Team.objects.filter(payment_number=payment).exists()):
            team.delete()
            return Response({'error': 'cant register a payment for two registers'}, status=status.HTTP_400_BAD_REQUEST)
        setattr(team, "payment_number", payment)
        team.save()
        members_data = request.data.get('members', '[]')

        if not members_data or len(members_data) != 3:
            team.delete()
            return Response({'error': 'Exactly 3 members are required'}, status=status.HTTP_400_BAD_REQUEST)

        for member_index in range(len(members_data)):

            member = members_data[member_index]
            # team.delete works because members will cascade
            if (not member.get('first_name') or not member.get('stdnumber') or not member.get('last_name') or not member.get('email') or not member.get('phone_number') or not member.get('major') or not member.get('year') or not member.get('university')):
                team.delete()
                return Response({'error': 'All member fields are required'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                year = int(member.get('year'))
            except:
                team.delete()
                return Response({'error': 'year must be integer'}, status=status.HTTP_400_BAD_REQUEST)
            if (year > 1404 or year < 1000):
                team.delete()
                return Response({'error': 'Invalid year'}, status=status.HTTP_400_BAD_REQUEST)
            if (TeamMember.objects.filter(email=member.get('email')).exists()):
                team.delete()
                return Response({'error': f"Member with email {member.get('email')} already exists"}, status=status.HTTP_400_BAD_REQUEST)
            leader = False
            if (member_index == 0):
                leader = True
            TeamMember.objects.create(
                team=team,
                first_name=member.get('first_name', ''),
                last_name=member.get('last_name', ''),
                email=member.get('email', ''),
                phone_number=member.get('phone_number', ''),
                student_number=member.get('stdnumber', ''),
                leader=leader,
                major=member.get('major', ''),
                year=int(member.get('year', '')),
                university=member.get('university', '')
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


class GetTeamView(generics.RetrieveAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]  # Update this line

    def get_object(self):
        return self.request.user


class GetRecaptchaSiteKey(APIView):
    def get(self, request):
        site_key = settings.RECAPTCHA_SITE_KEY
        return Response({'site_key': site_key})


class SendEmail(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        team = self.request.user
        if (team.verification_completed):
            return Response({'error': 'team already verified'}, status=status.HTTP_400_BAD_REQUEST)
        if (redis_conn.get(team.id)):
            expiration_time = getattr(settings, 'REDIS_EXPIRATION', 300)
            return Response({'error': f'verification code have been sent to you recently wait for {expiration_time/60} minutes and try again'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            email(redis_conn, team)
            return Response({'message': 'Verification code sent to your email'}, status=status.HTTP_200_OK)


class VarifyEmail(APIView):
    permission_classes = {IsAuthenticated}

    def post(self, request):

        if (not request.data.get('verification_code')):
            return Response({'error': 'Verification code is required'}, status=status.HTTP_400_BAD_REQUEST)

        verification_code = redis_conn.get(self.request.user.id)
        if verification_code:
            verification_code = int(verification_code)
        else:
            return Response({'error': 'Verification code not found or expired'}, status=status.HTTP_404_NOT_FOUND)
        if (verification_code == int(request.data.get('verification_code'))):
            team = self.request.user

            setattr(team, "verification_completed", True)
            team.save()

            print(team)
            return Response({'message': 'Verified'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Verification code doesnt match'}, status=status.HTTP_404_NOT_FOUND)


def registration_test(request):
    return render(request, 'test.html')
