from django.contrib import admin

from django.contrib import admin
from django.urls import include, path

from .models import Message, NewsletterUser, Newsletter, MyUser, Project

urlpatterns = [
    path("", include("BackendApp.urls")),
    path("admin/", admin.site.urls),
]


class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_added',)


class MyUserAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'name', 'address', 'company_name', 'status', 'is_staff', 'is_superuser', 'is_active',
        'registered_date')


admin.site.register(Message)
admin.site.register(NewsletterUser, NewsletterAdmin)
admin.site.register(Newsletter)
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Project)
