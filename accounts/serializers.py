from rest_framework import serializers
from .models import User

class PublicUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(read_only=False)
    username = serializers.CharField(read_only=False)
    user_icon = serializers.URLField(read_only=False)
    user_bio = serializers.CharField(read_only=False)
    address = serializers.JSONField(read_only=False)
    
class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=False)
    email = serializers.EmailField()
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)
    user_icon = serializers.URLField(required=False)
    user_bio = serializers.CharField(required=False)
    birthday = serializers.DateField(required=False)
    address = serializers.JSONField(required=False)
    user_chat_id = serializers.UUIDField(read_only=True)
    is_superuser = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ('id',
                  'first_name',
                  'email',
                  'username',
                  'password',
                  'user_icon',
                  'user_bio',
                  'birthday',
                  'address',
                  'user_chat_id',
                  'is_superuser',
                  'is_staff',
                  'is_active',
                  'date_joined',
                  'last_login')


class ChangePasswordSerializer(serializers.Serializer):
    # model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RecoveryPasswordSerializer(serializers.Serializer):
    # model = User
    email = serializers.EmailField()
    username = serializers.CharField(required=False)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class NotificationSerializer(serializers.Serializer):
    updates = serializers.JSONField(required=False)