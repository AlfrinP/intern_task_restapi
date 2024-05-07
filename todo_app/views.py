from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException
from .authenticate import create_access_token, create_refresh_token, decode_refresh_token
from .models import CustomUser, Task
from .serializers import CustomUserSerializer, ToDoSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser, FormParser



def Index(self):
   return HttpResponse('Server is Alive!')

class Refresh(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refreshToken')
        id = decode_refresh_token(refresh_token)
        access_token = create_access_token(id)
        return Response({
            'token': access_token
        })


class Signout(APIView):
    def get(self, _):
        response = Response()
        response.delete_cookie(key="refreshToken")
        response.data = {
            'message': "SUCCESS"
        }
        return response


class Login(APIView):
    def post(self, request):
        data = {
            'username': request.data.get('username'),
            'password': request.data.get('password'),
            'email': request.data.get('email'),
        }
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Signin(APIView):
    def post(self, request):
        data = request.data
        EoM = data.get('emailorusername')
        if EoM is None:
            raise APIException('EmailOrUsername is a mandatory field.')
        try:
            user = CustomUser.objects.get(username=EoM)
        except ObjectDoesNotExist:
            user = None
        if user is None:
            try:
                user = CustomUser.objects.get(email=EoM)
            except ObjectDoesNotExist:
                user = None
        if user is None:
            raise APIException('Invalid Credentials')

        if not user or not check_password(request.data['password'], user.password):
            raise APIException('Invalid Credentials')

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        response = Response()

        response.set_cookie(key='refreshToken',
                            value=refresh_token, httponly=True)
        response.data = {
            'access-token': access_token,
            'refresh-token': refresh_token
        }

        return response


class Todo(APIView):

    def get(self, request, pk=None):
        refresh_token = request.COOKIES.get('refreshToken')
        id = decode_refresh_token(refresh_token)

        if CustomUser.objects.filter(id=id).exists():
            if pk:
                try:
                    todo_obj = Task.objects.get(pk=pk, user=id)
                    serializer = ToDoSerializer(todo_obj)
                    return Response(serializer.data)
                except Task.DoesNotExist:
                    return Response({'message': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                items = Task.objects.filter(user=id)
                serializer = ToDoSerializer(items, many=True)
                return Response(serializer.data)
        else:
            return Response({'message': 'User is not logged in!'}, status=status.HTTP_400_BAD_REQUEST)

    @parser_classes([JSONParser, FormParser])
    def post(self, request):
        refresh_token = request.COOKIES.get('refreshToken')
        id = decode_refresh_token(refresh_token)

        if CustomUser.objects.filter(id=id).exists():
            update_data={
                "user":id,
                "title":request.POST.get('title'),
                "description":request.POST.get('description'),
                "completion_date":request.POST.get('date'),
            }
            serializer = ToDoSerializer(data=update_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'User is not logged in!'}, status=status.HTTP_400_BAD_REQUEST)



    def put(self, request, pk):
        refresh_token = request.COOKIES.get('refreshToken')
        id = decode_refresh_token(refresh_token)

        if CustomUser.objects.filter(id=id).exists():
            try:
                todo_obj = Task.objects.get(pk=pk, user=id)
            except Task.DoesNotExist:
                return Response({'message': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ToDoSerializer(instance=todo_obj, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Data Updated Successfully'})
        else:
            return Response({'message': 'User is not logged in!'}, status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, pk):
        refresh_token = request.COOKIES.get('refreshToken')
        id = decode_refresh_token(refresh_token)

        if CustomUser.objects.filter(id=id).exists():
            try:
                todo_obj = Task.objects.get(pk=pk, user=id)
            except Task.DoesNotExist:
                return Response({'message': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ToDoSerializer(instance=todo_obj, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Data Updated Successfully'})
        else:
            return Response({'message': 'User is not logged in!'}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk):
        refresh_token = request.COOKIES.get('refreshToken')
        id = decode_refresh_token(refresh_token)

        if CustomUser.objects.filter(id=id).exists():
            try:
                task = Task.objects.get(pk=pk, user=id)
                task.delete()
                return Response({'message': 'Data Deleted Successfully'})
            except Task.DoesNotExist:
                return Response({'message': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'User is not logged in!'}, status=status.HTTP_400_BAD_REQUEST)
        

