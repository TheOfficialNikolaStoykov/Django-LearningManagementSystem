import os

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from wystia import WistiaApi, WistiaUploadApi
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import *


class OverridenUserCreationForm(UserCreationForm):
    is_teacher = forms.BooleanField(required=False)
    is_student = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('is_teacher', 'is_student') 

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = self.cleaned_data['is_teacher']
        user.is_student = self.cleaned_data['is_student']
        if commit:
            user.save()
        return user

class OveriddenUserAdmin(UserAdmin):
    add_form = OverridenUserCreationForm
    list_display = ['username', 'is_teacher', 'is_student']


class LessonAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)
        self.upload_video_to_wistia()


    def upload_video_to_wistia(self):
        WistiaApi.configure(settings.WISTIA_API_KEY)
        object = Lesson.objects.latest('id')
        path = object.file.path
        name = object.file.name
        full_path = os.path.join('media', name)
        request = WistiaUploadApi.upload_file(full_path)


class NewsAdmin(admin.ModelAdmin):
    exclude = ['posted_by']

    def save_model(self, request, obj, form, change):
        obj.posted_by = request.user
        super().save_model(request, obj, form, change)

OveriddenUserAdmin.add_fieldsets = UserAdmin.add_fieldsets + (('Custom Fields', {'fields': ('is_teacher', 'is_student')}),)

admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(CustomUser, OveriddenUserAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Course)
admin.site.register(Section)