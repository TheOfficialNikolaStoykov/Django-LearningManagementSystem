import os
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Course, News, Student, Teacher, Lesson, Section
from django.views.generic import ListView, CreateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from .forms import LessonForm
from wystia import WistiaApi, WistiaUploadApi
from wystia.models import SortBy
from django.core.paginator import Paginator



class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_news'
    model = News
    fields = ['title', 'content']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user

        return super().form_valid(form)


@login_required
def admin_profile_view(request):

    return render(request, 'app/profile_admin.html')


@login_required
def teacher_profile_view(request):
    details = Teacher.objects.filter(user=request.user)
    context = {'details': details}
    
    return render(request, 'app/profile_teacher.html', context=context)


@login_required
def student_profile_view(request):
    details = Student.objects.filter(user=request.user)
    context = {'details': details}
    
    return render(request, 'app/profile_student.html', context=context)


@login_required
def index_view(request):
    news = News.objects.all()
    news_paginator = Paginator(news, 5)
    page_number = request.GET.get('page')
    news_objects = news_paginator.get_page(page_number)

    context = {'news_objects':news_objects}

    if request.user.groups.filter(name='Students').exists():
        courses = Course.objects.filter(students=request.user)
        courses_paginator = Paginator(courses, 4)
        page_number = request.GET.get('page')
        course_objects = courses_paginator.get_page(page_number)

        context = {'course_objects':course_objects, 'news_objects':news_objects}

    elif request.user.groups.filter(name='Teachers').exists():
        courses = Course.objects.filter(teacher=request.user.id)
        courses_paginator = Paginator(courses, 5)
        page_number = request.GET.get('page')
        course_objects = courses_paginator.get_page(page_number)

        context = {'course_objects':course_objects, 'news_objects':news_objects}

    return render(request, 'app/index.html', context=context)


@login_required
@permission_required('lesson.add_lesson')
def lesson_create_view(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            upload_to_wistia()
            return HttpResponseRedirect('/app/courses')
        else:
            print(form.errors)
    else:
        form = LessonForm()

    return render(request, 'app/create_lesson.html', {'form': form})


def upload_to_wistia():
    WistiaApi.configure(os.environ['WISTIA_API'])
    object = Lesson.objects.latest('id')
    path = object.file.path
    name = object.file.name
    full_path = os.path.join('media', name)
    request = WistiaUploadApi.upload_file(full_path)

    return print(request.created)


class PasswordChangeView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/password_change_form.html'


@login_required
def password_change_view(request):

    return render(request, 'templates/registration/password_change_form.html')


class NewsDetailView(LoginRequiredMixin, DetailView):
    model = News


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.object.pk
        current_course = Course.objects.get(id=pk)
        lessons = Lesson.objects.filter(course=current_course)
        sections = Section.objects.filter(lesson__in=lessons)
        
        context['lessons'] = lessons
        context['sections'] = sections

        return context


@login_required
def courses_view(request):
    if request.user.groups.filter(name='Teachers').exists():
        courses = Course.objects.filter(teacher=request.user.id)

        context = {'courses':courses}

    elif request.user.groups.filter(name='Students').exists():
        courses = Course.objects.filter(students=request.user)

        context = {'courses':courses}

    elif request.user.is_superuser:
        courses = Course.objects.all()

        context = {'courses':courses}

    return render(request, 'app/courses.html', context=context)


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson

    def get_media_url(self):
        WistiaApi.configure(os.environ['WISTIA_API'])
        projects = WistiaApi.list_all_projects(SortBy.NAME)

        list_project_info = []

        for item in projects:
            project_info = {'name': item.name, 'hashed_id': item.hashed_id}
            list_project_info.append(project_info)


        course_pk = self.object.course.pk
        current_course = Course.objects.get(id=course_pk)
        current_course_name = current_course.name

        lesson_pk = self.object.pk

        print(lesson_pk)
        
        for item in list_project_info:
            if item['name'] == current_course_name:
                hashed_id = item['hashed_id']
                videos = WistiaApi.list_videos(hashed_id)

        print(videos)

        video = videos[(lesson_pk - 1)].hashed_id

        return f'<script charset="ISO-8859-1" src="//fast.wistia.com/assets/external/E-v1.js" async></script><div class="wistia_responsive_padding" style="padding:56.25% 0 28px 0;position:relative;"><div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;"><div class="wistia_embed wistia_async_{video} fullscreenButton=true playbackRateControl=true playbar=true settingsControl=true" style="height:100%;width:100%">&nbsp;</div></div></div>'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_pk = self.object.course.pk

        current_course = Course.objects.get(id=course_pk)
        lessons = Lesson.objects.filter(course=current_course)
        sections = Section.objects.filter(lesson__in=lessons)
        
        embed_url = self.get_media_url()

        context['embed_url'] = embed_url
        context['lessons'] = lessons
        context['sections'] = sections

        return context


class SectionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'section.add_section'
    model = Section
    fields = "__all__"
    success_url = reverse_lazy('create_lesson')


