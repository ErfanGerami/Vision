from .models import *
from rest_framework import serializers

ORDER = ['image', 'video', 'link']


def compare(content: Link):

    if (content.type in ORDER):
        return ORDER.index(content.type)
    else:
        return len(ORDER)


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ['id', 'name', 'url', 'type']


class ContentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'title']


class ContentSerializer(serializers.ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['links'] = sorted(
            representation['links'], key=compare)
        return representation

    class Meta:
        model = Content
        fields = '__all__'
