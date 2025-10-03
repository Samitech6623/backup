from django.urls import path
from . import views
from .models import SchoolFeeStructure,FeePayment
from .forms import ParentForm, TeacherForm,FeeStructureForm,FeePaymentForm

urlpatterns = [
    path('home/',views.HomePage.as_view(),name='home'),
    path('about/',views.AboutPage.as_view(),name='about'),
    path('classes/',views.ClassesPage.as_view(),name='classes'),
    path('contact/',views.ContactPage.as_view(),name='contact'),
    path('admission/',views.AdmissionPage.as_view(),name='admission'),
    path('FAQs/',views.Faqs.as_view(),name='FAQs'),
    path('gallery/',views.Gallery.as_view(),name='gallery'),
    path('events/',views.Events.as_view(),name='events'),
    path('portal_selection/', views.PortalSelection.as_view(), name='portal_selection'),
    path('portal/login/management/', views.portal_log_in, {"role": "management"}, name='management_portal'),
    path('portal/login/parent/', views.portal_log_in, {"role": "parent"}, name='parent_portal'),
    path('portal/login/teacher/', views.portal_log_in, {"role": "teacher"}, name='teacher_portal'),
    path('portal/logout/', views.logout_view, name='portal_logout'),
    path('management/dashboard/', views.management_dashboard, name='management_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('parent/dashboard/', views.parent_dashboard, name='parent_dashboard'),

    path("portal/management/teachers/", views.ManageTeachers.as_view(), name="manage_teachers"),
    path("portal/management/parents/", views.ManageParents.as_view(), name="manage_parents"),
    path("portal/management/students/", views.ManageStudents.as_view(), name="manage_students"),
    path("portal/management/classes/", views.manage_classes, name="manage_classes"),
    path("portal/management/events/", views.ManageEvents.as_view(), name="manage_events"),
    path("portal/management/announcements/", views.ManageAnnouncements.as_view(), name="manage_announcements"),


    path("management/parents/add/", views.profile_create,{"form_class":ParentForm,"template":"dashboards/profile_create.html","redirect_url":"manage_parents","role":"Parent"}, name="parent_add"),
    path("management/parents/edit/<int:pk>/", views.ParentUpdate.as_view(), name="parent_edit"),
    path("management/parents/delete/<int:pk>/", views.ParentDelete.as_view(), name="parent_delete"),


    path("management/classes/add/", views.handle_class, {"action": "create"}, name="class_add"),
    path("management/classes/<int:pk>/edit/", views.handle_class, {"action": "edit"}, name="class_edit"),
    path("management/classes/<int:pk>/delete/", views.handle_class, {"action": "delete"}, name="class_delete"),



    path("management/teachers/add/", views.profile_create,{"form_class":TeacherForm,"template":"dashboards/profile_create.html","redirect_url":"manage_teachers","role":"Teacher"}, name="teacher_add"),
    path("management/teachers/delete/<int:pk>/",views.TeacherDelete.as_view(),name='delete_teacher'),
    path("management/teachers/edit/<int:pk>/",views.TeacherUpdate.as_view(),name='edit_teacher'),



    path("management/students/add/",views.AddStudent.as_view(),name='add_student'),
    path("management/students/delete/<int:pk>/",views.StudentDelete.as_view(),name='delete_student'),
    path("management/students/edit/<int:pk>/",views.StudentUpdate.as_view(),name='edit_student'),

    path("portal/management/financials/", views.ManageFinancials.as_view(), name="manage_financials"),


     # Fee Structures
    path("management/fees/structures/add/", views.handle_fee,
         {"model": SchoolFeeStructure, "form_class": FeeStructureForm,
          "template": "dashboards/edit_fee.html", "redirect_url": "manage_financials",
          "type_name": "structure", "action": "create"},
         name="fee_structure_add"),

    path("management/fees/structures/<int:pk>/edit/", views.handle_fee,
         {"model": SchoolFeeStructure, "form_class": FeeStructureForm,
          "template": "dashboards/edit_fee.html", "redirect_url": "manage_financials",
          "type_name": "structure", "action": "edit"},
         name="fee_structure_edit"),

    path("management/fees/structures/<int:pk>/delete/", views.handle_fee,
         {"model": SchoolFeeStructure, "form_class": FeeStructureForm,
          "template": "dashboards/edit_fee.html", "redirect_url": "manage_financials",
          "type_name": "structure", "action": "delete"},
         name="fee_structure_delete"),


    # Fee Payments
    path("management/fees/payments/add/", views.handle_fee,
         {"model": FeePayment, "form_class": FeePaymentForm,
          "template": "dashboards/edit_fee.html", "redirect_url": "manage_financials",
          "type_name": "payment", "action": "create"},
         name="fee_payment_add"),

    path("management/fees/payments/<int:pk>/edit/", views.handle_fee,
         {"model": FeePayment, "form_class": FeePaymentForm,
          "template": "dashboards/edit_fee.html", "redirect_url": "manage_financials",
          "type_name": "payment", "action": "edit"},
         name="fee_payment_edit"),

    path("management/fees/payments/<int:pk>/delete/", views.handle_fee,
         {"model": FeePayment, "form_class": FeePaymentForm,
          "template": "dashboards/edit_fee.html", "redirect_url": "manage_financials",
          "type_name": "payment", "action": "delete"},
         name="fee_payment_delete"),



    


   

]