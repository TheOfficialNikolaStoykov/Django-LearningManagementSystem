# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.validators import FileExtensionValidator

class Teacher(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=100)
    email = models.EmailField()
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def save(self):
        super().save()

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
    degree = models.CharField(max_length=3, choices=DEGREE, default=BACHELOR)
    faculty_id = models.IntegerField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=100)
    email = models.EmailField()
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
    def save(self):
        super().save()

        image = Image.open(self.profile_picture.path)

        if image.height > 300 or image.width > 300:
            output_size = (300, 300)
            image.thumbnail(output_size)
            image.save(self.profile_picture.path)


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    students = models.ManyToManyField(User)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Section(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=300)
    description = models.TextField()
    file = models.FileField(upload_to='media', validators=[FileExtensionValidator( ['mp4'] ) ], null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class News(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=300)
    content = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
    