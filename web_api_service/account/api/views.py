from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.views import ObtainAuthToken

from account.api.serializers import RegistrationSerializer
from django.utils.translation import gettext_lazy as _


'''
{
"email": "eee@eee.ru",
"first_name": "Kolya",
"last_name": "Dima",
"password": "Admin2022#",
"password2": "Admin2022#"
}

'''


@api_view(['POST', ])
def api_registration_view(request):

    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            print(user)
            data['response'] = _('successfully registered a new user.')
            data['email'] = user.email
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            token = Token.objects.get(user=user).key
            data['token'] = token
        else:
            data = serializer.errors
        return Response(data)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

