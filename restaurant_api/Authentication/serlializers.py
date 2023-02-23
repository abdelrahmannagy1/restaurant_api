from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate

class RegisterationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=6,
        write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['emp_name', 'emp_number', 'role', 'password', 'token']
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    emp_name = serializers.CharField(max_length=255, read_only=True)
    emp_number = serializers.CharField(max_length=4)
    role = serializers.CharField(max_length=255, read_only=True)

    token = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=255, write_only=True)

    def validate(self, data):
        emp_number = data.get('emp_number', None)
        password = data.get('password', None)

        if emp_number is None:
            raise serializers.ValidationError("An employee number is required to log in")

        if password is None:
            raise serializers.ValidationError("Password is required to log in")

        user = authenticate(emp_number=emp_number, password=password)

        if user is None:
            raise serializers.ValidationError("User Invalid or Wrong Password")

        return {
            "emp_number": user.emp_number,
            "emp_name": user.emp_name,
            "role": user.role,
            "token": user.token

        }




