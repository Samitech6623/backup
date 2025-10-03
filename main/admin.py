from django.contrib import admin
from .models import Student,Parent,Teacher,Management

# Register your models here.

admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(Teacher)
admin.site.register(Management)