from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import Course, CustomUser, Lesson, News, Section, Student, Teacher


class ViewsTestCase(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password")
        self.teacher_user = CustomUser.objects.create_user(username="teacher", password="teacherpassword", is_teacher=True)
        self.student_user = CustomUser.objects.create_user(username="student", password="studentpassword", is_student=True)
        self.test_user_admin = CustomUser.objects.create_superuser(username="test_user_admin", password="password")

        self.user.user_permissions.add(Permission.objects.get(codename="add_news"))
        self.user.user_permissions.add(Permission.objects.get(codename="add_lesson"))
        self.user.save()

        # Assign lesson creation permission to teacher user
        self.teacher_user.user_permissions.add(Permission.objects.get(codename="add_lesson"))
        self.teacher_user.save()

        self.teacher = Teacher.objects.create(user=self.teacher_user, first_name="Teacher", last_name="User", date_of_birth="1990-01-01", address="123 St", email="teacher@example.com")
        self.student = Student.objects.create(user=self.student_user, first_name="Student", last_name="User", date_of_birth="2000-01-01", address="456 St", email="student@example.com", faculty_id=123)

        self.course = Course.objects.create(name="Test Course", teacher=self.teacher)
        self.news = News.objects.create(title="Test News", content="News Content", posted_by=self.user)
        self.lesson = Lesson.objects.create(title="Test Lesson", description="Lesson Description", course=self.course, section=Section.objects.create(title="Section 1", course=self.course))
        
    def test_index_view_as_teacher(self):
        self.client.login(username="teacher", password="teacherpassword")
        
        response = self.client.get(reverse("index"))
        
        self.assertEqual(response.status_code, 200)

    def test_index_view_as_student(self):
        self.client.login(username="student", password="studentpassword")
        
        response = self.client.get(reverse("index"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No courses available at the moment.")  # Depending on actual content

    def test_index_view_as_superuser(self):
        self.client.login(username="test_user_admin", password="password")
        
        response = self.client.get(reverse("index"))
        
        self.assertEqual(response.status_code, 200)

    def test_news_create_view_permission(self):
        # Log in without permission
        self.client.login(username="testuser", password="password")
        
        response = self.client.get(reverse("post_news"))
        
        self.assertEqual(response.status_code, 403)
    
    @patch("app.views.upload_to_wistia")  # Mock Wistia upload API
    def test_lesson_create_view(self, mock_wistia_upload):
        self.client.login(username="test_user_admin", password="password")
        
        # Simulate POST request to create lesson
        response = self.client.post(reverse("create_lesson"), {
            "title": "Test Lesson",
            "description": "Lesson Description",
            "course": self.course.pk,
            "section": Section.objects.create(title="New Section", course=self.course).pk
        })
        
        self.assertEqual(response.status_code, 302)  # Redirection after successful creation
        mock_wistia_upload.assert_called_once()  # Verify Wistia upload is called
    
    def test_admin_profile_view(self):
        self.client.login(username="test_user_admin", password="password")
        
        response = self.client.get(reverse("profile_admin"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app/profile_admin.html")
    
    def test_course_detail_view(self):
        self.client.login(username="teacher", password="teacherpassword")
        
        response = self.client.get(reverse("course_detail", args=(self.course.pk,)))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)
        self.assertContains(response, "Test Lesson")  # Assuming the lesson created earlier is shown

    def test_lesson_create_view_permission(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("create_lesson"))
        
        self.assertEqual(response.status_code, 403)
    
    @patch("app.views.WistiaApi.list_all_projects")
    @patch("app.views.WistiaApi.list_project")
    def test_lesson_detail_view_with_wistia(self, mock_list_project, mock_list_all_projects):
        mock_list_all_projects.return_value = [SimpleNamespace(name="Test Course", id="123")]
        mock_list_project.return_value = [SimpleNamespace(hashed_id="hashed123")]
        
        self.client.login(username="teacher", password="teacherpassword")
        
        response = self.client.get(reverse("lesson_detail", args=(self.lesson.pk,)))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Lesson")
        self.assertContains(response, "wistia_async_hashed123")
    
    def test_section_create_view(self):
        self.client.login(username="test_user_admin", password="password")
        
        response = self.client.post(reverse("create_section"), {
            "title": "New Section",
            "course": self.course.pk
        })
        
        self.assertEqual(response.status_code, 302)  # Redirection after successful creation
        self.assertTrue(Section.objects.filter(title="New Section").exists())

    def test_admin_profile_view(self):
        self.client.login(username="test_user_admin", password="password")
        
        response = self.client.get(reverse("profile_admin"))
        
        self.assertEqual(response.status_code, 200)

    def test_teacher_profile_view(self):
        self.client.login(username="teacher", password="teacherpassword")
        
        response = self.client.get(reverse("profile_teacher"))
        
        self.assertEqual(response.status_code, 200)

    def test_student_profile_view(self):
        self.client.login(username="student", password="studentpassword")
        
        response = self.client.get(reverse("profile_student"))
        
        self.assertEqual(response.status_code, 200)

    @patch("app.views.WistiaApi.list_all_projects")
    @patch("app.views.WistiaApi.list_project")
    def test_lesson_detail_view(self, mock_list_project, mock_list_all_projects):
        mock_list_all_projects.return_value = [SimpleNamespace(name="Test Course", id="123")]
        mock_list_project.return_value = [SimpleNamespace(hashed_id="12123")]

        self.client.login(username="testuser", password="password")
        
        response = self.client.get(reverse("lesson_detail", args=(self.lesson.pk,)))
        
        self.assertEqual(response.status_code, 200)

    def test_news_detail_view(self):
        self.client.login(username="testuser", password="password")
        
        response = self.client.get(reverse("news_detail", args=(self.news.pk,)))
        
        self.assertEqual(response.status_code, 200)

    def test_course_detail_view(self):
        self.client.login(username="testuser", password="password")
        
        response = self.client.get(reverse("course_detail", args=(self.course.pk,)))
        
        self.assertEqual(response.status_code, 200)

    def test_password_change_view(self):
        self.client.login(username="testuser", password="password")
        
        response = self.client.get(reverse("password_change"))
        
        self.assertEqual(response.status_code, 200)

    def test_courses_view(self):
        self.client.login(username="teacher", password="teacherpassword")
        
        response = self.client.get(reverse("courses"))
        
        self.assertEqual(response.status_code, 200)

    def test_section_create_view(self):
        self.client.login(username="test_user_admin", password="password")
        
        response = self.client.get(reverse("create_section"))
        
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse("create_section"), {"title": "New Section", "course": self.course.pk})
        
        self.assertEqual(response.status_code, 302)