from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
import jwt
from datetime import datetime, timedelta

class UserManager(BaseUserManager):
    def create_user(self, emp_name, emp_number, role, password):
        """Create an employee"""
        if emp_name is None:
            raise TypeError("Employees must have a name")

        if emp_number is None or len(emp_number) != 4:
            raise TypeError("Invalid Employee Number")

        user = self.model(emp_name=emp_name, emp_number=emp_number, role=role)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, emp_name, emp_number, role, password):
        if role is None or role != "Admin":
            raise TypeError("Role must be set to Admin")
            
        user = self.create_user(emp_name, emp_number, "Admin", password)
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    emp_number = models.CharField(db_index=True, max_length=4, unique=True) 
    emp_name = models.CharField(db_index=True, max_length=255)
    role = models.CharField(max_length=255)

    USERNAME_FIELD = 'emp_number'
    REQUIRED_FIELDS = ['emp_name', 'role']

    objects = UserManager()

    def __str__(self):
        return self.emp_number + " " + self.emp_name + " " + self.role
    
    def get_full_name(self):
        return self.emp_name
    
    def get_short_name(self):
        return self.emp_name

    def _generate_jwt(self):
        # set expiry date after 30 days 
        dt = datetime.now() + timedelta(days=30)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt.utcfromtimestamp(dt.timestamp())  
        }, settings.SECRET_KEY, algorithm="HS256")

        return token


    @property
    def token(self):
        return self._generate_jwt()



