from .models import *
from rest_framework import serializers


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ['id', 'name', 'url', 'type']


class ContentSerializer(serializers.ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['links'] = sorted(representation['links'], key=lambda x: x['type'])
        return representation
    class Meta:
        model = Content
        fields = '__all__'
