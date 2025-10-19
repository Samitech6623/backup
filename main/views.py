from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
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
from .utils import (group_student_results, assign_positions,filter_subjects,class_score_summary,handle_own_class_results,
                    handle_other_class_results,subject_results_with_ranks,get_fee_summary)

from django.forms import modelformset_factory


from .forms import ParentForm, StudentForm, TeacherForm,ClassForm,FeeStructureForm,FeePaymentForm,ExamSelectionForm, ResultForm,ParentPerformanceFilterForm
#from weasyprint import HTML
# Create your views here.


# context_processors.py


def portal_log_in(request,role):
    if request.method == 'POST':
        form = AuthenticationForm( request,data = request.POST )
        if form.is_valid():
            user = form.get_user()
            if hasattr(user,role):
                login(request,user)
                return redirect(f'{role}_dashboard')
            else:
               messages.error(request, f"No {role} account with those details. Please try again or select another dashboard.")
        else:
            messages.error(request, "Invalid username or password.")

    else:
        form = AuthenticationForm()
    return render(request,'log_in_form.html',{"form":form,"role":role})

def logout_view(request):
    logout(request)
    return redirect('portal_selection')

def profile_create(request, form_class, template, go_to_url,role):
    if request.method == "POST":
        user_form = UserCreationForm(request.POST)
        profile_form = form_class(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect(go_to_url)
    else:
        user_form = UserCreationForm()
        profile_form = form_class()

    return render(request, template, {
        "user_form": user_form,
        "profile_form": profile_form,
        "role":role,
        "go_to_url":go_to_url
    })


@login_required
def management_dashboard(request):
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_parents = Parent.objects.count()
    context = {"total_students":total_students,"total_teachers":total_teachers,"total_parents":total_parents}

    return render(request, 'base_management_dashboard.html',context=context)

@login_required
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    classes_assigned = teacher.teaching_class_assignments.select_related("class_assigned", "subject")
    classes_assigned_count = classes_assigned.count()
    try:
        class_teacher_of = Class.objects.get(class_teacher=teacher)
    except Class.DoesNotExist:
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
    return render(request, 'teacher_dashboard.html',context)


@login_required
def my_classes(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    # Classes where the teacher is subject teacher
    teaching_assignments = teacher.teaching_class_assignments.select_related("class_assigned", "subject")

    # Classes where the teacher is class teacher (homeroom)
    homeroom_class = Class.objects.filter(class_teacher=teacher).first()

    context = {
        "teaching_assignments": teaching_assignments,
        "homeroom_class": homeroom_class,
    }
    return render(request, "dashboards/teacher_my_classes.html", context)

@login_required
def teacher_students(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    # Check if this teacher is a class teacher
    try:
        class_teacher_of = Class.objects.get(class_teacher=teacher)
        # Prefetch parent info so we avoid too many queries
        students = Student.objects.filter(current_class=class_teacher_of).select_related("parent")
    except Class.DoesNotExist:
        class_teacher_of = None
        students = Student.objects.none()  # empty queryset

    context = {
        "students": students,
        "class_teacher_of": class_teacher_of,
    }
    return render(request, "dashboards/teacher_students_page.html", context)


@login_required
def teacher_students_grades_view(request):
    teacher = get_object_or_404(Teacher, user=request.user)
    selection_form = ExamSelectionForm(request.GET or None)

    context = {
        "selection_form": selection_form,
        "own_class_results": [],
        "other_class_results": [],
        "selected_class": None,
        "class_teacher_class": Class.objects.filter(class_teacher=teacher).first(),
        "class_mean_score":None,
        "class_mean_grade":None,
        "class_average":None,
        "class_subjects_mean":None
    }

    if not selection_form.is_valid():
        return render(request, "dashboards/teacher_students_grades_view.html", context)

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
        return render(request, "dashboards/teacher_students_grades_view.html", context)

    context["selected_class"] = selected_class
    return render(request, "dashboards/teacher_students_grades_view.html", context)



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

        own_class = Class.objects.filter(class_teacher=teacher).first()
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

    return render(request, "dashboards/teacher_students_grades_edit.html", context)




class page_not_available(TemplateView):
    template_name = 'dashboards/page_not_available.html'


@login_required
def parent_dashboard(request):
    parent = get_object_or_404(Parent, user=request.user)
    children = parent.children.all()

    # Get the active session and exams
    active_session = Session.objects.filter(
        start_date__lte=timezone.now().date(),
        end_date__gte=timezone.now().date()
    ).first()

    current_exam = Exam.objects.filter(exam_session=active_session).order_by("-id").first()

    for child in children:
        child.balance = child.fee_balance(active_session.term, active_session.year)
        child.attendance_rate = getattr(child, "attendance_rate", 95)
        child.latest_exam = current_exam

        if current_exam:
            summary = child.exam_summary(current_exam)
            child.total_score = summary["total"]
            child.average_score = summary["average"]
            child.grade = summary["grade"]
            child.remark = summary["remark"]
        else:
            child.total_score = 0
            child.average_score = 0
            child.grade = "-"
            child.remark = "No exam yet"

    events = Event.objects.filter(date__gte=timezone.now()).order_by("date")[:5]

    context = {
        "children": children,
        "events": events,
        "current_exam": current_exam,
        "active_session": active_session,
    }
    return render(request, "parent_dashboard.html", context)

@login_required
def my_children(request):
    parent = get_object_or_404(Parent, user=request.user)
    children = parent.children.all()   # because of related_name="children"
    return render(request, "dashboards/my_children.html", {"children": children})


@login_required
def parent_child_detail(request, pk):
    child = get_object_or_404(Student, pk=pk, parent__user=request.user)

    # Example: latest exam results and attendance
    latest_exam = Result.objects.filter(student=child).order_by('-exam__exam_session__start_date').first()
    if latest_exam:
        latest_exam = latest_exam.exam  # The latest Exam object
        results = Result.objects.filter(student=child, exam=latest_exam)
    else:
        results = Result.objects.none()  # no results found

    total_paid = child.total_fees_paid()
    balance = child.fee_balance(term="Term 1", year=2025)  # you can adjust dynamically

    attendance_rate = getattr(child, "attendance_rate", None)

    return render(
        request,
        "dashboards/parent_child_detail.html",
        {
            "child": child,
            "results": results,
            "latest_exam":latest_exam,
            "total_paid": total_paid,
            "balance": balance,
            "attendance_rate": attendance_rate,
        },
    )
def parent_performance_page(request):
    form = ParentPerformanceFilterForm(request.GET or None, parent=request.user.parent_profile)

    results = []
    if form.is_valid():
        child = form.cleaned_data["child"]
        exam = form.cleaned_data["exam"]
        results = Result.objects.filter(student=child, exam=exam).select_related(
            "subject", "exam__exam_session", "grade_object"
        )

    return render(request, "dashboards/parent_children_performance_page.html", {
        "form": form,
        "results": results
    })

def parent_download_results(request):
    child_id = request.GET.get("child_id")
    exam_id = request.GET.get("exam_id")

    results = Result.objects.filter(student_id=child_id, exam_id=exam_id).select_related("subject", "grade_object", "exam")

    # Render an HTML template for PDF
    html_string = render(request, "parent/results_pdf.html", {
        "results": results,
        "child": results[0].student if results else None,
        "exam": results[0].exam if results else None,
    }).content.decode("utf-8")

    # Generate PDF
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="results_{child_id}_{exam_id}.pdf"'

    return response

@login_required
def parent_fees_page(request):
    parent = request.user.parent_profile
    children = parent.children.select_related("current_class").all()

    # Get current academic session
    current_session = Session.objects.order_by("-year", "-term").first()
    term = current_session.term if current_session else "Term 1"
    year = current_session.year if current_session else timezone.now().year

    fees_data = []

    for student in children:
        # ✅ Use helper to calculate fee summary
        fee_summary = get_fee_summary(student, term, year)

        payments = student.fee_payment.all().order_by("-paid_on")

        fees_data.append({
            "student": student,
            "class": student.current_class,
            "term": term,
            "year": year,
            "amount_required": fee_summary["required"],
            "total_paid": fee_summary["paid"],
            "balance": fee_summary["balance"],
            "status": fee_summary["status"],
            "payments": payments,
        })

    context = {
        "current_session": current_session,
        "fees_data": fees_data,
        "term": term,
        "year": year,
        "session": current_session,
    }

    return render(request, "dashboards/parent_fees_page.html", context)

class AboutPage(TemplateView):
    template_name = 'about.html'

class HomePage(TemplateView):
    template_name = 'home.html'

class ClassesPage(TemplateView):
    template_name = 'classes.html'

class ContactPage(TemplateView):
    template_name = 'contact.html'

class AdmissionPage(TemplateView):
    template_name = 'admission.html'

class Faqs(TemplateView):
    template_name = 'FAQs.html'

class Gallery(TemplateView):
    template_name = 'gallery.html'

class Events(TemplateView):
    template_name = 'events.html'
class PortalSelection(TemplateView):
    template_name = 'portal_selection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_role = None
        if user.is_authenticated:
            if hasattr(user, 'teacher'):
                user_role = 'teacher'
            elif hasattr(user, 'parent'):
                user_role = 'parent'
            elif hasattr(user, 'management'):
                user_role = 'management'
        context['user_role'] = user_role
        return context

class SettingsPage(TemplateView):
    template_name = 'dashboards/settings.html'

@method_decorator(login_required, name='dispatch')
class ManageTeachers(ListView):
    model = Teacher
    template_name = "dashboards/manage_teachers.html"
    context_object_name = "teachers"

class TeacherUpdate(UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = "dashboards/add_edit_form.html"
    success_url = reverse_lazy("manage_teachers")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_name'] = 'Teacher'
        context['go_to_url'] = 'manage_teachers'

        return context
    
    
class TeacherDelete(DeleteView):
    model = Teacher
    template_name = "dashboards/delete_form.html"
    success_url = reverse_lazy("manage_teachers")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_name'] = 'Teacher'
        context['go_to_url'] = 'manage_teachers'

        return context


@method_decorator(login_required, name='dispatch')
class ManageStudents(ListView):
    model = Student
    template_name = "dashboards/manage_students.html"
    context_object_name = "students"


class AddStudent(CreateView):
    model = Student
    form_class = StudentForm
    template_name = "dashboards/add_edit_form.html"
    success_url = reverse_lazy("manage_students")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_name'] = 'Student'
        context['go_to_url'] = 'manage_students'
        context['action'] = 'add'


        return context
    
class StudentUpdate(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "dashboards/add_edit_form.html"
    success_url = reverse_lazy("manage_students")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_name'] = 'Student'
        context['go_to_url'] = 'manage_students'
        context['action'] = 'edit'


        return context

class StudentDelete(DeleteView):
    model = Student
    template_name = "dashboards/delete_form.html"
    success_url = reverse_lazy("manage_students")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_name'] = 'Student'
        context['go_to_url'] = 'manage_students'

        return context

   ###
   # PRENTS 

class ManageParents(ListView):
    model = Parent
    template_name = "dashboards/manage_parents.html"
    context_object_name = "parents"

class ParentUpdate(UpdateView):
    model = Parent
    form_class = ParentForm
    template_name = "dashboards/profile_update.html"
    success_url = reverse_lazy("manage_parents")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_name'] = 'Parent'
        context['go_to_url'] = 'manage_parents'

        return context
    
    
class ParentDelete(DeleteView):
    model = Parent
    template_name = "dashboards/delete_form.html"
    success_url = reverse_lazy("manage_parents")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type_name'] = 'Parent'
        context['go_to_url'] = 'manage_parents'


        return context

   ####
   # classes 

@login_required
def manage_classes(request):
    classes = Class.objects.all().order_by("name")
    return render(request, "dashboards/manage_classes.html", {"classes": classes})

def handle_class(request, action, pk=None):
 
    go_to_url = 'manage_classes'
    if action == "create":
        if request.method == "POST":
            form = ClassForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("manage_classes")
        else:
            form = ClassForm()
        return render(request, "dashboards/add_edit_form.html", {"form": form, "type_name":'Class', "action": "Add", "go_to_url":go_to_url})

    elif action == "edit":
        obj = get_object_or_404(Class, pk=pk)
        if request.method == "POST":
            form = ClassForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return redirect("manage_classes")
        else:
            form = ClassForm(instance=obj)
        return render(request, "dashboards/add_edit_form.html", {"form": form, "type_name":'Class',  "action": "Edit", "go_to_url":go_to_url})

    elif action == "delete":
        obj = get_object_or_404(Class, pk=pk)
        if request.method == "POST":
            obj.delete()
            return redirect("manage_classes")
        return render(request, "dashboards/delete_form.html", {"object": obj,"type_name":"Class","go_to_url":go_to_url})




@method_decorator(login_required, name='dispatch')
class ManageEvents(ListView):
    model = Event
    template_name = "dashboards/manage_events.html"
    context_object_name = "events"   # instead of object_list

    def get_queryset(self):
        # Example: order events by date (soonest first)
        return Event.objects.order_by("date")


@method_decorator(login_required, name='dispatch')
class ManageAnnouncements(ListView):
    model = Announcement
    template_name = "dashboards/manage_announcements.html"
    context_object_name = "announcements" 



def handle_announcement_event(request, model, form_class, template, go_to_url , type_name, action, pk=None):
    obj = None
    if pk:
        obj = get_object_or_404(model, pk=pk)

    if action in ["create", "edit"]:
        if request.method == "POST":
            form = form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return redirect(go_to_url)
        else:
            form = form_class(instance=obj)
        return render(request, template, {"form": form, "type_name": type_name, "action": action, "go_to_url":go_to_url})

    elif action == "delete":
        if request.method == "POST":
            obj.delete()
            return redirect(go_to_url)
        return render(request, template, {"object": obj, "type_name": type_name, "action": action, "go_to_url":go_to_url})


class ManageFinancials(TemplateView):
    template_name = "dashboards/manage_financials.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fee_structures"] = SchoolFeeStructure.objects.all()
        context["fees"] = FeePayment.objects.all()
        context["students"] = Student.objects.all()
        return context
    


def handle_fee(request, model, form_class, template, go_to_url, pk=None, action="create", type_name = 'item'):
   
    if action == "create":
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(go_to_url)
        else:
            form = form_class()
        return render(request, template, {"form": form, "type_name": type_name , "go_to_url":go_to_url, "action":action})

    elif action == "edit":
        obj = get_object_or_404(model, pk=pk)
        if request.method == "POST":
            form = form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return redirect(go_to_url)
        else:
            form = form_class(instance=obj)
        return render(request, template, {"form": form, "type_name": type_name, "go_to_url":go_to_url, "action":action})

    elif action == "delete":
        obj = get_object_or_404(model, pk=pk)
        if request.method == "POST":
            obj.delete()
            return redirect(go_to_url)
        return render(request, "dashboards/delete_form.html", {"object": obj, "type_name": type_name ,"go_to_url":go_to_url,"action":action})







@login_required
def reports_portal(request):
    # General counts
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_parents = Parent.objects.count()

    # Financials
    total_fees_expected = SchoolFeeStructure.objects.aggregate(Sum("amount_required"))["amount_required__sum"] or 0
    total_fees_paid = FeePayment.objects.aggregate(Sum("amount"))["amount__sum"] or 0
    balance = total_fees_expected - total_fees_paid

    # Activities
    upcoming_events = Event.objects.count()
    announcements_count = Announcement.objects.count()

    context = {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_parents": total_parents,
        "total_fees_expected": total_fees_expected,
        "total_fees_paid": total_fees_paid,
        "balance": balance,
        "upcoming_events": upcoming_events,
        "announcements_count": announcements_count,
    }
    return render(request, "dashboards/manage_reports.html", context)



@login_required
def management_student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)

    # Example: latest exam results and attendance
    parent = student.parent.display_name
    results = student.results.all().order_by("-id")[:10]  # last 10 results
    total_paid = student.total_fees_paid()
    balance = student.fee_balance(term="Term 1", year=2025)  # you can adjust dynamically

    attendance_rate = getattr(student, "attendance_rate", None)

    return render(
        request,
        "dashboards/management_models_details.html",
        {
            "student": student,
            "results": results,
            "total_paid": total_paid,
            "balance": balance,
            "attendance_rate": attendance_rate,
            "parent":parent
        },
    )

@login_required
def events_page(request):
    events = Event.objects.all().order_by("date")  # upcoming first
    return render(request, "dashboards/events_page.html", {"events": events})


