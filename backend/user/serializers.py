from rest_framework import serializers
from .models import *


class StaffMemberSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            path = request.build_absolute_uri(obj.image.url).repl
            path.replace('http://', 'https://')
            return path
        return None

    class Meta:
        model = StaffMember
        exclude = ['staff_team']


class StaffSerializer(serializers.ModelSerializer):
    staff = serializers.SerializerMethodField()

    def get_staff(self, obj):
        return StaffMemberSerializer(obj.members.all(), many=True, context=self.context).data

    class Meta:
        model = StaffTeam
        fields = '__all__'


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['first_name', 'last_name', 'email', 'phone_number']


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'username', 'members',
                  'verification_completed', 'register_completed']
