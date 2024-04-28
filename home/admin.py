from django.contrib import admin
from django import forms
from home.models import Blog, Project, Skill, About, Category

# Register your models here.
class BlogAdminForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'id': "richtext_field"}))

    class Meta:
        model = Blog
        fields = "__all__"

class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm

admin.site.register(Blog, BlogAdmin)
admin.site.register(Project)
admin.site.register(Skill)
admin.site.register(About)
admin.site.register(Category)
