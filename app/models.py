from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from PIL import Image


class CustomUser(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=100)
    email = models.EmailField()
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image = Image.open(self.profile_picture.path)

        if image.height > 300 or image.width > 300:
            output_size = (300, 300)
            image.thumbnail(output_size)
            image.save(self.profile_picture.path)


class Student(models.Model):
    ASSOCIATE = 'AS'
    BACHELOR = 'BA'
    MASTER = 'MA'
    PROFESSIONAL = 'PR'
    DOCTORAL = 'PhD'
    DEGREE = [
    ('AS', 'Associate'),
    ('BA', 'Bachelor'),
    ('MA', 'Master'),
    ('PR', 'Professional'),
    ('PhD', 'Doctoral'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    degree = models.CharField(max_length=3, choices=DEGREE, default=BACHELOR)
    faculty_id = models.IntegerField()
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=100)
    email = models.EmailField()
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        image = Image.open(self.profile_picture.path)

        if image.height > 300 or image.width > 300:
            output_size = (300, 300)
            image.thumbnail(output_size)
            image.save(self.profile_picture.path)


class Course(models.Model):
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(Student)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Section(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    file = models.FileField(upload_to='media', validators=[FileExtensionValidator( ['mp4'] ) ], null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    def get_index_in_course(self):
        return list(self.course.lesson_set.order_by('id')).index(self)

class News(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
    