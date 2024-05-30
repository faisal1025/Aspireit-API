from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import FileModel

# User = get_user_model()
class FileSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')
    creator_id = serializers.ReadOnlyField(source='creator.id')
    file = serializers.FileField(required=False)

    class Meta:
        model = FileModel
        fields = ['id', 'creator', 'creator_id', 'description', 'file']

    def save(self, user):
        item = FileModel(creator=user, 
                         description=self.validated_data['description'], 
                         file=self.validated_data['file'])
        item.save()
        return item
    
class UserSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'date_joined', 'files', 'id']

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input-type' : 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'Error': "password does not match"})
        
        if User.objects.filter(email = self.validated_data['email']).exists():
            raise serializers.ValidationError({'Error': 'Email already exists'})
        
        validated_data = self.validated_data
        account = User(username = validated_data['username'],
                        email = validated_data['email'], 
                        first_name = validated_data['first_name'], 
                        last_name = validated_data['last_name'])
        account.set_password(password)

        account.save()
        return account

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class UserEditSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()





