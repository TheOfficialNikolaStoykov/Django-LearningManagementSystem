import os
from django.contrib import admin
from .models import Teacher, Student, Course, News, Lesson, Section
from wystia import WistiaApi, WistiaUploadApi


class LessonAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)
        self.upload_video_to_wistia()


    def upload_video_to_wistia(self):
        WistiaApi.configure('8e09fb0ac8fd7fa7da3493fe772cb966fbf252167e83260411d4cbf255e3db1e')
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


# Register your models here.
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(News, NewsAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Course)
admin.site.register(Section)