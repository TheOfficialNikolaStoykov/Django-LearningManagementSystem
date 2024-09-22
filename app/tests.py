from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
import os

from .models import Course, CustomUser, Lesson, News, Section, Student, Teacher
from .views import upload_to_wistia
from django.conf import settings
from django.core.files import File


class ViewsTestCase(TestCase):

    def setUp(self):
        self.teacher_user = CustomUser.objects.create_user(username="test_teacher", password="password", is_teacher=True)
        self.student_user = CustomUser.objects.create_user(username="test_student", password="password", is_student=True)
        self.admin_user = CustomUser.objects.create_superuser(username="test_admin_user", password="password")

        self.teacher_user.user_permissions.add(Permission.objects.get(codename="add_lesson"))
        self.teacher_user.user_permissions.add(Permission.objects.get(codename="add_section"))
        self.teacher_user.save()

        self.teacher = Teacher.objects.create(user=self.teacher_user, first_name="Teacher", last_name="User", date_of_birth="1990-01-01", address="123 St", email="teacher@example.com")
        self.student = Student.objects.create(user=self.student_user, first_name="Student", last_name="User", date_of_birth="2000-01-01", address="456 St", email="student@example.com", faculty_id=123)

        self.course = Course.objects.create(name="Test Course", teacher=self.teacher)
        self.news = News.objects.create(title="Test News", content="News Content", posted_by=self.teacher_user)
        self.lesson = Lesson.objects.create(title="Test Lesson", description="Lesson Description", course=self.course, section=Section.objects.create(title="Section 1", course=self.course))

    def get_test_image(self):
        """Helper function to reference the existing image from the media directory."""
        image_path = os.path.join(settings.MEDIA_ROOT, 'test_image.jpg')
        return SimpleUploadedFile(name='test_image.jpg', content=open(image_path, 'rb').read(), content_type='image/jpeg')
    
    def get_test_video(self):
        """Helper function to reference the existing video from the media directory."""
        video_path = os.path.join(settings.MEDIA_ROOT, 'Example_Video.mp4')
        with open(video_path, 'rb') as f:
            return File(f, name='Example_Video.mp4')

    def test_custom_user_str(self):
        self.assertEqual(str(self.teacher_user), "test_teacher")
        self.assertEqual(str(self.student_user), "test_student")

    def test_teacher_profile_picture_resize(self):
        self.teacher.profile_picture = self.get_test_image()
        self.teacher.save()

        self.assertTrue(os.path.exists(self.teacher.profile_picture.path))

        image = Image.open(self.teacher.profile_picture.path)
        self.assertTrue(image.width <= 300)
        self.assertTrue(image.height <= 300)

    def test_student_profile_picture_resize(self):
        self.student.profile_picture = self.get_test_image()
        self.student.save()

        self.assertTrue(os.path.exists(self.student.profile_picture.path))

        image = Image.open(self.student.profile_picture.path)
        self.assertTrue(image.width <= 300)
        self.assertTrue(image.height <= 300)

    def test_anonymous_user_redirect(self):
        response = self.client.get(reverse("index"))
        self.assertRedirects(response, f'{reverse("login")}?next=/app/')

    def test_index_view_as_teacher(self):
        self.client.login(username=self.teacher_user.username, password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_as_student(self):
        self.client.login(username=self.student_user.username, password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_as_superuser(self):
        self.client.login(username=self.admin_user.username, password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_news_create_view_permission(self):
        self.client.login(username=self.student_user.username, password="password")
        response = self.client.get(reverse("post_news"))
        self.assertEqual(response.status_code, 403)

    def test_news_create_view_with_permission(self):
        self.client.login(username=self.teacher_user.username, password="password")
        self.teacher_user.user_permissions.add(Permission.objects.get(codename="add_news"))
        response = self.client.post(reverse("post_news"), {"title": "News Title", "content": "Some content"})
        self.assertRedirects(response, reverse("index"))

    @patch("app.views.upload_to_wistia")
    def test_lesson_create_view(self, mock_wistia_upload):
        self.client.login(username=self.teacher_user.username, password="password")
        response = self.client.post(reverse("create_lesson"), {
            "title": "Test Lesson",
            "description": "Lesson Description",
            "course": self.course.pk,
            "section": Section.objects.create(title="New Section", course=self.course).pk
        })
        self.assertEqual(response.status_code, 200)

    def test_admin_profile_view(self):
        self.client.login(username=self.admin_user.username, password="password")
        response = self.client.get(reverse("profile_admin"))
        self.assertEqual(response.status_code, 200)

    def test_teacher_profile_view(self):
        self.client.login(username=self.teacher_user.username, password="password")
        response = self.client.get(reverse("profile_teacher"))
        self.assertEqual(response.status_code, 200)

    def test_student_profile_view(self):
        self.client.login(username=self.student_user.username, password="password")
        response = self.client.get(reverse("profile_student"))
        self.assertEqual(response.status_code, 200)

    @patch("app.views.WistiaApi.list_all_projects")
    @patch("app.views.WistiaApi.list_project")
    def test_lesson_detail_view_with_wistia(self, mock_list_project, mock_list_all_projects):
        mock_list_all_projects.return_value = [SimpleNamespace(name="Test Course", id="123")]
        mock_list_project.return_value = [SimpleNamespace(hashed_id="hashed123")]
        self.client.login(username=self.teacher_user.username, password="password")
        response = self.client.get(reverse("lesson_detail", args=(self.lesson.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "fast.wistia.com")

    def test_course_detail_view(self):
        self.client.login(username=self.teacher_user.username, password="password")
        response = self.client.get(reverse("course_detail", args=(self.course.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_section_create_view(self):
        self.client.login(username=self.admin_user.username, password="password")
        response = self.client.post(reverse("create_section"), {
            "title": "New Section",
            "course": self.course.pk
        })
        self.assertEqual(response.status_code, 302)

    def test_password_change_view(self):
        self.client.login(username=self.teacher_user.username, password="password")
        response = self.client.get(reverse("password_change"))
        self.assertEqual(response.status_code, 200)

    def test_courses_view(self):
        self.client.login(username=self.teacher_user.username, password="password")
        response = self.client.get(reverse("courses"))
        self.assertEqual(response.status_code, 200)

    def test_section_create_view(self):
        self.client.login(username=self.teacher_user.username, password="password")
        response = self.client.get(reverse("create_section"))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse("create_section"), {"title": "New Section", "course": self.course.pk})
        self.assertEqual(response.status_code, 302)

    @patch("app.views.WistiaUploadApi.upload_file")
    def test_upload_to_wistia(self, mock_upload_file):
        mock_upload_file.return_value = SimpleNamespace(hashed_id="hashed123")
        response = upload_to_wistia(self.get_test_video())
        self.assertEqual(response.hashed_id, "hashed123")
