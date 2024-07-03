import logging
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password
from django.utils.crypto import constant_time_compare, get_random_string
import hashlib
from django.contrib.auth.hashers import BasePasswordHasher
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, send_mail
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.http import JsonResponse
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import NewsletterUser, MyUser, Project
from .serializers import MessageSerializer, NewsletterUserSignUpSerializer, MyTokenObtainPairSerializer, \
    MyUserSerializer, ProjectSerializer


@method_decorator(csrf_exempt, name='dispatch')
class ClientDetailView(APIView):
    print('Client Detail')
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    print('Client Detail - after Permissions')

    def get(self, request, id):
        client = MyUser.objects.filter(pk=id)
        serializer = MyUserSerializer(client, many=True)
        return Response(serializer.data)

    def put(self, request, id):
        client = get_object_or_404(MyUser, pk=id)
        client_data = {
            'email': request.data.get('email'),
            'name': request.data.get('name'),
            'address': request.data.get('address'),
            'phone_number': request.data.get('phone_number'),
            'company_name': request.data.get('company_name'),
            'status': request.data.get('status'),
            'is_staff': request.data.get('is_staff'),
            'is_superuser': request.data.get('is_superuser')
        }
        serializer = MyUserSerializer(client, data=client_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        client = get_object_or_404(MyUser, pk=id)
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name='dispatch')
class ClientView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        serializer = MyUserSerializer(user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        client_data = {
            'name': request.data.get('name'),
            'email': request.data.get('email'),
            'company_name': request.data.get('company_name'),
            'password': request.data.get('password'),
            'password2': request.data.get('password2')
        }

        if MyUser.objects.filter(email=client_data['email']).exists():
            return JsonResponse({'success': False, 'message': 'Email already taken'})

        if client_data['password'] != client_data['password2']:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'})

        serializer = MyUserSerializer(data=client_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class AllClientsView(APIView):
    serializer_class = MyUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        clients = MyUser.objects.all()
        serializer = MyUserSerializer(clients, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectDetailView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Project.objects.filter(client=self.request.user)

    def get(self, request, id):
        project = Project.objects.filter(pk=id)
        serializer = ProjectSerializer(project, many=True)
        return Response(serializer.data)

    def put(self, request, id):
        project = get_object_or_404(Project, id=id)

        client_email = request.data.get('client')
        client = get_object_or_404(MyUser, email=client_email)

        project_data = {
            'name': request.data.get('name'),
            'link': request.data.get('link'),
            'client': client.id,
            'status': request.data.get('status'),
            'finish_due_date': request.data.get('finish_due_date'),
            'batch_price': request.data.get('batch_price'),
            'monthly_price': request.data.get('monthly_price'),
            'batch_payment_due_date': request.data.get('batch_payment_due_date'),
            'monthly_payment_due_date': request.data.get('monthly_payment_due_date'),
            'batch_payment_status': request.data.get('batch_payment_status'),
            'monthly_payment_status': request.data.get('monthly_payment_status'),
            'registered_date': request.data.get('registered_date')
        }
        serializer = ProjectSerializer(project, data=project_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        project = get_object_or_404(Project, pk=id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name='dispatch')
class AllProjectsView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class ProjectView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        projects = Project.objects.filter(client=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        client_email = request.data.get('client')

        client = get_object_or_404(MyUser, email=client_email)

        project_data = {
            'name': request.data.get('name'),
            'link': request.data.get('link'),
            'client': client.id,
            'status': request.data.get('status'),
            'finish_due_date': request.data.get('finish_due_date'),
            'batch_price': request.data.get('batch_price'),
            'monthly_price': request.data.get('monthly_price'),
            'batch_payment_due_date': request.data.get('batch_payment_due_date'),
            'monthly_payment_due_date': request.data.get('monthly_payment_due_date'),
            'batch_payment_status': request.data.get('batch_payment_status'),
            'monthly_payment_status': request.data.get('monthly_payment_status'),
            'registered_date': request.data.get('registered_date')
        }

        serializer = ProjectSerializer(data=project_data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = MyUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = MyUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


def user_recover(request):
    return None


def user_recover_password(request):
    return None


@csrf_exempt
@api_view(['POST', 'GET'])
def create_message(request):
    if request.method == 'POST':
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            name = request.POST.get('name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            message = request.POST.get('message')

            subject = "WeCreate - Contact Form"
            content = f"Name: {name} \n" \
                      f"Phone: {phone}\n" \
                      f"Email: {email}\n" \
                      f"Message: {message}"

            # from_mail = settings.EMAIL_HOST_USER
            from_email = 'wecreate.designs.srl@hotmail.com'
            recipient_list = ['wecreate.designs.srl@gmail.com']

            # send_mail(subject, content, from_email, recipient_list, fail_silently=False)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
        return HttpResponse("Yo")


logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST', 'GET'])
def newsletter_subscribe(request):
    if request.method == 'POST':
        try:
            serializer = NewsletterUserSignUpSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                if not NewsletterUser.objects.filter(email=email).exists():
                    serializer.save()
                    subject = "Bine ai venit la WeCreate!"
                    # from_email = settings.EMAIL_HOST_USER
                    from_email = 'wecreate.designs.srl@hotmail.com'
                    recipient_list = [email]
                    subscribe_message = get_template('subscribe_email.txt').render()
                    html_template = get_template('subscribe_email.html').render()
                    message = EmailMultiAlternatives(subject=subject, body=subscribe_message, from_email=from_email,
                                                     to=recipient_list)
                    message.attach_alternative(html_template, "text/html")
                    # message.send()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(f"Validation error occurred: {e}")
            return Response({"error": "Validation error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return HttpResponseServerError("An unexpected error occurred. Please try again later.")
    else:
        return HttpResponse("Yo")


@csrf_exempt
@api_view(['POST', 'GET'])
def newsletter_unsubscribe(request):
    if request.method == 'POST':
        serializer = NewsletterUserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if NewsletterUser.objects.filter(email=email).exists():
                serializer.save()
                NewsletterUser.objects.filter(email=email).delete()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            else:
                print('Email NOT exists')
                messages.warning(request, "Email not in database.", extra_tags='warning')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    else:
        return HttpResponse("Yo")
