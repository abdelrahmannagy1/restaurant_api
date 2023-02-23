from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import UserJSONRenderer
from .serlializers import RegisterationSerializer
from .serlializers import LoginSerializer

from rest_framework import exceptions

class RegisterationAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        if not request.user.role == 'Admin': 
            raise exceptions.NotAuthenticated("Not an admin User")

        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user',{})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)