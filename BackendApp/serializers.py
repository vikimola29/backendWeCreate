from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Message, NewsletterUser, Newsletter, MyUser, Project


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class NewsletterUserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterUser
        fields = '__all__'


class NewsletterCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = '__all__'


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):

        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }
        user = get_user_model().objects.filter(email=credentials['email']).first()
        if user and user.check_password(credentials['password']):
            return super().validate(attrs)
        else:
            raise serializers.ValidationError('Invalid credentials')
