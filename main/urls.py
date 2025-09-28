from django.urls import path
from .views import AboutPage,HomePage,ClassesPage,ContactPage,AdmissionPage,Faqs,Gallery,Events,PortalSelection

urlpatterns = [
    path('home/',HomePage.as_view(),name='home'),
    path('about/',AboutPage.as_view(),name='about'),
    path('classes/',ClassesPage.as_view(),name='classes'),
    path('contact/',ContactPage.as_view(),name='contact'),
    path('admission/',AdmissionPage.as_view(),name='admission'),
    path('FAQs/',Faqs.as_view(),name='FAQs'),
    path('gallery/',Gallery.as_view(),name='gallery'),
    path('events/',Events.as_view(),name='events'),
    path('portal_selection/',PortalSelection.as_view(),name='portal_selection')
]