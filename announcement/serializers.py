from rest_framework import serializers
from .models import Announcement, User

class UsernameSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'username')

class AnnouncementSerializer (serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'context', 'created_user', 'created_time', 'last_modified', 'visible', 'important']

class AnnouncementInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'created_time', 'last_modified', 'visible', 'important']

class AnnouncementCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['visible', 'important']