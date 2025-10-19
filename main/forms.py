from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Parent, Student, Teacher,Class,User,SchoolFeeStructure,FeePayment, Announcement, Event,Session, Exam, Result,Grade


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

        widgets = {
            "subjects":forms.CheckboxSelectMultiple()
        }

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




class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'

        widgets = {
            'created_on': forms.DateInput(attrs={'type':'date'})
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

        widgets = {
            'date': forms.DateInput(attrs={'type':'date'}),
            'created_on': forms.DateInput(attrs={'type':'date'})
        }


class ExamSelectionForm(forms.Form):
    session = forms.ModelChoiceField(
        queryset=Session.objects.all(),
        label="Select Session",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        label="Select Exam",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    class_selected = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        label="Select Class",
        widget=forms.Select(attrs={"class": "form-control"})
    )

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'subject', 'score', 'remarks']
        
        widgets = {
            'student': forms.HiddenInput(),
            'subject': forms.HiddenInput(),
            'score': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = '__all__'

class ParentPerformanceFilterForm(forms.Form):
    child = forms.ModelChoiceField(queryset=None)
    session = forms.ModelChoiceField(queryset=Session.objects.all())
    exam = forms.ModelChoiceField(queryset=Exam.objects.all())

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent")
        super().__init__(*args, **kwargs)
        self.fields["child"].queryset = Student.objects.filter(parent=parent)