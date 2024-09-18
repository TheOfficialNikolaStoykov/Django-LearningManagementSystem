import os

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from wystia import WistiaApi, WistiaUploadApi

from .models import *


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


admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(CustomUser)
admin.site.register(News, NewsAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Course)
admin.site.register(Section)