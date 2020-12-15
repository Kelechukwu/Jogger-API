from rest_framework import serializers

from .models import User, Jog


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User table."""

    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active']

class SignUpSerializer(serializers.ModelSerializer):
    """Serializer for User Registeration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        
    )
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'password']


class JogSerializer(serializers.ModelSerializer):
    """Serializer for Jog table."""

    user = UserSerializer

    class Meta:
        model = Jog
        fields = ['id', 'date', 'distance',
                  'time', 'location', 'user', 'weather']
