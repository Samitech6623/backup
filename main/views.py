from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

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