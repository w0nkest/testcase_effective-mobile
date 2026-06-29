from rest_framework import serializers
from .models import UserProfile, UserRole, Roles
from bcrypt import hashpw, gensalt

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'name', 'surname', 'email', 'is_active')

class UserRegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    surname = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255, write_only=True)
    is_active = serializers.BooleanField(default=True)

    def create(self, validated_data):
        validated_data['password'] = hashpw(validated_data['password'].encode('utf-8'), gensalt()).decode('utf-8')
        user = UserProfile.objects.create(**validated_data)

        UserRole.objects.create(user=user, role=Roles.objects.get(name='user'))

        return user

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.email = validated_data.get('email', instance.email)
        instance.password = validated_data.get('password', instance.password)
        instance.is_active = validated_data.get('is_active', instance.is_active)

        instance.save()

        return instance