from typing import Iterable
from django.db import models
from django.utils import timezone
import random

ALPHA = "abcdefghijklmnopqrstuvwxyz "

# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=300)
    features = models.TextField(null=True, blank=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    technologies = models.CharField(max_length=255)
    demo_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Skill(models.Model):
    name = models.CharField(max_length=200)
    rate = models.IntegerField(verbose_name="Rate (out of 100)", default=0, null=False, blank=0)
    tag = models.CharField(max_length=200, editable=False, default="", null=False)

    def clamp_rate(self):
        self.rate = min(100, max(0, self.rate))

    def save(self, *args) -> None:
        self.tag = "".join([char.lower() for char in self.tag if char.lower() in ALPHA])

        if self.tag == "":
            for _ in range(15):
                self.tag += random.choice(ALPHA)

        self.tag = self.tag.replace(" ", "_")

        self.clamp_rate()
        return super().save(*args)

    def __str__(self):
        return self.name
    
class About(models.Model):
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text.split("\n")[0][:20] # first line until 2Oth char
    
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name
    
class Blog(models.Model):
    sno = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    meta = models.CharField(max_length=300)
    content = models.TextField()
    thumbnail_img = models.ImageField(null=True, blank=True, upload_to="images/")
    thumbnail_url = models.URLField(blank=True, null=True)
    categories = models.ManyToManyField("Category", blank=False) # TODO: Auto set to uncategorized
    slug = models.CharField(max_length=100, unique=True)
    time = models.DateField(auto_now_add=True)

    def __str__(self):
        categories = list(self.categories.all())
        print(self.title, categories)
        categories = [c.name for c in categories]
        return f"{self.title}     ||     {'-'.join(categories)}"
    
"""    def save(self, *args, **kwargs):
        # Appel à super() pour sauvegarder l'objet dans la base de données
        super().save(*args, **kwargs) 

        categories = list(self.categories.all())
        if not categories:
            # get the default category
            default = Category.objects.filter(name="Uncategorized").first()

            # Vérifiez si l'objet a un ID (c'est-à-dire s'il a été enregistré dans la base de données)
            if self.pk:
                # Ajoutez la catégorie par défaut
                self.categories.add(default)
                self.save(update_fields=['categories'])

                print(f"Added category {default.name} to the post {self.title}")
                print([c for c in self.categories.all()])
            else:
                print("Object not saved yet, cannot add default category.")"""

