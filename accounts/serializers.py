from rest_framework import serializers
from .models import User, Organisation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            phone=validated_data.get('phone', '')
        )
        return user

class OrganisationSerializer(serializers.ModelSerializer):
    orgId = serializers.UUIDField(source='org_id', read_only=True)

    class Meta:
        model = Organisation
        fields = ['orgId', 'name', 'description']
