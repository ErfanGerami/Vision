from .models import *
from rest_framework import serializers


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ['id', 'name', 'url', 'type']


class ContentSerializer(serializers.ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = '__all__'
