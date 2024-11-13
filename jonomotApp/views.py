from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import *
import random
import string
from django.db.models import F
from django.core.mail import send_mail
from django.conf import settings
import uuid
import json
from django.http import JsonResponse

from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

CustomUser = get_user_model()


def generate_random_username():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))



@extend_schema(request=CustomUserRegistrationSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration(request):
    if request.method == 'POST':
        serializer = CustomUserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            auth_token = str(uuid.uuid4())
            subject = 'Account Verification Link'
            message = f'hi click the link to create your account http://api.jonomot.live/account/verify/{user.auth_token}'
            email_from = 'noreply@jonomot.live'
            recipient = [user.email]

            try:
                send_mail(subject, message, email_from, recipient)
                return Response({'message': 'User registered successfully. Please check your email inbox or spam for the account verification link.'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'message': f'Failed to send verification email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# def verify_email(request, token):
#     try:
#         user = CustomUser.objects.get(auth_token=token)
#         if user.is_verified:
#             return redirect('https://jonomot.live')
#         else:
#             user.is_verified = True
#             user.save()
#             return redirect('https://jonomot.live')  
#     except CustomUser.DoesNotExist:
#         return Response({'error': 'Invalid verification token'}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['GET'])
# def verify_email(request, token):
#     try:
#         user = CustomUser.objects.get(auth_token=token)
        
#         if user.is_verified:
#             return Response({
#                 'message': 'User is already verified.',
#                 'redirect_url': 'https://jonomot.live'  # URL to redirect to the login page
#             }, status=status.HTTP_200_OK)
        
#         user.is_verified = True
#         user.save()
#         return Response({
#             'message': 'Verification successful!',
#             'redirect_url': 'https://jonomot.live'  # URL to redirect to the login page
#         }, status=status.HTTP_200_OK)
    
#     except CustomUser.DoesNotExist:
#         return Response({'error': 'Invalid verification token'}, status=status.HTTP_404_NOT_FOUND)

from django.http import HttpResponse
from rest_framework import status

@api_view(['GET'])
def verify_email(request, token):
    try:
        user = CustomUser.objects.get(auth_token=token)
        
        if user.is_verified:
            return HttpResponse(
                content="User is already verified. Please go to the login page: <a href='https://jonomot.live'>https://jonomot.live</a>",
                status=status.HTTP_200_OK
            )
        
        user.is_verified = True
        user.save()
        return HttpResponse(
            content="Verification successful! Please go to the login page: <a href='https://jonomot.live'>https://jonomot.live</a>",
            status=status.HTTP_200_OK
        )
    
    except CustomUser.DoesNotExist:
        return HttpResponse(
            content="Invalid verification token. Please go to the login page: <a href='https://jonomot.live'>https://jonomot.live</a>",
            status=status.HTTP_404_NOT_FOUND
        )


    

@extend_schema(request=CustomUserLoginSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    if request.method == 'POST':
        serializer = CustomUserLoginSerializer(data=request.data)
        if serializer.is_valid():
            phone_number_or_email = serializer.validated_data.get('phone_number')
            password = serializer.validated_data.get('password')

            if '@' in phone_number_or_email:
                user = CustomUser.objects.filter(email=phone_number_or_email).first()
            else:
                user = CustomUser.objects.filter(phone_number=phone_number_or_email).first()

            if user and user.check_password(password):
                if user.is_verified:  
                    refresh = RefreshToken.for_user(user)
                    access_token_payload = {
                        'user_id': user.id,
                        'username': user.username,
                    }
                    refresh.payload.update(access_token_payload)
                    user_serializer = CustomUserSerializer(user)

                    return Response({
                        'user': user_serializer.data,
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Your account is not verified. Please check your email for the verification link.'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CustomUserSerializer)
@api_view(['PUT'])
def update_profile(request):
    pk = request.data.get('pk')
    if pk is None:
        return Response({"error": "Primary key (pk) is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(pk=pk)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        parsers = (MultiPartParser, FormParser)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@extend_schema(request=ReactionSerializer)
@api_view(['POST'])
def create_reaction(request):
    user_id = request.data.get('user')
    post_id = request.data.get('post')
    reaction_type = request.data.get('reaction_type')
    ip_address = request.META.get('REMOTE_ADDR')

    if not (post_id and reaction_type):
        return Response({'detail': 'post ID and reaction type are required.'}, status=status.HTTP_400_BAD_REQUEST)

    all_data_instance = AllData.objects.get(pk=post_id)

    if reaction_type not in dict(Reaction.REACTION_TYPES).keys():
        return Response({'detail': 'Invalid reaction type.'}, status=status.HTTP_400_BAD_REQUEST)

    if user_id:
        user = CustomUser.objects.get(id=user_id)
        existing_reaction = Reaction.objects.filter(user=user, post=all_data_instance).first()
        if existing_reaction:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
            return Response({'detail': 'Your reaction has been updated.'}, status=status.HTTP_200_OK)
        else:
            reaction = Reaction.objects.create(user=user, post=all_data_instance, reaction_type=reaction_type)
            CustomUser.objects.filter(pk=user.pk).update(points=F('points') + 5)
    else:
        existing_reaction = Reaction.objects.filter(post=all_data_instance, ip_address=ip_address).first()

        if existing_reaction:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
            return JsonResponse({'detail': 'Your reaction has been updated based on IP address.'}, status=status.HTTP_200_OK)
        else:
            reaction = Reaction.objects.create(post=all_data_instance, reaction_type=reaction_type, ip_address=ip_address)
            return JsonResponse({'detail': 'Reaction created based on IP address.'}, status=status.HTTP_201_CREATED)


    serializer = ReactionSerializer(reaction)
    return Response(serializer.data, status=status.HTTP_201_CREATED)





@extend_schema(request=CommentSerializer)
@api_view(['POST'])

def create_comment(request):
    user_id = request.data.get('user')
    post_id = request.data.get('post')
    text = request.data.get('text')
    ip_address = request.META.get('REMOTE_ADDR')

    if not (post_id and text):
        return Response({'detail': 'Post ID and comment text are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        all_data_instance = AllData.objects.get(pk=post_id)
    except AllData.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user_id:
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        comment = Comment.objects.create(user=user, post=all_data_instance, text=text)
        CustomUser.objects.filter(pk=user.pk).update(points=F('points') + 10)
    else:
        existing_comment = Comment.objects.filter(post=all_data_instance, ip_address=ip_address).first()
        if existing_comment:
            existing_comment.text = text
            existing_comment.save()
            serializer = CommentSerializer(existing_comment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            comment = Comment.objects.create(post=all_data_instance, text=text, ip_address=ip_address)
    
    serializer = CommentSerializer(comment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)




@extend_schema(request=AllDataSerializer)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_all_data(request):
    serializer = AllDataSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(user=request.user)
        all_data_instance = serializer.instance
        all_data_instance.user = request.user
        all_data_instance.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(request=CommentSerializer)
@api_view(['GET'])
def get_comments(request):
    comments = Comment.objects.all()
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


@extend_schema(request=ReactionSerializer)
@api_view(['GET'])
def get_reactions(request):
    reactions = Reaction.objects.all()
    serializer = ReactionSerializer(reactions, many=True)
    return Response(serializer.data)


@extend_schema(request=AllDataSerializer)
@api_view(['GET'])
def get_all_data(request):
    all_data = AllData.objects.all()[::-1]
    serializer = AllDataSerializer(all_data, many=True)
    return Response(serializer.data)


@extend_schema(request=ReactionSerializer)
@api_view(['GET'])
def poll_view_count(request, pk):
    try:
        instance = AllData.objects.get(pk=pk)
    except AllData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = request.user if request.user.is_authenticated else None
    if user:
        poll_view, created = PollView.objects.get_or_create(poll=instance, user=user)
        poll_view.view_count += 1
        poll_view.save()
    else:
        random_username = generate_random_username()
        user, created = CustomUser.objects.get_or_create(username=random_username)
        PollView.objects.get_or_create(poll=instance, user=user)

    serializer = AllDataSerializer(instance)
    return Response(serializer.data)


@extend_schema(request=ReactionSerializer)
@api_view(['GET'])
def get_poll_view_count(request, pk):
    try:
        instance = AllData.objects.get(pk=pk)
    except AllData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    poll_views = PollView.objects.filter(poll=instance)
    total_views = poll_views.aggregate(Sum('view_count')).get('view_count__sum', 0)

    return Response({'poll_id': pk, 'total_views': total_views})
 
@extend_schema(request=CategorySerializer)
@api_view(['GET', 'POST'])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
@extend_schema(request=OptionChoiceSerializer)
@api_view(['POST'])
def create_option_choice(request, pk):
    user_id = request.data.get('user')
    option_selected = request.data.get('option_selected')
    ip_address = request.META.get('REMOTE_ADDR')

    if not option_selected:
        return Response({'detail': 'Option selection is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        all_data_instance = AllData.objects.get(pk=pk)
    except AllData.DoesNotExist:
        return Response({'detail': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user_id:
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        existing_option_choice = OptionChoice.objects.filter(post=all_data_instance, user=user).first()
        if existing_option_choice:
            existing_option_choice.option_selected = option_selected
            existing_option_choice.save()
            serializer = OptionChoiceSerializer(existing_option_choice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            option_choice = OptionChoice.objects.create(post=all_data_instance, option_selected=option_selected, user=user)
            CustomUser.objects.filter(pk=user.pk).update(points=F('points') + 10)
            serializer = OptionChoiceSerializer(option_choice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        existing_option_choice = OptionChoice.objects.filter(post=all_data_instance, ip_address=ip_address).first()

        if existing_option_choice:
            existing_option_choice.option_selected = option_selected
            existing_option_choice.save()
            serializer = OptionChoiceSerializer(existing_option_choice)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            option_choice = OptionChoice.objects.create(post=all_data_instance, option_selected=option_selected, ip_address=ip_address)
            serializer = OptionChoiceSerializer(option_choice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

@extend_schema(request=CustomUserSerializer)   
@api_view(['GET'])
def user_detail(request, pk):
    try:
        user_instance = CustomUser.objects.get(pk=pk)
        user_data = AllData.objects.filter(user=user_instance)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if not user_data:
        serializer = CustomUserSerializer(user_instance)
        return Response({"user_details": serializer.data, "associated_data": []})

    user_serializer = CustomUserSerializer(user_instance)
    data_serializer = AllDataSerializer(user_data, many=True)
    return Response({"user_details": user_serializer.data, "associated_data": data_serializer.data})
    
@extend_schema(request=logoSerializer)       
@api_view(['GET'])
def logo_list(request):
    logos = logo.objects.all()
    serializer = logoSerializer(logos, many=True)
    return Response(serializer.data)
 
    
@api_view(['POST'])
def change_password(request):
    user_id = request.data.get('user_id')
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    if not (user_id and old_password and new_password):
        return Response({'error': 'User ID, old password, and new password are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if not user.check_password(old_password):
        return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    user.password = make_password(new_password)
    user.save()

    return Response({'success': 'Password has been changed successfully'}, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def alldata_detail(request, pk):
    try:
        alldata_instance = AllData.objects.get(pk=pk)
    except AllData.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = AllDataSerializer(alldata_instance)
    return Response(serializer.data)
    
    
@api_view(['GET'])
def Share_count(request, pk):
    try:
        alldata_instance = AllData.objects.get(pk=pk)
        alldata_instance.Share_count += 1
        alldata_instance.save()

        return Response({"detail": "Share count incremented successfully."})
    except AllData.DoesNotExist:
        return Response({"detail": "AllData instance does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        


@api_view(['GET'])
def search_polls(request):
    query = request.GET.get('q', None)
    category = request.GET.get('category', None)
    post_type = request.GET.get('post_type', None)

    if query is None and category is None and post_type is None:
        return Response({"error": "No search parameters provided."}, status=status.HTTP_400_BAD_REQUEST)

    polls = AllData.objects.all()

    if query:
        polls = polls.filter(
            Q(notice__icontains=query) |
            Q(text__icontains=query) |
            Q(option1__icontains=query) |
            Q(option2__icontains=query) |
            Q(option3__icontains=query) |
            Q(option4__icontains=query)
        )

    if category:
        polls = polls.filter(category__name__icontains=category)

    if post_type:
        polls = polls.filter(post_type=post_type)

    serializer = AllDataSerializer(polls, many=True)
    return Response(serializer.data)        

@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        try:
            # Parse the JSON body
            # body = json.loads(request.body.decode('utf-8'))
            phone_number = request.POST.get('phone_number')
            new_password = request.POST.get('new_password')

            if not phone_number or not new_password:
                return JsonResponse({'error': 'Phone number and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Retrieve the user by phone number
                user = CustomUser.objects.get(phone_number=phone_number)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'User not found with the provided phone number.'}, status=status.HTTP_404_NOT_FOUND)

            # Update the user's password
            user.set_password(new_password)
            user.save()

            return JsonResponse({'success': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse({'error': 'Only POST method is allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)