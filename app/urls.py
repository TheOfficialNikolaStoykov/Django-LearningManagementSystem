from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index_redirection_view, name='index'),
    path('post_news/', views.NewsCreateView.as_view(), name='post_news'),
    path('profile_admin/', views.admin_profile_view, name='profile_admin'),
    path('profile_teacher/', views.teacher_profile_view, name='profile_teacher'),
    path('profile_student/', views.student_profile_view, name='profile_student'),
    path('create_lesson/', views.LessonCreateView.as_view(), name='create_lesson'),
    path('courses/', views.courses_view, name='courses'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('news_detail/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('course_detail/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('lesson_detail/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('create_section/', views.SectionCreateView.as_view(), name='create_section')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)