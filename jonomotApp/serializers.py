from rest_framework import serializers
from .models import *


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'phone_number', 'profile_picture',
            'gender', 'followers', 'email','points','premium_user'
        ]

class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'phone_number', 'password', 'profile_picture', 'gender', 'email')

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            profile_picture=validated_data.get('profile_picture'),
            gender=validated_data.get('gender'),
            email=validated_data.get('email')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = '__all__'
        
class logoSerializer(serializers.ModelSerializer):
    class Meta:
        model = logo
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


# ----------------------------------------------------------------------------
class OptionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionChoice
        fields = '__all__'

class PollViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollView
        fields = '__all__'


class AllDataSerializer(serializers.ModelSerializer):
    user_details = CustomUserSerializer(source='user', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    option_choices = OptionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = AllData
        fields = ['id',
            'media1', 'media2', 'media3', 'media4',
            'text', 'option1', 'option2', 'option3', 'option4',
            'notice', 'user', 'user_details', 'created_at', 'post_type', 'is_comments','is_poll','category', 'category_details','reactions', 'comments','option_choices','Share_count'
        ]




