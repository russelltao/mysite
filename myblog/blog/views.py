from django.shortcuts import render,get_object_or_404  
from django.template.response import TemplateResponse  
from blog.models import Blog  
  
# Create your views here.  
def home(request):  
    return TemplateResponse(request,"home.html",{'blog':Blog.objects.all()})  
def blog(request,slug):  
    blog=get_object_or_404(Blog,slug=slug)  
    return TemplateResonse(request,"blog.html",{'blog':blog})  