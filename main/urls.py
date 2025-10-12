from django.urls import path
from . import views
from .models import SchoolFeeStructure,FeePayment,Event,Announcement
from .forms import ParentForm, TeacherForm,FeeStructureForm,FeePaymentForm,EventForm,AnnouncementForm

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
        path("portal/management/settings/", views.SettingsPage.as_view(), name="settings_page"),

    


    path("management/parents/add/", views.profile_create,{"form_class":ParentForm,"template":"dashboards/profile_create.html","go_to_url":"manage_parents","role":"Parent"}, name="parent_add"),
    path("management/parents/edit/<int:pk>/", views.ParentUpdate.as_view(), name="parent_edit"),
    path("management/parents/delete/<int:pk>/", views.ParentDelete.as_view(), name="parent_delete"),


    path("management/classes/add/", views.handle_class, {"action": "create"}, name="class_add"),
    path("management/classes/<int:pk>/edit/", views.handle_class, {"action": "edit"}, name="class_edit"),
    path("management/classes/<int:pk>/delete/", views.handle_class, {"action": "delete"}, name="class_delete"),



    path("management/teachers/add/", views.profile_create,{"form_class":TeacherForm,"template":"dashboards/profile_create.html","go_to_url":"manage_teachers","role":"Teacher"}, name="teacher_add"),
    path("management/teachers/delete/<int:pk>/",views.TeacherDelete.as_view(),name='delete_teacher'),
    path("management/teachers/edit/<int:pk>/",views.TeacherUpdate.as_view(),name='edit_teacher'),




    path("management/students/add/",views.AddStudent.as_view(),name='add_student'),
    path("management/students/delete/<int:pk>/",views.StudentDelete.as_view(),name='delete_student'),
    path("management/students/edit/<int:pk>/",views.StudentUpdate.as_view(),name='edit_student'),

    ###
    ##FINANCES

    path("portal/management/financials/", views.ManageFinancials.as_view(), name="manage_financials"),


     # Fee Structures
    path("management/fees/structures/add/", views.handle_fee,
         {"model": SchoolFeeStructure, "form_class": FeeStructureForm,
          "template": "dashboards/add_edit_form.html", "go_to_url": "manage_financials",
          "type_name": "structure", "action": "create"},
         name="fee_structure_add"),

    path("management/fees/structures/<int:pk>/edit/", views.handle_fee,
         {"model": SchoolFeeStructure, "form_class": FeeStructureForm,
          "template": "dashboards/add_edit_form.html", "go_to_url": "manage_financials",
          "type_name": "structure", "action": "edit"},
         name="fee_structure_edit"),

    path("management/fees/structures/<int:pk>/delete/", views.handle_fee,
         {"model": SchoolFeeStructure, "form_class": FeeStructureForm,
          "template": "dashboards/delete_form.html", "go_to_url": "manage_financials",
          "type_name": "structure", "action": "delete"},
         name="fee_structure_delete"),


    # Fee Payments
    path("management/fees/payments/add/", views.handle_fee,
         {"model": FeePayment, "form_class": FeePaymentForm,
          "template": "dashboards/add_edit_form.html", "go_to_url": "manage_financials",
          "type_name": "payment", "action": "create"},
         name="fee_payment_add"),

    path("management/fees/payments/<int:pk>/edit/", views.handle_fee,
         {"model": FeePayment, "form_class": FeePaymentForm,
          "template": "dashboards/add_edit_form.html", "go_to_url": "manage_financials",
          "type_name": "payment", "action": "edit"},
         name="fee_payment_edit"),

    path("management/fees/payments/<int:pk>/delete/", views.handle_fee,
         {"model": FeePayment, "form_class": FeePaymentForm,
          "template": "dashboards/delete_form.html", "go_to_url": "manage_financials",
          "type_name": "payment", "action": "delete"},
         name="fee_payment_delete"),


#Announcements
 path("management/announcements/add/", views.handle_announcement_event,
         {"model": Announcement, "form_class": AnnouncementForm,
          "template": "dashboards/add_edit_form.html", "go_to_url": "manage_announcements",
          "type_name": "announcement", "action": "create"},
         name="announcement_add"),

    path("management/announcements/<int:pk>/edit/", views.handle_announcement_event,
         {"model": Announcement, "form_class": AnnouncementForm,
          "template": "dashboards/add_edit_form.html", "go_to_url": "manage_announcements",
          "type_name": "announcement", "action": "edit"},
         name="announcement_edit"),

    path("management/announcements/<int:pk>/delete/", views.handle_announcement_event,
         {"model": Announcement, "form_class": AnnouncementForm,
          "template": "dashboards/delete_form.html", "go_to_url": "manage_announcements",
          "type_name": "announcement", "action": "delete"},
         name="announcement_delete"),

    # Events
    path("management/events/add/", views.handle_announcement_event,
         {"model": Event, "form_class": EventForm,
          "template": "dashboards/add_edit_form.html", "go_to_url": "manage_events",
          "type_name": "event", "action": "create"},
         name="event_add"),

    path("management/events/<int:pk>/edit/", views.handle_announcement_event,
         {"model": Event, "form_class": EventForm,
          "template": "dashboards/add_edit_form.html", "go_to_url": "manage_events",
          "type_name": "event", "action": "edit"},
         name="event_edit"),

    path("management/events/<int:pk>/delete/", views.handle_announcement_event,
         {"model": Event, "form_class": EventForm,
          "template": "dashboards/delete_form.html", "go_to_url": "manage_events",
          "type_name": "event", "action": "delete"},
         name="event_delete"),


     path("management/reports/", views.reports_portal, name="reports_portal"),
     path("management/students/details/<int:pk>/",views.management_student_detail, name="management_student_detail"),
    
    path("parent/children/", views.my_children, name="my_children"),
        path("child/<int:pk>/", views.parent_child_detail, name="child_detail"),
            path("parent/events/", views.events_page, name="events_page"),
            path("parent/performance/",views.performance_page, name="performance_page"),
                path("parent/fees/", views.fees_page, name="fees_page"),



     path("teacher/my-classes/", views.my_classes, name="teacher_my_classes"),
     path("teacher/students/", views.teacher_students, name="teacher_students"),
     path("teacher/students/grades/", views.teacher_students_grades_view, name="teacher_students_grades_view"),
     path("teacher/students/grades/edit/", views.teacher_students_grades_edit, name="teacher_students_grades_edit"),


path("page/not/available",views.page_not_available.as_view(),name='page_not_available')







   

]