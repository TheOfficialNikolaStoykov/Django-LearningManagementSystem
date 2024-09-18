import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from wystia import WistiaApi, WistiaUploadApi
from wystia.models import SortBy

from .forms import LessonForm
from .models import Course, Lesson, News, Section, Student, Teacher


class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'news.add_news'
    model = News
    fields = ['title', 'content']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user

        return super().form_valid(form)

def paginate_objects(request, queryset, items_per_page=5):
    paginator = Paginator(queryset, items_per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

def add_no_items_message(queryset, message):
    if not queryset.exists():
        return message
    return None

def get_courses_for_user(user):
    if user.is_superuser or user.is_staff:
        return Course.objects.all()
    elif user.is_teacher:
        return Course.objects.filter(teacher=user.id)
    elif user.is_student:
        student_instance = Student.objects.get(user=user)
        return Course.objects.filter(students=student_instance)
    return Course.objects.none()

def get_all_news():
    return News.objects.all()

@login_required
def index_redirection_view(request):
    all_news = get_all_news()
    user_courses = get_courses_for_user(request.user)

    paginated_news = paginate_objects(request, all_news)
    paginated_courses = paginate_objects(request, user_courses)

    course_message = add_no_items_message(user_courses, "No courses available at the moment.")
    news_message = add_no_items_message(all_news, "No news available at the moment.")

    context = {
        'all_courses': paginated_courses,
        'all_news': paginated_news,
        'course_message': course_message,
        'news_message': news_message,
    }

    if request.user.is_superuser or request.user.is_staff:
        return render(request, 'app/index_admin.html', context)
    elif request.user.is_teacher:
        return render(request, 'app/index_teacher.html', context) # We only need one page I think
    elif request.user.is_student:
        return render(request, 'app/index_student.html', context)
    else:
        return render(request, 'app/login.html')

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
    WistiaApi.configure(settings.WISTIA_API)
    object = Lesson.objects.latest('id')
    path = object.file.path
    name = object.file.name
    full_path = os.path.join('media', name)
    request = WistiaUploadApi.upload_file(full_path)

    return print(request.created)

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
def password_change_view(request):

    return render(request, 'templates/registration/password_change_form.html')


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


