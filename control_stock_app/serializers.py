from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.utils import model_meta

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'