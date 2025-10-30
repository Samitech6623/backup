from django.urls import path
from . import views

urlpatterns = [
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path("teacher/my-classes/", views.my_classes, name="teacher_my_classes"),
     path("teacher/students/", views.teacher_students, name="teacher_students"),
     path("teacher/students/grades/", views.teacher_students_grades_view, name="teacher_students_grades_view"),
     path("teacher/students/grades/edit/", views.teacher_students_grades_edit, name="teacher_students_grades_edit"),
     path("teacher/assignments/", views.page_not_available.as_view(),name="teacher_assignments"),
     path("teacher/messages/",views.page_not_available.as_view(),name="teacher_messages")
]