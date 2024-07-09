from django.urls import re_path, path, include
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views
from .views import MyTokenObtainPairView, ProfileView, ProjectView, AllProjectsView, AllClientsView, ProjectDetailView, \
    ClientView, ClientDetailView, get_csrf_token

urlpatterns = [
    re_path(r'^get-csrf-token/$', get_csrf_token),

    re_path(r'^create_message/$', views.create_message, name='create_message'),
    re_path(r'^newsletter/subscribe/$', views.newsletter_subscribe, name='newsletter_subscribe'),
    re_path(r'^newsletter/unsubscribe/$', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),

    re_path(r'^reset_password/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    re_path(r'^token/$', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
    re_path('^profile/$', ProfileView.as_view(), name='profile'),
    re_path('^projects/$', ProjectView.as_view(), name='projects'),
    path('project/<int:id>/', ProjectDetailView.as_view(), name='project-detail'),
    re_path('^all-projects/$', AllProjectsView.as_view(), name='all-projects'),

    re_path('^all-clients/$', AllClientsView.as_view(), name='all-clients'),
    re_path('^clients/$', ClientView.as_view(), name='clients'),
    path('client/<int:id>/', ClientDetailView.as_view(), name='client-detail')

]
