from django.contrib import admin
from .models import (
    Management, Parent, Class, Student, 
    Teacher, Subject, TeachingClassAssignment, 
    FeePayment, Result, SchoolFeeStructure, 
    Announcement, Event,Session, Exam,Grade

)

# Register all models using the default admin settings

admin.site.register(Management)
admin.site.register(Parent)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(TeachingClassAssignment)
admin.site.register(FeePayment)
admin.site.register(Result)
admin.site.register(SchoolFeeStructure)
admin.site.register(Announcement)
admin.site.register(Event)
admin.site.register(Session)
admin.site.register(Exam)
admin.site.register(Grade)
