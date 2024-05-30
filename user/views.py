from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import RegisterSerializer, LoginSerializer, UserSerializer, UserEditSerializer, FileSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from transformers import pipeline
from .models import FileModel
from django.http import FileResponse

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your views here.
@api_view(['POST'])
def register(request):
    data = {
        'username': request.data['username'],
        'email': request.data['email'],
        'first_name': request.data['firstName'],
        'last_name': request.data['lastName'],
        'password': request.data['password'],
        'password2': request.data['confirmPassword'],
    }
    response = {}
    serializer = RegisterSerializer(data=data)
    if serializer.is_valid():
        account = serializer.save()
        print(type(account))
        response['status'] = 201
        response['message'] = f"Hi {account.first_name}, congrats your account created successfully"
        response['username'] = account.username
        response['token'] = get_tokens_for_user(account)
    else:
        response = serializer.errors
        response['status'] = 400
    return Response(response)

@api_view(['POST'])
def login(request):
    try:
        data = {
            'username': request.data['username'],
            'password': request.data['password']
        }
        response = {}
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            username = serializer.data['username']
            password = serializer.data['password']

            user = authenticate(username=username, password=password)

            if user is None: 
                response['status'] = 400
                response['message'] = 'user is not authenticated, username or password may wrong'
                response['data'] = {}
            elif user:
                userSerializer = UserSerializer(user)
                response['status'] = 200
                response['message'] = f'Hi, {userSerializer.data['first_name']}, Welcome back'
                response['username'] = userSerializer.data['username']
                response['token'] = get_tokens_for_user(user)

        else:
            response = serializer.errors

        return Response(response)
    
    except Exception as e:
        print(e)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request): 
    try:
        username = request.query_params['username']
        user = User.objects.prefetch_related('files').get(username=username)  # Query the user by username
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit(request):
    try:
        username = request.query_params['username']
        serializer = UserEditSerializer(data=request.data)
        print("user name h", username)
        response = {}

        if serializer.is_valid():
            try:
                user = User.objects.get(username=username)
                print("user: ", user)
                user.first_name=serializer.validated_data['first_name'] 
                user.last_name = serializer.validated_data['last_name'] 
                user.email = serializer.validated_data['email']
                user.save()
                response['message'] = f'hi {user.first_name} your profile updated successfully'
                response['status'] = status.HTTP_200_OK
                return Response(response)
            except User.DoesNotExist:
                response['message'] = f'hi {user.first_name} does not exist'
                response['status'] = status.HTTP_400_INTERNAL_SERVER_ERROR
                return Response(response)
            except Exception:
                response['message'] = f'hi {user.first_name} something went wrong, please try again'
                response['status'] = status.HTTP_500_INTERNAL_SERVER_ERROR
                return Response(response)


        response['message'] = f'hi {user.first_name} something went wrong, please try again'
        response['status'] = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Response(response)
    except Exception as e: 
        print(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze(request):
    try:
        text = request.data['text']
        analyzer = pipeline('sentiment-analysis') # using deffault ML model
        result = analyzer(text)
        return Response({'result': result})
    except Exception as e:
        print(e)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload(request): 
    try:
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save(request.user)
            return Response({'message': "File uploaded successfully", 'data': data.description})
        else:
            return Response({'Error': serializer.errors})
    except Exception as e:
        print(e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download(request): 
    try:
        fileId = request.query_params['id']
        file = FileModel.objects.get(id = fileId)
        filehandle = file.file.open()
        response = FileResponse(filehandle, as_attachment=True, filename=file.file.name)
        response['Content-Length'] = file.file.size
        return response
    except FileModel.DoesNotExist:
        return Response({'status': 404, 'message': "file not found"})
