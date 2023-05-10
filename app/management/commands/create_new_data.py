from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from wystia import WistiaApi, WistiaUploadApi
from app.models import Teacher, Student, Lesson, Course, News, Section
from django.contrib.auth.models import User
import os
from django.core.files import File
from wystia.models import SortBy
from django.core import management
from django.core.management.commands import loaddata


class Command(BaseCommand):

    def delete_database(self):
        path = '../db.sqlite3'
        os.remove(path)


    def delete_migrations(self):
        path = os.path.join(os.path.dirname(__file__), '../../__init__.py')
        print(path)
        for file in os.listdir(directory):
            if file != '__init__.py':
                os.remove(os.path.join(directory, file))


    def create_database(self):
        management.call_command('makemigrations')
        management.call_command('migrate')


    def delete_all_videos(self):
        directory = '/var/media/media/media'
        for file in os.listdir(directory):
            os.remove(os.path.join(directory, file))


    def delete_wystia_videos(self):
        WistiaApi.configure(os.environ['WISTIA_API'])
        projects = WistiaApi.list_all_projects(SortBy.NAME)
        project_ids = [p.hashed_id for p in projects]
        for id in project_ids:
            WistiaApi.delete_project(id)


    def delete_all_objects(self):
        Student.objects.all().delete()
        Teacher.objects.all().delete()
        Course.objects.all().delete()
        Lesson.objects.all().delete()
        News.objects.all().delete()
        Section.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()


    def create_teacher_users(self):
        User.objects.create_user(username='vvelichkov', password='vvelichkovlms123@@@$$$%%%')
        User.objects.create_user(username='itodorova', password='itodorovalms123@@@$$$%%%')
        User.objects.create_user(username='mevgeniev', password='mevgenievlms123@@@$$$%%%')
        User.objects.create_user(username='mstoyanova', password='mstoyanovalms123@@@$$$%%%')
        User.objects.create_user(username='lbalkanski', password='lbalkanskilms123@@@$$$%%%')

    
    def create_student_user(self):
        User.objects.create_user(username='svladov', password='svladovlms123@@@$$$%%%')


    def create_teacher_accounts(self):
        teachers_create_list = [Teacher(first_name='Ventsislav', last_name='Velichkov', date_of_birth='1989-01-24', address='10, ul. Vihren', email='nikola.stoykov666@gmail.com', user=User.objects.get(username='vvelichkov')),
                                Teacher(first_name='Iliyana', last_name='Todorova', date_of_birth='1993-09-21', address='70-72, bul. Cherni vrah', email='nikola.stoykov666@gmail.com', user=User.objects.get(username='itodorova')),
                                Teacher(first_name='Milen', last_name='Evgeniev', date_of_birth='1983-07-31', address='25, ul. Asenova krepost', email='nikola.stoykov666@gmail.com', user=User.objects.get(username='mevgeniev')),
                                Teacher(first_name='Marina', last_name='Stoyanova', date_of_birth='1993-04-04', address='43А, ul. Todor Dzhebarov', email='nikola.stoykov666@gmail.com', user=User.objects.get(username='mstoyanova')),
                                Teacher(first_name='Lyubomir', last_name='Balkanski', date_of_birth='1986-09-04', address='19А, ul. Boris Rumenov', email='nikola.stoykov666@gmail.com', user=User.objects.get(username='lbalkanski'))]

        Teacher.objects.bulk_create(teachers_create_list)


    def create_student_account(self):
        students_create_list = [Student(degree='BA', faculty_id='540029', first_name='Stoyan', last_name='Vladov', date_of_birth='1998-03-12', address='20, ul. Prof. d-r Ivan Stranski', email='nikola.stoykov666@gmail.com', user=User.objects.get(username='svladov'))]
        Student.objects.bulk_create(students_create_list)


    def create_courses(self):
        course_maths = Course.objects.create(name='Mathematics', teacher=Teacher.objects.get(last_name='Velichkov'))
        course_maths.students.set(User.objects.filter(username='svladov'))

        course_econ = Course.objects.create(name='Economics', teacher=Teacher.objects.get(last_name='Todorova'))
        course_econ.students.set(User.objects.filter(username='svladov'))

        course_soft_dev = Course.objects.create(name='Software Development', teacher=Teacher.objects.get(last_name='Evgeniev'))
        course_soft_dev.students.set(User.objects.filter(username='svladov'))

        course_comp_netw = Course.objects.create(name='Computer Networks', teacher=Teacher.objects.get(last_name='Stoyanova'))
        course_comp_netw.students.set(User.objects.filter(username='svladov'))

        course_mob_apps = Course.objects.create(name='Mobile Applications Development', teacher=Teacher.objects.get(last_name='Balkanski'))
        course_mob_apps.students.set(User.objects.filter(username='svladov'))



    def create_sections(self):
        sections_create_list = [Section(title='Algebra'),
                                Section(title='Calculus'),
                                Section(title='Geometry'),
                                Section(title='Probability and Statistics'),
                                Section(title='Set Theory'),
                                Section(title='Trigonometry'),
                                Section(title='Labour Economics'),
                                Section(title='Econometrics'),
                                Section(title='Financial Economics'),
                                Section(title='Health Economics'),
                                Section(title='Macroeconomics'),
                                Section(title='Microeconomics'),
                                Section(title='Introduction to Python'),
                                Section(title='Strings, Lists and Tuples'),
                                Section(title='Dictionaries and Sets'),
                                Section(title='Conditional Execution & Loops'),
                                Section(title='Comprehensions'),
                                Section(title='Functions'),
                                Section(title='Network Basics'),
                                Section(title='TCP/IP Model'),
                                Section(title='OSI Model'),
                                Section(title='Routing'),
                                Section(title='IP Addressing'),
                                Section(title='Network Services'),
                                Section(title='Class and Object'),
                                Section(title='Nested and Inner Class'),
                                Section(title='Kotlin Constructor'),
                                Section(title='Visibility Modifier'),
                                Section(title='Kotlin Inheritance'),
                                Section(title='Abstract Class')]

        Section.objects.bulk_create(sections_create_list)


    def file(self, item):
        lesson = item
        for num in range(1,11):
            with open('/var/media/media/Example_Video.mp4', 'rb') as lesson_file:
                lesson.file.save('Example_Video.mp4', File(lesson_file), save=True)
            lesson.save()


    def create_lessons(self):
        lessons_create_list = [Lesson(title='Algebra', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mathematics'), section=Section.objects.get(title='Algebra')),
                                #Lesson(title='Calculus', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mathematics'), section=Section.objects.get(title='Calculus')),
                                Lesson(title='Geometry', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mathematics'), section=Section.objects.get(title='Geometry')),
                                #Lesson(title='Probability and Statistics', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mathematics'), section=Section.objects.get(title='Probability and Statistics')),
                                #Lesson(title='Set Theory', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mathematics'), section=Section.objects.get(title='Set Theory')),
                                #Lesson(title='Trigonometry', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mathematics'), section=Section.objects.get(title='Trigonometry')),
                                Lesson(title='Labour Economics', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Economics'), section=Section.objects.get(title='Labour Economics')),
                                #Lesson(title='Econometrics', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Economics'), section=Section.objects.get(title='Econometrics')),
                                #Lesson(title='Financial Economics', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Economics'), section=Section.objects.get(title='Financial Economics')),
                                #Lesson(title='Health Economics', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Economics'), section=Section.objects.get(title='Health Economics')),
                                Lesson(title='Macroeconomics', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Economics'), section=Section.objects.get(title='Macroeconomics')),
                                #Lesson(title='Microeconomics', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Economics'), section=Section.objects.get(title='Microeconomics')),
                                Lesson(title='Introduction to Python', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Software Development'), section=Section.objects.get(title='Introduction to Python')),
                                #Lesson(title='Strings, Lists and Tuples', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Software Development'), section=Section.objects.get(title='Strings, Lists and Tuples')),
                                #Lesson(title='Dictionaries and Sets', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Software Development'), section=Section.objects.get(title='Dictionaries and Sets')),
                                #Lesson(title='Conditional Execution & Loops', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Software Development'), section=Section.objects.get(title='Conditional Execution & Loops')),
                                Lesson(title='Comprehensions', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Software Development'), section=Section.objects.get(title='Comprehensions')),
                                #Lesson(title='Functions', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Software Development'), section=Section.objects.get(title='Functions')),
                                Lesson(title='Network Basics', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Computer Networks'), section=Section.objects.get(title='Network Basics')),
                                #Lesson(title='TCP/IP Model', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Computer Networks'), section=Section.objects.get(title='TCP/IP Model')),
                                #Lesson(title='OSI Model', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Computer Networks'), section=Section.objects.get(title='OSI Model')),
                                #Lesson(title='Routing', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Computer Networks'), section=Section.objects.get(title='Routing')),
                                Lesson(title='IP Addressing', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Computer Networks'), section=Section.objects.get(title='IP Addressing')),
                                #Lesson(title='Network Services', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Computer Networks'), section=Section.objects.get(title='Network Services')),
                                Lesson(title='Class and Object', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mobile Applications Development'), section=Section.objects.get(title='Class and Object')),
                                #Lesson(title='Nested and Inner Class', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mobile Applications Developments'), section=Section.objects.get(title='Nested and Inner Class')),
                                Lesson(title='Kotlin Constructor', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mobile Applications Development'), section=Section.objects.get(title='Kotlin Constructor'))]
                                #Lesson(title='Visibility Modifier', description='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque non quam et nulla euismod tristique pharetra sed nunc. Morbi ut faucibus quam, eget euismod neque. Nunc dictum, nunc rhoncus vulputate efficitur, felis metus fringilla velit, non gravida lacus metus id leo. Nullam rhoncus erat at lorem tempus tincidunt. Pellentesque semper sed orci eu efficitur. Cras bibendum, dolor eget feugiat iaculis, purus metus congue velit, nec laoreet libero quam non neque.', course=Course.objects.get(name='Mobile Applications Developments'), section=Section.objects.get(title='Visibility Modifier'))]

        for item in lessons_create_list:
            self.file(item)


    def upload_to_wistia(self):
        WistiaApi.configure(os.environ['WISTIA_API'])
        full_path = '/var/media/media/Example_Video.mp4'
        courses_names = Course.objects.all().values('name')
        courses_names_list = [u['name'] for u in courses_names]

        for name in courses_names_list:
            project = WistiaApi.create_project(project_name=name, public=1)

        projects = WistiaApi.list_all_projects(SortBy.NAME)
        project_ids = [p.hashed_id for p in projects]
        for id in project_ids:
            file_1 = WistiaUploadApi.upload_file(file_path=full_path, project_id=id)
            file_2 = WistiaUploadApi.upload_file(file_path=full_path, project_id=id)



    def create_news(self):
        news_create_list = [News(title='Proin faucibus vel sem quis consequat', content='In bibendum, purus eu commodo semper, ante tellus vestibulum tellus, sed euismod orci purus lobortis risus. Curabitur cursus eu lectus vel blandit. Proin faucibus vel sem quis consequat. Aliquam erat volutpat. Quisque consectetur nec mauris et tincidunt. Praesent aliquet, ipsum ac lacinia iaculis, dui nibh elementum nisl, tincidunt efficitur tortor magna eu ligula. Proin a mi sagittis, rutrum felis vitae, tempor augue. Nulla quis neque pellentesque, cursus urna ac, faucibus nibh. Suspendisse gravida interdum quam, eget luctus erat rutrum in. Sed sed sapien fermentum, accumsan nisi a, convallis felis. Sed vestibulum ligula non euismod porttitor. Proin ligula mauris, vehicula eget risus congue, feugiat laoreet ante. Proin et libero aliquet, pretium eros ac, rutrum quam. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nunc arcu lacus, fermentum ultricies sem et, fermentum porta sem.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='Nullam at sodales sem, ac dictum metus. Fusce elementum ante a urna placerat, vitae lobortis elit bibendum', content='Morbi dictum pulvinar nisl, ut lobortis mi ullamcorper ut. Proin pellentesque ultricies tincidunt. Cras varius luctus sem, sagittis rhoncus arcu consectetur eu. Ut faucibus ligula sit amet tincidunt mattis. Donec eu tincidunt nibh, nec fringilla nisi. Vivamus porttitor nunc neque, a mattis erat volutpat quis. Curabitur ornare sem nisi, a malesuada nisl fringilla eget. Pellentesque id ornare odio, tempor commodo dui. Phasellus tristique nibh ex. Pellentesque tristique egestas risus sed luctus. Proin elementum in neque non fringilla.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='Proin aliquam lectus eu porttitor euismod', content='Quisque quis libero a lectus molestie congue. Morbi tristique quam imperdiet, aliquet mi posuere, rutrum elit. Sed nec dui vitae felis laoreet luctus ac sit amet nulla. Mauris euismod turpis vitae consectetur gravida. Vivamus vitae sapien at lacus convallis sollicitudin eu et velit. Vestibulum at ipsum rhoncus, dictum velit id, elementum sapien. Ut eu tempor ante. Vestibulum risus ante, laoreet quis nisl ut, malesuada ullamcorper nunc.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='Nunc dapibus odio eu turpis sollicitudin ultricies', content='Ut malesuada sed nunc ac ornare. Curabitur ut molestie nisl, at tincidunt purus. In hac habitasse platea dictumst. Sed rutrum nisl ac odio ornare viverra. Quisque egestas convallis ante eget ultricies. Proin blandit diam quis elit pretium aliquet. Quisque elementum pulvinar sapien id feugiat. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Morbi sit amet dictum massa, non dignissim enim. In nec ligula at risus molestie imperdiet sed at nisl. Vestibulum at ligula posuere, iaculis velit eu, porta nunc. Fusce augue enim, consectetur vel elit vestibulum, dapibus fringilla tellus. Proin pellentesque justo dui, nec fermentum ligula aliquam ac. Maecenas euismod enim enim, ornare eleifend augue molestie ac. In turpis odio, eleifend eu tristique ac, pharetra a ante.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='Maecenas consequat eget erat at pellentesque', content='Phasellus gravida quam et arcu malesuada imperdiet. Integer vitae accumsan risus. Phasellus tempus iaculis eros at faucibus. Vivamus ultrices euismod mi, sit amet semper tellus malesuada vitae. Nulla ullamcorper tellus vel augue suscipit efficitur non eget turpis. In hac habitasse platea dictumst. Morbi vulputate eros ac sapien volutpat, vitae tincidunt erat lobortis. Sed porta sem luctus augue commodo vehicula. Mauris lacinia mattis sem, eu placerat metus mollis nec. Morbi ultricies orci odio, in dapibus orci molestie porttitor. Vestibulum nec semper magna. Pellentesque gravida porta congue. Sed porta felis eget dui lacinia, eget vehicula diam tempus. Suspendisse neque tortor, tempor sit amet nisi vel, ultrices hendrerit mi.', date_created='2023-04-12', posted_by=User.objects.get(username='mstoyanova')),
                            News(title='Aliquam varius ipsum eget ipsum pharetra vulputate', content='Nulla convallis finibus lacus, vitae rutrum urna. Etiam tempus ante nunc, a semper augue lacinia auctor. Suspendisse potenti. Phasellus eu elit nec nulla elementum facilisis. Donec vestibulum congue ligula eget egestas. Praesent rhoncus ultricies lectus, et maximus lectus imperdiet id. Etiam mollis vitae elit eget egestas. Duis rutrum sagittis eros quis efficitur. Cras nec tellus non sem iaculis pharetra. Praesent dignissim semper mattis. Vivamus quis tincidunt felis. Maecenas augue tellus, tempor id ante at, hendrerit dignissim arcu.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='Sed magna eros, mattis ac tempor eu, interdum at nulla', content='Maecenas porta bibendum lacus ac lobortis. Curabitur quis ullamcorper est. Nullam tempor, nisi vitae dictum venenatis, ante nulla sodales justo, id ornare erat est id elit. Donec vitae scelerisque ipsum. Vestibulum sollicitudin semper sodales. Praesent posuere ultrices sodales. Fusce a tortor sed eros consequat euismod. Praesent et tristique turpis. Nam sit amet purus varius, scelerisque justo quis, volutpat purus. Aenean quis rhoncus tortor. Phasellus venenatis odio vel nisl aliquet gravida. Curabitur id diam a lectus molestie ornare. Phasellus sed tincidunt nulla. Suspendisse ipsum est, elementum ut molestie eget, consectetur ac nibh. Quisque lacinia eget sem id mollis. Suspendisse ut pretium enim, vel faucibus erat.', date_created='2023-04-12', posted_by=User.objects.get(username='mstoyanova')),
                            News(title='Proin mattis magna vel aliquam rutrum', content='Donec ultrices nulla eget nisi faucibus, at laoreet tellus feugiat. Proin eget enim condimentum, tempus elit ac, porttitor felis. Mauris nec iaculis nisl. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris dignissim dui sed suscipit pellentesque. Suspendisse non sapien vel neque rhoncus finibus ac sed diam. Aliquam consequat odio vitae nisi varius mollis.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='Curabitur elementum libero eget enim bibendum dignissim', content='Aliquam id turpis ac nibh convallis consectetur id ac justo. Nulla lobortis ullamcorper tincidunt. Pellentesque tortor ipsum, commodo id mattis et, ullamcorper sit amet justo. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Curabitur vitae lorem vel sapien vestibulum pretium. Proin commodo tortor a massa volutpat, id feugiat felis consectetur. Sed diam dui, maximus vitae vulputate vel, auctor at nisl. Vivamus pellentesque sed elit nec venenatis. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.', date_created='2023-04-12', posted_by=User.objects.get(username='itodorova')),
                            News(title='Nunc quis ligula in magna lacinia ultricies', content='Praesent eu nisl fringilla, ornare est non, congue elit. Donec id mi semper, aliquam urna vitae, posuere sapien. Donec at nibh at purus malesuada varius id et augue. Praesent mattis tempor bibendum. Nunc sit amet turpis maximus augue tempor dignissim. Aenean nulla ipsum, vehicula at pharetra vel, bibendum ut quam. Etiam sed urna eget arcu facilisis feugiat at eget metus. Maecenas sit amet risus dui.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='Vestibulum volutpat ex sed scelerisque mattis', content='Etiam elit sapien, luctus vitae nulla at, ultricies pharetra libero. In volutpat sem ut condimentum congue. Pellentesque ut justo arcu. Aenean suscipit lectus finibus elit egestas, non consequat est ullamcorper. Vivamus in odio consequat, pellentesque eros sit amet, ultricies odio. Nunc risus turpis, sagittis eget tellus vitae, luctus fringilla lectus. Curabitur placerat facilisis urna, eu rutrum purus suscipit tempor. Quisque et enim sit amet ligula viverra blandit. Suspendisse a euismod velit. In blandit porttitor tincidunt. Praesent aliquam condimentum orci a accumsan. Praesent semper ut lacus vitae maximus.', date_created='2023-04-12', posted_by=User.objects.get(username='itodorova')),
                            News(title='Integer molestie volutpat sodales', content='Quisque ac justo mauris. Quisque molestie mauris elit, nec consequat lorem convallis nec. Fusce eleifend ac nibh a posuere. Vivamus tempus suscipit mauris vitae mattis. Suspendisse facilisis velit non lobortis dapibus. Suspendisse dignissim at justo et tristique. Phasellus vel consequat tortor. Vivamus pellentesque elit non libero pretium varius. Phasellus leo mi, egestas quis scelerisque et, scelerisque non massa. Nullam euismod, diam ut venenatis vehicula, lorem sapien varius nisl, et dictum metus tellus id libero. Fusce facilisis, massa in tempor volutpat, risus nulla faucibus lorem, vitae faucibus sapien purus at ligula.', date_created='2023-04-12', posted_by=User.objects.get(username='mevgeniev')),
                            News(title='Quisque tristique consectetur sapien', content='Quisque malesuada eros porta nibh porttitor, sed efficitur augue condimentum. Etiam placerat nulla erat, nec ultricies odio ultricies ut. Nullam rhoncus ultricies lacus, vitae pretium odio. Aliquam ut risus vel tortor dictum ullamcorper ut feugiat nulla. Integer porta dui eu vulputate porta. Nulla mollis non sem vel volutpat. Vestibulum vel lorem tellus. Nunc scelerisque tellus non massa ornare placerat. Aliquam vulputate est commodo nulla dictum, sit amet semper ligula cursus. Aenean pellentesque neque quis risus interdum consectetur. Quisque elementum libero diam, at luctus nibh venenatis sed. Ut ultrices vel magna ut aliquam. Aliquam vitae varius tellus.', date_created='2023-04-12', posted_by=User.objects.get(username='mevgeniev')),
                            News(title='Donec molestie ex eget ligula semper', content='Nullam molestie eleifend quam non blandit. Suspendisse potenti. Nulla orci lorem, molestie vel mauris a, viverra convallis est. In id quam elit. Quisque in lobortis orci. Donec et euismod nibh. Duis non imperdiet elit. Interdum et malesuada fames ac ante ipsum primis in faucibus. Integer a dui nisi. Vestibulum eu velit orci. Proin suscipit tempus vulputate.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='In bibendum nisl non massa aliquet, a congue turpis venenatis', content='In consectetur odio at nisi suscipit, eget cursus erat commodo. Proin eu posuere lorem. Morbi vel sapien sed orci cursus varius. Donec condimentum auctor nisi et volutpat. Quisque vestibulum nunc leo. Vivamus lacinia sem vitae odio maximus aliquet. Nam lacinia, libero sit amet lacinia scelerisque, nisi libero porttitor magna, fermentum convallis leo nisi ac ipsum. Aenean sit amet ultricies sapien. Maecenas tincidunt urna egestas scelerisque pretium.', date_created='2023-04-12', posted_by=User.objects.get(username='vvelichkov')),
                            News(title='Quisque mollis sem enim', content='Aliquam vestibulum gravida lobortis. Integer consectetur in ex quis condimentum. Donec id nisi pulvinar, rutrum magna a, volutpat enim. Nunc dictum luctus sem, vel euismod massa tempor vitae. Suspendisse potenti. Aliquam erat volutpat. Donec elementum egestas magna at ornare. Cras porta luctus magna nec rutrum. Quisque pellentesque gravida dui ac fermentum. Proin egestas, augue a mollis finibus, sapien leo pellentesque nulla, et consectetur leo massa scelerisque diam. Proin ipsum turpis, lacinia vitae tortor id, semper pulvinar dui. Etiam bibendum leo leo, eget consectetur quam auctor et. Cras dignissim placerat arcu, non malesuada nisi malesuada nec. Vivamus eget volutpat neque, in rhoncus mauris. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae.', date_created='2023-04-12', posted_by=User.objects.get(username='lbalkanski'))]

        News.objects.bulk_create(news_create_list)


    def create_groups(self):
        teachers_group_create = Group.objects.create(name='Teachers')
        students_group_create = Group.objects.create(name='Students')


    def add_users_to_groups(self):
        teachers_group = Group.objects.get(name='Teachers')
        students_group = Group.objects.get(name='Students')
        teacher_users = User.objects.all().exclude(username='svladov')
        student_user = User.objects.get(username='svladov')

        for user in teacher_users:
            user.groups.add(teachers_group)

        student_user.groups.add(students_group)


    def assign_permissions(self):
        teachers_group = Group.objects.get(name='Teachers')
        add_lesson = Permission.objects.get(codename='add_lesson')
        delete_lesson = Permission.objects.get(codename='delete_lesson')
        add_section = Permission.objects.get(codename='add_section')
        delete_section = Permission.objects.get(codename='delete_section')
        add_news = Permission.objects.get(codename='add_news')
        teachers_group.permissions.add(add_lesson)
        teachers_group.permissions.add(delete_lesson)
        teachers_group.permissions.add(add_section)
        teachers_group.permissions.add(delete_section)
        teachers_group.permissions.add(add_news)


    def handle(self, *args, **options):
        self.delete_migrations()
        self.delete_database()
        self.create_database()
        self.delete_all_videos()
        self.delete_wystia_videos()
        self.delete_all_objects()
        self.create_teacher_users()
        self.create_student_user()
        self.create_teacher_accounts()
        self.create_student_account()
        self.create_courses()
        self.create_sections()
        self.create_lessons()
        self.upload_to_wistia()
        self.create_news()
        self.create_groups()
        self.add_users_to_groups()
        self.assign_permissions()


