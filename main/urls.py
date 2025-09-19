from django.urls import path
from .views import AboutPage,HomePage,ClassesPage,ContactPage,AdmissionPage

urlpatterns = [
    path('home/',HomePage.as_view(),name='home'),
    path('about/',AboutPage.as_view(),name='about'),
    path('classes/',ClassesPage.as_view(),name='classes'),
    path('contact/',ContactPage.as_view(),name='contact'),
    path('admission/',AdmissionPage.as_view(),name='admission')
]