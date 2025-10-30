from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login,logout
from django.contrib import messages
from django.views.generic import TemplateView,ListView,UpdateView,CreateView,DeleteView
from django.contrib.auth.models import User
from main.models import Student,Teacher,Parent,ClassRoom,Result,Subject,Exam, Session,Grade
from django.urls import reverse_lazy
from django.db.models import Sum,Count,Avg
from django.utils import timezone
from django.db import transaction  # Import transaction for robust saving
from main.utils import (group_student_results, assign_positions,filter_subjects,class_score_summary,handle_own_class_results,
                    handle_other_class_results,subject_results_with_ranks,get_fee_summary,child_latest_exam_summary)

from django.forms import modelformset_factory


from main.forms import (ParentForm, StudentForm, TeacherForm,ClassRoomForm,FeeStructureForm,
                    FeePaymentForm,ExamSelectionForm, ResultForm,ParentPerformanceFilterForm,
                    FeeStructureSelectionForm)
# Create your views here.
@login_required
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    classes_assigned = teacher.teaching_class_assignments.select_related("class_assigned", "subject")
    classes_assigned_count = classes_assigned.count()
    try:
        class_teacher_of = ClassRoom.objects.get(class_teacher=teacher)
    except ClassRoom.DoesNotExist:
        class_teacher_of = None
    class_ids = classes_assigned.values_list("class_assigned", flat=True)
    total_students_subjects_assigned = Student.objects.filter(current_class__in=class_ids).count() 
    if class_teacher_of:
        total_students_my_class = Student.objects.filter(current_class=class_teacher_of).count()
    else:
        total_students_my_class = 0
    pending_grades = 'N/A'
    context = {
        "classes_assigned":classes_assigned,
        "class_teacher_of":class_teacher_of,
        "total_students_subjects_assigned":total_students_subjects_assigned,
        "total_students_my_class":total_students_my_class,
        "total_subjects_assigned":classes_assigned_count,
        "pending_grades":pending_grades

    }
    return render(request, 'teachers/teacher_dashboard.html',context)


@login_required
def my_classes(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    # Classes where the teacher is subject teacher
    teaching_assignments = teacher.teaching_class_assignments.select_related("class_assigned", "subject")

    # Classes where the teacher is class teacher (homeroom)
    homeroom_class = ClassRoom.objects.filter(class_teacher=teacher).first()

    context = {
        "teaching_assignments": teaching_assignments,
        "homeroom_class": homeroom_class,
    }
    return render(request, "teachers/teacher_my_classes.html", context)

@login_required
def teacher_students(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    # Check if this teacher is a class teacher
    try:
        class_teacher_of = ClassRoom.objects.get(class_teacher=teacher)
        # Prefetch parent info so we avoid too many queries
        students = Student.objects.filter(current_class=class_teacher_of).select_related("parent")
    except ClassRoom.DoesNotExist:
        class_teacher_of = None
        students = Student.objects.none()  # empty queryset

    context = {
        "students": students,
        "class_teacher_of": class_teacher_of,
    }
    return render(request, "teachers/teacher_students_page.html", context)


@login_required
def teacher_students_grades_view(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    selection_form = ExamSelectionForm(request.GET or None)

    context = {
        "selection_form": selection_form,
        "own_class_results": [],
        "other_class_results": [],
        "selected_class": None,
        "class_teacher_class": ClassRoom.objects.filter(class_teacher=teacher).first(),
        "class_mean_score":None,
        "class_mean_grade":None,
        "class_average":None,
        "class_subjects_mean":None
    }

    if not selection_form.is_valid():
        return render(request, "teachers/teacher_students_grades_view.html", context)

    selected_class = selection_form.cleaned_data["class_selected"]
    exam = selection_form.cleaned_data["exam"]
    exam_session = selection_form.cleaned_data['session']
    if exam.exam_session == exam_session:
        students = Student.objects.filter(current_class=selected_class)
        subjects_taught = teacher.subjects_in_class(selected_class)
        results_qs = Result.objects.filter(exam=exam, student__in=students).select_related("student", "subject")
    
        grouped_data = group_student_results(results_qs, students)
        subject_ranked_results = subject_results_with_ranks(grouped_data,subjects_taught)
        context["subject_ranked_results"] = subject_ranked_results
        grouped_data = assign_positions(grouped_data)
        class_summary = class_score_summary(grouped_data,results_qs)
        context.update({
            "class_mean_score": class_summary.get("class_mean_score"),
            "class_average": class_summary.get("class_average"),
            "class_mean_grade": class_summary.get("class_mean_grade"),
            "class_subjects_mean": class_summary.get("class_subjects_mean"),
            "selected_class": selected_class
        })



        if context["class_teacher_class"] == selected_class:
            context["own_class_results"] = grouped_data
        else:
            context["other_class_results"] = filter_subjects(grouped_data, subjects_taught)
    else:
        messages.error(request,"No exam results associated with the details provided.Please check and try again")
        return render(request, "teachers/teacher_students_grades_view.html", context)

    context["selected_class"] = selected_class
    return render(request, "teachers/teacher_students_grades_view.html", context)



@login_required
def teacher_students_grades_edit(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    selection_form = ExamSelectionForm(request.GET or None)

    # Initialize context
    context = {
        "selection_form": selection_form,
        "own_class_formset": None,
        "other_class_formset": None,
        "selected_class": None,
        "class_teacher_class": None,
    }

    if selection_form.is_valid():
        exam = selection_form.cleaned_data['exam']
        exam_session = selection_form.cleaned_data['session']
        selected_class = selection_form.cleaned_data['class_selected']
        students = Student.objects.filter(current_class=selected_class)

        own_class = ClassRoom.objects.filter(class_teacher=teacher).first()
        context["selected_class"] = selected_class
        context["class_teacher_class"] = own_class

        subjects_taught = teacher.subjects_in_class(selected_class)
 
        # ✏️ Handle own class
        if own_class and selected_class == own_class:
            form_response = handle_own_class_results(request, exam, selected_class, students,exam_session)
        else:
            form_response = handle_other_class_results(request, exam, selected_class, students, subjects_taught,exam_session)

        # 🔁 If helper returned a redirect, redirect immediately
        if isinstance(form_response, HttpResponseRedirect):
            return form_response

        # Otherwise, set the appropriate formset in context
        if own_class and selected_class == own_class:
            context["own_class_formset"] = form_response
        else:
            context["other_class_formset"] = form_response

    return render(request, "teachers/teacher_students_grades_edit.html", context)

class page_not_available(TemplateView):
    template_name = 'teachers/page_not_available.html'