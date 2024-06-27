import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
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
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import NewsletterUser, MyUser
from .serializers import MessageSerializer, NewsletterUserSignUpSerializer, MyTokenObtainPairSerializer


@method_decorator(csrf_exempt, name='dispatch')
class MyTokenObtainPairView(TokenObtainPairView):
    print("Views.py")
    serializer_class = MyTokenObtainPairSerializer


@csrf_exempt
@api_view(['POST'])
def user_register(request):
    if request.method == 'POST':
        print("AAA")
        name = request.data.get('name')
        email = request.data.get('email')
        company_name = request.data.get('companyName')
        password = request.data.get('password')
        password2 = request.data.get('password2')
        print("BBB")

        if MyUser.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Username already taken'})

        print("CCC")

        if password != password2:
            return JsonResponse({'success': False, 'message': 'Passwords do not match'})
        print("EEE")

        # password = make_password(password)
        # print("FFF0")
        user = MyUser(name=name, email=email, password=make_password(password), is_active=True, address=None,
                      company_name=company_name, status="Client")
        print("FFF")


        print("GGG")
        user.save()
        print("HHH")
        return JsonResponse({'success': True, 'message': 'Registration successful'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def get_data(request):
    data = MyUser.objects.all().values()
    return JsonResponse({'data': list(data)})


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
