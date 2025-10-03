from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Parent, Student, Teacher,Class,User,SchoolFeeStructure,FeePayment


class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username" , "password1", "password2"]

class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ["full_name", "phone", "email"]


class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = [ "full_name", "phone","email"]

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
             'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [ "teacher_name" , "email" , "phone" ]

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = '__all__'

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = SchoolFeeStructure
        fields = '__all__'

class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = '__all__'

        widgets = {
            'paid_on': forms.DateInput(attrs={'type':'date'})
        }