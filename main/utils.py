from django.shortcuts import render,redirect,get_object_or_404,reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView,ListView,UpdateView,CreateView,DeleteView
from django.contrib.auth import login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordChangeForm,PasswordResetForm
from .models import Student,Teacher,Parent,Class,SchoolFeeStructure,FeePayment,Announcement,Event,Result,Subject,Exam, Session,Grade
from django.urls import reverse_lazy
from django.db.models import Sum,Count,Avg
from django.utils import timezone
from django.db import transaction  # Import transaction for robust saving

from django.forms import modelformset_factory


from .forms import ParentForm, StudentForm, TeacherForm,ClassForm,FeeStructureForm,FeePaymentForm,ExamSelectionForm, ResultForm
from collections import defaultdict
from decimal import Decimal

def group_student_results(results_qs, students):
    grouped = []
    student_results_map = defaultdict(list)
    class_total = 0

    for result in results_qs:
        student_results_map[result.student_id].append(result)

    for student in students:
        results = student_results_map.get(student.id, [])
        if not results:
            continue
        total = sum(r.score for r in results)
        average = round(total / len(results), 2)
        grade_obj = Grade.objects.filter(min_score__lte=average, max_score__gte=average).first()
        grade = grade_obj.grade if grade_obj else "-"
        remark = grade_obj.remark if grade_obj else "No remark"

        grouped.append({
            "student": student,
            "records": results,
            "total": total,
            "average": average,
            "grade": grade,
            "remark": remark,
        })

    return grouped

def assign_positions(grouped_data):
    grouped_data.sort(key=lambda x: x["average"], reverse=True)
    for idx, data in enumerate(grouped_data, start=1):
        data["position"] = idx
    return grouped_data


def filter_subjects(grouped_data, subjects_taught):
    filtered = []
    for data in grouped_data:
        data["records"] = [r for r in data["records"] if r.subject in subjects_taught]
        if data["records"]:
            filtered.append(data)
    return filtered

def class_score_summary(grouped_data,results_qs):
    totals = [entry["total"] for entry in grouped_data]

    class_mean_score = round(sum(totals) / len(totals), 2) if totals else None
    


        # 2. class_mean_grade: based on class_mean_score

    class_average = results_qs.aggregate(avg=Avg("score"))["avg"]
    class_average = round(class_average, 2) if class_average else None

    if class_average is not None:
        grade_obj = Grade.objects.filter(min_score__lte=class_average, max_score__gte=class_average).first()
        class_mean_grade = grade_obj.grade if grade_obj else "-"
    else:
        class_mean_grade = None
    subject_means_qs = results_qs.values("subject__name").annotate(mean_score=Avg("score"))
    class_subject_mean = { }
    for entry in subject_means_qs:
        subject_name = entry["subject__name"]
        mean_score = round(entry["mean_score"], 2)
        
        # Get grade for the mean score
        grade_obj = Grade.objects.filter(min_score__lte=mean_score, max_score__gte=mean_score).first()
        grade = grade_obj.grade if grade_obj else "-"
        class_subject_mean[subject_name] = {
                    "mean_score": mean_score,
                    "mean_grade": grade,
                }
            

    grouped = {
        "class_mean_score":class_mean_score,
        "class_average":class_average,
    "class_mean_grade":class_mean_grade,
        "class_subjects_mean":class_subject_mean

    }

    return grouped


def subject_results_with_ranks(grouped_data, subjects_taught):
    subjects_data = defaultdict(list)

    # Go through each student's records
    for student_data in grouped_data:
        for result in student_data["records"]:
            if result.subject in subjects_taught:
                subjects_data[result.subject.name].append({
                    "student": result.student,
                    "score": result.score,
                    "grade": result.grade_object.grade,
                    "remark": result.grade_object.remark,
                })

    ranked_subjects = []

    for subject, results in subjects_data.items():
        results = sorted(results, key=lambda x: x["score"], reverse=True)

        for idx, res in enumerate(results, start=1):
            res["rank"] = idx

        mean_score = sum(r["score"] for r in results) / len(results)
        grade_obj = Grade.objects.filter(
            min_score__lte=mean_score,
            max_score__gte=mean_score
        ).first()

        ranked_subjects.append({
            "subject": subject,
            "mean_score": round(mean_score, 2),
            "mean_grade": grade_obj.grade if grade_obj else "N/A",
            "remark": grade_obj.remark if grade_obj else "",
            "records": results,
        })

    return ranked_subjects


def get_or_create_results_for_class(exam, students, subjects):
    for student in students:
        for subject in subjects:
            Result.objects.get_or_create(student=student, subject=subject, exam=exam)
    return Result.objects.filter(exam=exam, student__in=students)

def handle_own_class_results(request, exam, selected_class, students,exam_session):
    subjects = selected_class.subjects.all()
    results = Result.objects.filter(exam=exam, student__in=students)

    expected_count = students.count() * subjects.count()
    if not results.exists() or results.count() < expected_count:
        results = get_or_create_results_for_class(exam, students, subjects)

    ExamResultFormSet = modelformset_factory(Result, form=ResultForm, extra=0)
    formset = ExamResultFormSet(request.POST or None, queryset=results, prefix="own")

    if request.method == "POST" and formset.is_valid():
        try:
            with transaction.atomic():
                formset.save()
            messages.success(request, "✅ My Class grades saved successfully!")

            return redirect(f"{reverse('teacher_students_grades_view')}?session={exam_session.id}&exam={exam.id}&class_selected={selected_class.id}")
           # return redirect ('teacher_students_grades_view')
        except Exception as e:
            messages.error(request, f"❌ Database Error during save: {e}")

    return formset


def handle_other_class_results(request, exam, selected_class, students, subjects_taught,exam_session):
    results = Result.objects.filter(
        exam=exam,
        student__in=students,
        subject__in=subjects_taught
    )

    ExamResultFormSet = modelformset_factory(Result, form=ResultForm, extra=0)
    formset = ExamResultFormSet(request.POST or None, queryset=results, prefix="other")

    if request.method == "POST" and formset.is_valid():
        try:
            with transaction.atomic():
                formset.save()
            messages.success(request, "✅ Grades for other classes updated successfully!")

            return redirect(f"{reverse('teacher_students_grades_view')}?session={exam_session.id}&exam={exam.id}&class_selected={selected_class.id}")

        except Exception as e:
            messages.error(request, f"❌ Database Error during save: {e}")

    return formset

def get_fee_summary(student, term, year):
    # Get the fee structure for the student's current class
    fee_structure = SchoolFeeStructure.objects.filter(
        class_name=student.current_class, term=term, year=year
    ).first()

    amount_required = fee_structure.amount_required if fee_structure else Decimal('0.00')

    # Sum all confirmed payments
    total_paid = FeePayment.objects.filter(
        student=student,
        status="CONFIRMED"
    ).aggregate(total=Sum("amount"))["total"] or Decimal('0.00')

    # Calculate balance
    balance = amount_required - total_paid

    # Determine status
    if balance <= 0:
        status = "Paid in Full" if balance == 0 else "Overpaid"
    elif total_paid == 0:
        status = "Not Paid"
    else:
        status = "Partially Paid"

    return {
        "required": amount_required,
        "paid": total_paid,
        "balance": abs(balance),
        "status": status,
    }

