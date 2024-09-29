import os
from json import loads
from types import SimpleNamespace
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import Course, CustomUser, Lesson, News, Section, Student, Teacher
from .views import upload_to_wistia


class ViewsTestCase(TestCase):
    """Test case for views in the application."""

    def setUp(self):
        """Set up initial test data including users, courses, and lessons."""
        self.teacher_user = CustomUser.objects.create_user(username="test_teacher", password="password", is_teacher=True, is_superuser = False, is_staff = False)
        self.student_user = CustomUser.objects.create_user(username="test_student", password="password", is_student=True, is_superuser = False, is_staff = False)
        self.admin_user = CustomUser.objects.create_superuser(username="test_admin_user", password="password")

        self.teacher_user.user_permissions.add(Permission.objects.get(codename="add_lesson"))
        self.teacher_user.user_permissions.add(Permission.objects.get(codename="add_section"))
        self.teacher_user.save()

        self.teacher = Teacher.objects.create(user=self.teacher_user, first_name="Teacher", last_name="User", date_of_birth="1990-01-01", address="123 St", email="teacher@example.com")
        self.student = Student.objects.create(user=self.student_user, first_name="Student", last_name="User", date_of_birth="2000-01-01", address="456 St", email="student@example.com", faculty_id=123)

        self.course = Course.objects.create(name="Test Course", teacher=self.teacher)
        self.section = Section.objects.create(title="Test Section", course=self.course)
        self.news = News.objects.create(title="Test News", content="News Content", posted_by=self.teacher_user)
        self.lesson = Lesson.objects.create(title="Test Lesson 1", description="Lesson Description", course=self.course, section=Section.objects.create(title="Section 1", course=self.course))

    def get_test_image(self):
        """Helper function to reference the existing image from the media directory."""
        image_path = os.path.join(settings.MEDIA_ROOT, 'test_image.jpg')
        return SimpleUploadedFile(name='test_image.jpg', content=open(image_path, 'rb').read(), content_type='image/jpeg')
    
    def get_test_video_file(self):
        """Helper function to reference the existing video from the media directory."""
        video_path = os.path.join(settings.MEDIA_ROOT, 'Example_Video.mp4')
        with open(video_path, 'rb') as f:
            return File(f, name='Example_Video.mp4')

    def test_custom_user_str(self):
        """Test string representation of custom users."""
        self.assertEqual(str(self.teacher_user), "test_teacher")
        self.assertEqual(str(self.student_user), "test_student")

    def test_teacher_profile_picture_resize(self):
        """Test resizing of teacher's profile picture."""
        large_image = Image.new('RGB', (500, 500))
        large_image_path = os.path.join(settings.MEDIA_ROOT, 'large_test_image.jpg')
        large_image.save(large_image_path)

        with open(large_image_path, 'rb') as img_file:
            self.teacher.profile_picture = SimpleUploadedFile(name='large_test_image.jpg', content=img_file.read(), content_type='image/jpeg')

        self.teacher.save()

        image = Image.open(self.teacher.profile_picture.path)
        
        self.assertTrue(image.width <= 300)
        self.assertTrue(image.height <= 300)

    def test_student_profile_picture_resize(self):
        """Test resizing of student's profile picture."""
        large_image = Image.new('RGB', (500, 500))
        large_image_path = os.path.join(settings.MEDIA_ROOT, 'large_student_image.jpg')
        large_image.save(large_image_path)

        with open(large_image_path, 'rb') as img_file:
            self.student.profile_picture = SimpleUploadedFile(name='large_student_image.jpg', content=img_file.read(), content_type='image/jpeg')

        self.student.save()

        image = Image.open(self.student.profile_picture.path)
        
        self.assertTrue(image.width <= 300)
        self.assertTrue(image.height <= 300)
    
    def test_lesson_get_index_in_course(self):
        """Test the method for getting the lesson index in a course."""
        lesson_2 = Lesson.objects.create(title="Test Lesson 2", description="Desc 1", course=self.course, section=self.section)
 
        self.assertEqual(self.lesson.get_index_in_course(), 0)
        self.assertEqual(lesson_2.get_index_in_course(), 1)

    def test_index_view_anonymous_user(self):
        """Test index view for anonymous user redirects to login."""
        regular_user = CustomUser.objects.create_user(username="test_user", password="password")
        self.client.login(username=regular_user.username, password="password")
        
        response = self.client.get(reverse("index"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_index_view_as_teacher(self):
        """Test index view for logged-in teacher user."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("index"))
        
        self.assertEqual(response.status_code, 200)

    def test_index_view_as_student(self):
        """Test index view for logged-in student user."""
        self.client.login(username=self.student_user.username, password="password")
        
        response = self.client.get(reverse("index"))
        
        self.assertEqual(response.status_code, 200)

    def test_index_view_as_superuser(self):
        """Test index view for logged-in superuser."""
        self.client.login(username=self.admin_user.username, password="password")
        
        response = self.client.get(reverse("index"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/index.html")

    def test_news_create_view_permission(self):
        """Test news creation view without the required permission."""
        self.client.login(username=self.student_user.username, password="password")
        
        response = self.client.get(reverse("post_news"))
        
        self.assertEqual(response.status_code, 403)

    def test_news_create_view_with_permission(self):
        """Test news creation view with the required permission."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        self.teacher_user.user_permissions.add(Permission.objects.get(codename="add_news"))
        
        response = self.client.post(reverse("post_news"), {"title": "News Title", "content": "Some content"})
        
        self.assertRedirects(response, reverse("index"))

    @patch("app.views.upload_to_wistia")
    def test_lesson_create_view(self, mock_wistia_upload):
        """Test lesson creation view with a valid file upload."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        data = {
            "title": "Test Lesson",
            "description": "Lesson Description",
            "course": self.course.pk,
            "section": Section.objects.create(title="New Section", course=self.course).pk,
            "file": SimpleUploadedFile(name='Example_Video.mp4', content=b'A test video file content', content_type='video/mp4')
        }
        
        response = self.client.post(reverse("create_lesson"), data)
        
        self.assertEqual(response.status_code, 302)
    
    @patch("app.views.upload_to_wistia")
    def test_lesson_create_view_course_does_not_exist(self, mock_wistia_upload):
        """Test lesson creation when course does not exist."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        data = {
            "title": "Test Lesson",
            "description": "Lesson Description",
            "course": 4,
            "section": Section.objects.create(title="New Section", course=self.course).pk,
            "file": SimpleUploadedFile(name='Example_Video.mp4', content=b'A test video file content', content_type='video/mp4')
        }
        
        response = self.client.post(reverse("create_lesson"), data)

        self.assertEqual(response.status_code, 200)
        
        form = response.context.get("form", None)
        self.assertIsNotNone(form)
        self.assertQuerysetEqual(form.fields['section'].queryset, Section.objects.none())
    
    @patch("app.views.upload_to_wistia")
    def test_lesson_create_view_course_no_course(self, mock_wistia_upload):
        """Test lesson creation view when no course is selected."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        data = {
            "title": "Test Lesson",
            "description": "Lesson Description",
            "course": "",
            "section": Section.objects.create(title="New Section", course=self.course).pk,
            "file": SimpleUploadedFile(name='Example_Video.mp4', content=b'A test video file content', content_type='video/mp4')
        }
        
        response = self.client.post(reverse("create_lesson"), data)

        self.assertEqual(response.status_code, 200)
        
        form = response.context.get("form", None)
        self.assertIsNotNone(form)
        self.assertQuerysetEqual(form.fields['section'].queryset, Section.objects.none())
    
    @patch("app.views.upload_to_wistia")
    def test_lesson_create_view_course_get(self, mock_wistia_upload):
        """Test getting lesson creation view."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("create_lesson"))

        self.assertEqual(response.status_code, 200)
        
        form = response.context.get("form", None)
        self.assertIsNotNone(form)
        self.assertQuerysetEqual(form.fields['section'].queryset, Section.objects.none())

    def test_admin_profile_view(self):
        """Test admin profile view."""
        self.client.login(username=self.admin_user.username, password="password")
        
        response = self.client.get(reverse("profile_admin"))
        
        self.assertEqual(response.status_code, 200)

    def test_teacher_profile_view(self):
        """Test teacher profile view."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("profile_teacher"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.teacher.first_name)

    def test_student_profile_view(self):
        """Test student profile view."""
        self.client.login(username=self.student_user.username, password="password")
        
        response = self.client.get(reverse("profile_student"))
        
        self.assertEqual(response.status_code, 200)

    @patch("app.views.WistiaApi.list_all_projects")
    @patch("app.views.WistiaApi.list_project")
    def test_lesson_detail_view_with_wistia(self, mock_list_project, mock_list_all_projects):
        """Test lesson detail view including Wistia video information."""
        mock_list_all_projects.return_value = [SimpleNamespace(name="Test Course", id="123")]
        mock_list_project.return_value = [SimpleNamespace(hashed_id="hashed123")]
        
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("lesson_detail", args=(self.lesson.pk,)))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "fast.wistia.com")
    
    @patch("app.views.WistiaApi.list_all_projects")
    @patch("app.views.WistiaApi.list_project")
    def test_lesson_detail_view_context(self, mock_list_all_projects, mock_list_project):
        """Test context data in lesson detail view."""
        self.client.login(username=self.teacher_user.username, password="password")

        mock_list_all_projects.return_value = [SimpleNamespace(name="Test Course", id="123")]
        mock_list_project.return_value = [SimpleNamespace(hashed_id="hashed123")]
        
        response = self.client.get(reverse("lesson_detail", args=(self.lesson.pk,)))
        
        self.assertIn('lessons', response.context)
        self.assertIn('sections', response.context)
        self.assertIn('embed_url', response.context)

    def test_course_detail_view(self):
        """Test course detail view."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("course_detail", args=(self.course.pk,)))
        
        self.assertEqual(response.status_code, 200)

    def test_section_create_view(self):
        """Test section creation view."""
        self.client.login(username=self.admin_user.username, password="password")
        
        response = self.client.post(reverse("create_section"), {
            "title": "New Section",
            "course": self.course.pk
        })
        
        self.assertEqual(response.status_code, 302)
    
    def test_section_create_view_form_queryset(self):
        """Test section creation view with form queryset filtering courses by teacher."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("create_section"))

        form = response.context['form']
        self.assertEqual(list(form.fields['course'].queryset), list(Course.objects.filter(teacher=self.teacher)))

    def test_courses_view_teacher(self):
        """Test courses view for teacher."""
        self.teacher_user.is_staff = False
        self.teacher_user.is_superuser = False
        self.teacher_user.save()
        
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("courses"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/courses.html")
    
    def test_courses_view_student(self):
        """Test courses view for student."""
        self.client.login(username=self.student_user.username, password="password")
        
        response = self.client.get(reverse("courses"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/courses.html")
    
    def test_courses_view_admin(self):
        """Test courses view for admin."""
        self.client.login(username=self.admin_user.username, password="password")
        
        response = self.client.get(reverse("courses"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/courses.html")

    def test_section_create_view(self):
        """Test section creation view for teacher."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("create_section"))
        
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("create_section"), {"title": "New Section", "course": self.course.pk})
        self.assertEqual(response.status_code, 302)

    @patch("app.views.WistiaUploadApi.upload_file")
    def test_upload_to_wistia(self, mock_upload_file):
        """Test uploading a file to Wistia."""
        mock_upload_file.return_value = SimpleNamespace(hashed_id="hashed123")
        
        response = upload_to_wistia(self.get_test_video_file())
        
        self.assertEqual(response.hashed_id, "hashed123")
    
    @patch("app.views.WistiaUploadApi.upload_file")
    def test_upload_to_wistia_exception(self, mock_upload_file):
        """Test handling of an exception during Wistia file upload."""
        mock_upload_file.side_effect = Exception("")
        
        with self.assertRaises(Exception):
            response = upload_to_wistia(self.get_test_video_file())

    def test_password_change_view(self):
        """Test password change view."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("password_change"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_change_form.html')

    def test_get_sections_by_course(self):
        """Test fetching sections by course using AJAX."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        response = self.client.get(reverse("get_sections_by_course", args=(self.course.pk,)))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.section.title, loads(response.content)[0]["title"])
    
    @patch("app.views.WistiaApi.list_all_projects")
    def test_lesson_detail_view_get_media_url_error(self, mock_list_all_projects):
        """Test lesson detail view when Wistia API returns an error."""
        self.client.login(username=self.teacher_user.username, password="password")
        
        mock_list_all_projects.return_value = []
        
        with self.assertRaises(ValueError):
            response = self.client.get(reverse("lesson_detail", args=(self.lesson.pk,)))
    
    @patch("app.views.WistiaApi.list_all_projects")
    @patch("app.views.WistiaApi.list_project")
    def test_lesson_detail_view_handles_error(self, mock_list_all_projects, mock_list_project):
        """Test lesson detail view handles error during Wistia API call."""
        self.client.login(username=self.teacher_user.username, password="password")

        mock_list_all_projects.return_value = []

        with self.assertRaises(ValueError):
            response = self.client.get(reverse("lesson_detail", args=(self.lesson.pk,)))
    
    @patch("app.views.WistiaApi.list_all_projects")
    def test_lesson_detail_view_get_media_url_exception(self, mock_list_all_projects):
        """Test lesson detail view handling exception during Wistia API failure."""
        self.client.login(username=self.teacher_user.username, password="password")

        mock_list_all_projects.side_effect = Exception("Wistia API failed")

        response = self.client.get(reverse("lesson_detail", args=(self.lesson.pk,)))
        
        self.assertContains(response, "Error during listing project/s: Wistia API failed")