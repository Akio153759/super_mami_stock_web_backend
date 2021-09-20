from django.shortcuts import render
from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .serializers import *
from .data_access import db_helper as _db


@api_view(['POST'])
def login(request):
    try:
        _username = request.POST['username']
        _password = request.POST['password']

        try:
            _objUser = User.objects.get(username=_username)
            if not check_password(_password, _objUser.password):
                raise User.DoesNotExist
        except User.DoesNotExist:
            return Response('Usuario y/o contraseña incorrectos', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as ex:
            return Response('Error al intentar autentificar', status=status.HTTP_400_BAD_REQUEST)

        _user_info = _db.get_data_from_procedure(connection=connection,
                                                 proc_name='sp_get_user_info')
        _response = UserSerializer(_objUser, many=False)

        return Response(_user_info, status=status.HTTP_200_OK)
    except:
        return Response('Server Error',status=status.HTTP_500_INTERNAL_SERVER_ERROR)
