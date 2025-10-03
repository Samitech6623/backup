from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView,ListView,UpdateView,CreateView,DeleteView
from django.contrib.auth import login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,PasswordChangeForm,PasswordResetForm
from .models import Student,Teacher,Parent,Class,SchoolFeeStructure,FeePayment
from django.urls import reverse_lazy

from .forms import ParentForm, StudentForm, TeacherForm,ClassForm,FeeStructureForm,FeePaymentForm

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

def profile_create(request, form_class, template, redirect_url,role):
    if request.method == "POST":
        user_form = UserCreationForm(request.POST)
        profile_form = form_class(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect(redirect_url)
    else:
        user_form = UserCreationForm()
        profile_form = form_class()

    return render(request, template, {
        "user_form": user_form,
        "profile_form": profile_form,
        "role":role,
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
    return render(request, 'teacher_dashboard.html')

@login_required
def parent_dashboard(request):
    return render(request, 'parent_dashboard.html')

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



@method_decorator(login_required, name='dispatch')
class ManageTeachers(ListView):
    model = Teacher
    template_name = "dashboards/manage_teachers.html"
    context_object_name = "teachers"


@method_decorator(login_required, name='dispatch')
class ManageStudents(ListView):
    model = Student
    template_name = "dashboards/manage_students.html"
    context_object_name = "students"

@login_required
def manage_classes(request):
    classes = Class.objects.all().order_by("name")
    return render(request, "dashboards/manage_classes.html", {"classes": classes})



@method_decorator(login_required, name='dispatch')
class ManageEvents(TemplateView):
    template_name = "dashboards/manage_events.html"


@method_decorator(login_required, name='dispatch')
class ManageAnnouncements(TemplateView):
    template_name = "dashboards/manage_announcements.html"

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
        context['role_name'] = 'Parent'
        context['go_to_url'] = 'manage_parents'

        return context
    
    
class ParentDelete(DeleteView):
    model = Parent
    template_name = "dashboards/profile_delete.html"
    success_url = reverse_lazy("manage_parents")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_name'] = 'Parent'
        context['go_to_url'] = 'manage_parents'

        return context



class AddStudent(CreateView):
    model = Student
    form_class = StudentForm
    template_name = "dashboards/add_student.html"
    success_url = reverse_lazy("manage_students")
    
class StudentUpdate(UpdateView):
    model = Student
    form_class = StudentForm
    template_name = "dashboards/profile_update.html"
    success_url = reverse_lazy("manage_students")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_name'] = 'Student'
        context['go_to_url'] = 'manage_students'

        return context

class StudentDelete(DeleteView):
    model = Student
    template_name = "dashboards/profile_delete.html"
    success_url = reverse_lazy("manage_students")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_name'] = 'Student'
        context['go_to_url'] = 'manage_students'

        return context
    

class TeacherUpdate(UpdateView):
    model = Teacher
    form_class = ParentForm
    template_name = "dashboards/profile_update.html"
    success_url = reverse_lazy("manage_teachers")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_name'] = 'Teacher'
        context['go_to_url'] = 'manage_teachers'

        return context
    
    
class TeacherDelete(DeleteView):
    model = Teacher
    template_name = "dashboards/profile_delete.html"
    success_url = reverse_lazy("manage_teachers")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['role_name'] = 'Teacher'
        context['go_to_url'] = 'manage_teachers'

        return context







class ManageFinancials(TemplateView):
    template_name = "dashboards/manage_financials.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["fee_structures"] = SchoolFeeStructure.objects.all()
        context["fees"] = FeePayment.objects.all()
        context["students"] = Student.objects.all()
        return context
    


def handle_fee(request, model, form_class, template, redirect_url, pk=None, action="create", type_name = 'item'):
   
    if action == "create":
        if request.method == "POST":
            form = form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(redirect_url)
        else:
            form = form_class()
        return render(request, template, {"form": form, "type": type_name})

    elif action == "edit":
        obj = get_object_or_404(model, pk=pk)
        if request.method == "POST":
            form = form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return redirect(redirect_url)
        else:
            form = form_class(instance=obj)
        return render(request, template, {"form": form, "type": type_name})

    elif action == "delete":
        obj = get_object_or_404(model, pk=pk)
        if request.method == "POST":
            obj.delete()
            return redirect(redirect_url)
        return render(request, "dashboards/fee_delete.html", {"object": obj, "type": type_name})


def handle_class(request, action, pk=None):
 

    if action == "create":
        if request.method == "POST":
            form = ClassForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("manage_classes")
        else:
            form = ClassForm()
        return render(request, "dashboards/class_edit_form.html", {"form": form, "action": "Add"})

    elif action == "edit":
        obj = get_object_or_404(Class, pk=pk)
        if request.method == "POST":
            form = ClassForm(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return redirect("manage_classes")
        else:
            form = ClassForm(instance=obj)
        return render(request, "dashboards/class_edit_form.html", {"form": form, "action": "Edit"})

    elif action == "delete":
        obj = get_object_or_404(Class, pk=pk)
        if request.method == "POST":
            obj.delete()
            return redirect("manage_classes")
        return render(request, "dashboards/class_delete_form.html", {"object": obj})
