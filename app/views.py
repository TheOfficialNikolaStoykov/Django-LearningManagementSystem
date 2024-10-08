import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from wystia import WistiaApi, WistiaUploadApi

from .forms import LessonForm
from .models import Course, Lesson, News, Section, Student, Teacher

WistiaApi.configure(settings.WISTIA_API_KEY)


def add_no_items_message(queryset, message):
    if not queryset.exists():
        return message
    return None

@login_required
def index_redirection_view(request):
    news = News.objects.order_by('date_created')
    news_paginator = Paginator(news, 5)
    page_number = request.GET.get("page")
    page_obj = news_paginator.get_page(page_number)

    courses = Course.objects.all()

    courses_message = ""
    news_message = ""

    courses_message = add_no_items_message(courses, "No courses available at the moment.")
    news_message = add_no_items_message(news, "No news available at the moment.")

    context = {
        'courses': courses,
        "page_obj": page_obj,
        'courses_message': courses_message,
        'news_message': news_message,
    }

    if request.user.is_teacher:
        teacher_instance = Teacher.objects.get(user=request.user)
        teacher_courses = Course.objects.filter(teacher=teacher_instance)
        courses_message = add_no_items_message(teacher_courses, "No courses available at the moment.")

        context['courses'] = teacher_courses
        context['courses_message'] = courses_message

    elif request.user.is_student:
        student_instance = Student.objects.get(user=request.user)
        student_courses = Course.objects.filter(students=student_instance)
        courses_message = add_no_items_message(student_courses, "No courses available at the moment.")

        context['courses'] = student_courses
        context['courses_message'] = courses_message
    
    elif request.user.is_staff or request.user.is_superuser:
        return render(request, 'app/index.html', context)
    else:
        return render(request, 'registration/login.html')
        
    return render(request, 'app/index.html', context)

class NewsCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'app.add_news'
    model = News
    fields = ['title', 'content']
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        form.instance.posted_by = self.request.user

        return super().form_valid(form)

class NewsDetailView(LoginRequiredMixin, DetailView):
    model = News

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
def password_change_view(request):

    return render(request, 'templates/registration/password_change_form.html')

class LessonCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'app.add_lesson'
    model = Lesson
    form_class = LessonForm
    success_url = reverse_lazy("create_lesson")
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        teacher_instance = Teacher.objects.get(user=self.request.user)
        form.fields['course'].queryset = Course.objects.filter(teacher=teacher_instance)

        if self.request.method == 'POST':
            selected_course_id = self.request.POST.get('course')
            if selected_course_id:
                try:
                    selected_course = Course.objects.get(id=selected_course_id)
                    form.fields['section'].queryset = Section.objects.filter(course=selected_course)
                except Course.DoesNotExist:
                    form.fields['section'].queryset = Section.objects.none()
            else:
                form.fields['section'].queryset = Section.objects.none()
        else:
            form.fields['section'].queryset = Section.objects.none()

        return form

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        
        response = super().form_valid(form)
        
        video_file = form.instance.file
        upload_to_wistia(video_file)

        return response

class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    WistiaApi.configure(settings.WISTIA_API_KEY)

    def get_media_url(self):

        course_pk = self.object.course.pk
        current_course = Course.objects.get(id=course_pk)
        
        try:
            projects = WistiaApi.list_all_projects()
        
            matching_projects = [p for p in projects if p.name == current_course.name]
            
            if not matching_projects:
                raise ValueError(f"No Wistia project found for course: {current_course.name}")
            
            project = matching_projects[0]

            videos = WistiaApi.list_project(project.id)

            video_hashed_id = videos[0].hashed_id
            
            embed_code = f"""<script src="https://fast.wistia.com/embed/medias/{video_hashed_id}.jsonp" async></script>
            <script src="https://fast.wistia.com/assets/external/E-v1.js" async></script>
            <div class="wistia_responsive_padding" style="padding:56.25% 0 0 0;position:relative;">
            <div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;">
            <div class="wistia_embed wistia_async_{video_hashed_id} seo=true videoFoam=true" style="height:100%;position:relative;width:100%">
            <div class="wistia_swatch" style="height:100%;left:0;opacity:0;overflow:hidden;position:absolute;top:0;transition:opacity 200ms;width:100%;">
            <img src="https://fast.wistia.com/embed/medias/{video_hashed_id}/swatch" style="filter:blur(5px);height:100%;object-fit:contain;width:100%;" alt="" aria-hidden="true" onload="this.parentNode.style.opacity=1;" />
            </div></div></div></div>"""
            
            return embed_code
        
        except ValueError:
            raise
        except Exception as e:
            return f"Error during listing project/s: {e}"

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

def get_sections_by_course(request, course_id):
    sections = Section.objects.filter(course_id=course_id)
    section_list = [{'id': section.id, 'title': section.title} for section in sections]
    return JsonResponse(section_list, safe=False)

def upload_to_wistia(video_file):
    filename = video_file.file.name
    video_file_path = os.path.join('media', filename)
    
    try:
        response = WistiaUploadApi.upload_file(video_file_path)
        return response
    except Exception as e:
        print(f"An error occurred while uploading the file to Wistia: {str(e)}")
        raise

@login_required
def courses_view(request):
    if request.user.is_teacher:
        teacher_instance = Teacher.objects.get(user=request.user)
        courses = Course.objects.filter(teacher=teacher_instance)
        courses_message = add_no_items_message(courses, "No courses available at the moment.")

        context = {'courses': courses,
                   'courses_message': courses_message}

    elif request.user.is_student:
        student_instance = Student.objects.get(user=request.user)
        courses = Course.objects.filter(students=student_instance)
        courses_message = add_no_items_message(courses, "No courses available at the moment.")

        context = {'courses': courses,
                   'courses_message': courses_message}

    elif request.user.is_staff or request.user.is_superuser:
        courses = Course.objects.all()
        courses_message = add_no_items_message(courses, "No courses available at the moment.")

        context = {'courses': courses,
                   'courses_message': courses_message}

    return render(request, 'app/courses.html', context)

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

class SectionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'app.add_section'
    model = Section
    fields = "__all__"
    success_url = reverse_lazy('create_lesson')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        teacher_instance = Teacher.objects.get(user=self.request.user)
        form.fields['course'].queryset = Course.objects.filter(teacher=teacher_instance)

        return form