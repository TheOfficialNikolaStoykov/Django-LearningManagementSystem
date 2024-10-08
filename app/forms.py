from django.contrib.auth.forms import SetPasswordForm
from django.forms import ModelForm

from .models import Lesson, Student, Teacher


class LessonForm(ModelForm):
    class Meta:
        model = Lesson
        fields = "__all__"
    
    def __init__(self, *args, **kwargs):
        super(LessonForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': 'video/mp4'})


class SetPasswordFormTeacher(SetPasswordForm):
    class Meta:
        model = Teacher
        fields = ['new_password1', 'new_password2']


class SetPasswordFormStudent(SetPasswordForm):
    class Meta:
        model = Student
        fields = ['new_password1', 'new_password2']

