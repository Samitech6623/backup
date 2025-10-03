from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

from django.utils import timezone

# Create your models here.

class Management(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    is_admin_user = models.BooleanField(default=True)

    def __str__(self):
        return  "school admin"

class Parent(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True, null=True, blank=True) 

    @property
    def display_name(self):
        return f"{self.full_name}"
    
    def __str__(self):
        return (f"parent:{self.full_name}")
    def delete(self, *args, **kwargs):
        # Save reference to the linked user
        linked_user = self.user
        # Delete the Parent record
        super().delete(*args, **kwargs)
        # Delete the linked user too
        if linked_user:
            linked_user.delete()
    
class Class(models.Model):
    name = models.CharField(max_length=50, unique=True)
    teacher = models.ForeignKey(
        "Teacher", on_delete=models.SET_NULL, null=True, blank=True, related_name="classes"
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    parent = models.ForeignKey(Parent,on_delete=models.CASCADE,related_name='children')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[
        ('Male', 'Male'),
        ('Female', 'Female')
    ])

    admission_number = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    current_class = models.ForeignKey(
        Class, on_delete=models.SET_NULL, null=True, blank=True, related_name="students"
    )   
    is_active = models.BooleanField(default=True)

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return (f"{self.first_name} {self.last_name} {self.admission_number}") 
    
    def total_fees_paid(self):
        return self.fees.filter(status="CONFIRMED").aggregate(total=Sum("amount"))["total"] or 0

    def fee_balance(self, term, year):
        try:
            structure = SchoolFeeStructure.objects.get(
                class_name=self.current_class, term=term, year=year
            )
            required = structure.amount_required
        except SchoolFeeStructure.DoesNotExist:
            required = 0
        return required - self.total_fees_paid()
    

    
class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    teacher_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True) 
    phone = models.CharField(max_length=15)

    
    @property
    def display_name(self):
        return (f"{self.teacher_name}")
    
    def __str__(self):
        return self.teacher_name
    
    def delete(self, *args, **kwargs):
        # Save reference to the linked user
        linked_user = self.user
        # Delete the Parent record
        super().delete(*args, **kwargs)
        # Delete the linked user too
        if linked_user:
            linked_user.delete()




class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateTimeField(default=timezone.now)
    receipt_number = models.CharField(max_length=50, unique=True)  # M-Pesa receipt
    payment_method = models.CharField(max_length=20, choices=[
        ("MPESA", "M-Pesa"),
        ("BANK", "Bank"),
        ("CASH", "Cash"),
    ], default="MPESA")
    status = models.CharField(max_length=20, choices=[
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("FAILED", "Failed"),
    ], default="PENDING")

    def __str__(self):
        return f"{self.student} - {self.amount} ({self.status})"


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    subject = models.CharField(max_length=100)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2, blank=True)
    term = models.CharField(max_length=50)  # e.g. "Term 1 2025"
    year = models.IntegerField(default=timezone.now().year)
    remarks = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"{self.student} - {self.subject} ({self.grade})"


class SchoolFeeStructure(models.Model):
    class_name = models.CharField(max_length=50)  # e.g. "Grade 1"
    term = models.CharField(max_length=20)  # e.g. "Term 1"
    year = models.IntegerField()
    amount_required = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.class_name} - {self.term} {self.year} - {self.amount_required}"






