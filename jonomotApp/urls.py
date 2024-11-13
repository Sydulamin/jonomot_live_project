from django.urls import path
from .views import *

urlpatterns = [
    path('register/', user_registration, name='user-registration'),
    path('login/', user_login, name='user-login'),
    path('reactions/', create_reaction, name='create_reaction'),
    path('comments/', create_comment, name='create_comment'),
    path('api/create_all_data/', create_all_data, name='create_all_data'),
    path('comments/', get_comments, name='get_comments'),
    path('reactions/', get_reactions, name='get_reactions'),
    path('alldata/', get_all_data, name='get_all_data'),
    path('polls/<int:pk>/view/', poll_view_count, name='poll-view'),
    path('polls/<int:pk>/view-count/', get_poll_view_count, name='poll-view-count'),
    path('categories/', category_list, name='category-list'),
    path('create_option_choice/<int:pk>/', create_option_choice, name='create-option-choice'),
    path('user/<int:pk>/', user_detail, name='user-detail'),
    path('api/logos/', logo_list, name='logo-list'),
    path('verify/<str:token>/', verify_email, name='verify_email'),
    path('update-profile/', update_profile, name='update-profile'),
    path('change-password/', change_password, name='change_password'),
    path('alldata/<int:pk>/', alldata_detail, name='alldata-detail'),
    path('Share_count/<int:pk>/', Share_count, name='Share_count'),
    path('polls/search/', search_polls, name='search_polls'),
    path('reset-password/', reset_password, name='reset_password'),
    ]