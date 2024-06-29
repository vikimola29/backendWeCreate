from django.urls import re_path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views
from .views import MyTokenObtainPairView, ProfileView, ProjectView, AllProjectView

urlpatterns = [
    re_path(r'^api/create_message/$', views.create_message, name='create_message'),
    re_path(r'^api/newsletter/subscribe/$', views.newsletter_subscribe, name='newsletter_subscribe'),
    re_path(r'^api/newsletter/unsubscribe/$', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    re_path(r'^api/register/$', views.user_register, name='register'),
    re_path(r'^api/recover/$', views.user_recover, name='recover'),
    re_path(r'^api/recover-password/$', views.user_recover_password, name='recover-password'),
    re_path(r'^api/token/$', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^api/token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('^api/profile/$', ProfileView.as_view(), name='profile'),
    re_path('^api/projects/$', ProjectView.as_view(), name='projects'),
    re_path('^api/all-projects/$', AllProjectView.as_view(), name='all-projects'),

]
