from django.db import models  
  
# Create your models here.  
class Blog(models.Model):  
    time    =models.DateTimeField(auto_now_add = True)  
    title   =models.CharField(max_length=100)  
    slug    =models.SlugField()  
    perex   =models.TextField()  
    content =models.TextField()  
    @models.permalink  
    def get_absolute_url(self):  
        return ('blog',[self.slug])  
    def __unicode__(self):  
        return self.title  
    class Meta:  
        ordering =['-time']  