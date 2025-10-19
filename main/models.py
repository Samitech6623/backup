from django.db import models
from django.db.models import Sum,Avg
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.

class Session(models.Model):
    TERM_CHOICES = [
        ("Term 1", "Term 1"),
        ("Term 2", "Term 2"),
        ("Term 3", "Term 3"),
    ]
    
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    year = models.IntegerField(default=timezone.now().year)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    @property
    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def __str__(self):
        return (f"{self.term} Year {self.year}")

class Management(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='management_profile')
    is_admin_user = models.BooleanField(default=True)

    def __str__(self):
        return  "school admin"

class Parent(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='parent_profile')
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

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name
    
class Class(models.Model):
    name = models.CharField(max_length=50, unique=True)
    class_teacher = models.OneToOneField(
        "Teacher", on_delete=models.SET_NULL, null=True, blank=True, related_name="class_teacher"
    )
    description = models.TextField(blank=True, null=True)
    subjects = models.ManyToManyField(Subject, related_name="classes") 

    @property
    def display_name(self):
        return self.name
    @property
    def total_class_students(self):
        return self.students.count()
    def class_perfomance_summary(self):
        return

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
    
    def exam_summary(self, exam):
       
        results = self.results.filter(exam=exam)
        summary = results.aggregate(total=Sum("score"), average=Avg("score"))
        total = summary["total"] or 0
        average = summary["average"] or 0

        # Fetch the corresponding grade based on the average
        grade_obj = Grade.objects.filter(
            min_score__lte=average, max_score__gte=average
        ).first()

        grade = grade_obj.grade if grade_obj else "-"
        remark = grade_obj.remark if grade_obj else "Ungraded"

        return {
            "total": total,
            "average": round(average, 2),
            "grade": grade,
            "remark": remark,
        }

    
    def total_fees_paid(self):
        return self.fee_payment.filter(status="CONFIRMED").aggregate(total=Sum("amount"))["total"] or 0

    def fee_balance(self, term, year):
        try:
            structure = SchoolFeeStructure.objects.get(
                class_name=self.current_class, term=term, year=year
            )
            required = structure.amount_required
        except SchoolFeeStructure.DoesNotExist:
            required = 0
        return required - self.total_fees_paid()
    
    def __str__(self):
        return (f"{self.first_name} {self.last_name} {self.admission_number}") 
    
class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='teacher_profile')
    teacher_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True) 
    phone = models.CharField(max_length=15)

    
    @property
    def display_name(self):
        return (f"{self.teacher_name}")
    
    def __str__(self):
        return self.teacher_name
    
    def subjects_in_class(self, class_obj):
        return Subject.objects.filter(teaching_class_assignments__teacher=self, teaching_class_assignments__class_assigned=class_obj)
    
    def delete(self, *args, **kwargs):
        # Save reference to the linked user
        linked_user = self.user
        # Delete the Parent record
        super().delete(*args, **kwargs)
        # Delete the linked user too
        if linked_user:
            linked_user.delete()



class TeachingClassAssignment(models.Model):
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE, related_name="teaching_class_assignments")
    class_assigned = models.ForeignKey("Class", on_delete=models.CASCADE, related_name="teaching_class_assignments")
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE, related_name="teaching_class_assignments")

    def __str__(self):
        return f"{self.teacher} teaches {self.subject} in {self.class_assigned}"



class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_payment")
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

    @property
    def display_name(self):
        return f"{self.student} - {self.amount} ({self.receipt_number}) payment"

    def __str__(self):
        return f"{self.student} - {self.amount} ({self.status})"
    

class Exam(models.Model):
    exam_name = models.CharField(max_length=150, blank=False,null=False)
    exam_session = models.ForeignKey(Session,on_delete=models.CASCADE)
    exam_classes = models.ManyToManyField(Class,related_name="exam_classes")

    class Meta:
        unique_together = ("exam_name", "exam_session")  # ✅ valid combo
        verbose_name_plural = "Exams"

    def __str__(self):
        return f"{self.exam_name} ({self.exam_session.term} - {self.exam_session.year})"

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="results")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="exam_details")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade_object = models.ForeignKey(
        'Grade', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="results_with_this_grade"
    )    
    remarks = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Automatically assign grade and remarks based on score
        grade_obj = Grade.objects.filter(min_score__lte=self.score, max_score__gte=self.score).first()
        if grade_obj:
            self.grade_object = grade_obj
        else:
            self.grade_object = None
        super().save(*args, **kwargs)

    def __str__(self):
        grade_str = self.grade_object.grade if self.grade_object else "N/A"

        return f"{self.student} - {self.subject} ({grade_str})"



class SchoolFeeStructure(models.Model):
    class_name = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="fee_structures")
    term = models.CharField(max_length=20)  # e.g. "Term 1"
    year = models.IntegerField()
    amount_required = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def display_name(self):
        return f"{self.class_name} -Term: {self.term} Year:{self.year} fee structure"


    def __str__(self):
        return f"{self.class_name} - {self.term} {self.year} - {self.amount_required}"
    


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    author = models.CharField(max_length=100, blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)

    @property
    def display_name(self):
        return f"{self.title} - {self.created_on.strftime('%Y-%m-%d')} announcement"

    def __str__(self):
        return f"{self.title} - {self.created_on.strftime('%Y-%m-%d')}"


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    location = models.CharField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)

    @property
    def display_name(self):
        return f"{self.name} ({self.date}) event"

    def __str__(self):
        return f"{self.name} ({self.date})"


class Grade(models.Model):
    min_score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2)
    remark = models.CharField(max_length=50)

    class Meta:
        ordering = ['-min_score']

    def clean(self):
        """Ensure min_score is less than max_score."""
        if self.min_score >= self.max_score:
            raise ValidationError(
                'min_score must be strictly less than max_score.'
            )
        # You could also check for negative values if scores must be non-negative
        if self.min_score < 0:
             raise ValidationError('Scores cannot be negative.')

    def save(self, *args, **kwargs):
        if self.grade:
            self.grade = self.grade.upper()
            self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.grade} ({self.min_score}-{self.max_score})"





