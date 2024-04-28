from django.shortcuts import render
from home.models import Blog, Project, Skill, About, Category
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.db.models import Q
import random
import re


# manually defined tags for most commons techs
TECHNOLOGIES = {
    'python': '<span class="text-xs bg-gradient-to-r from-cyan-500 to-blue-500 py-1 px-4 rounded-full"><i class="fa-brands fa-python"></i> Python</span>',
    'sql':    '<span class="text-xs bg-gradient-to-r from-cyan-500 to-blue-500 py-1 px-4 rounded-full"><i class="fa-brands fa-database"></i> SQL</span>',
    'django': '<span class="text-xs bg-gradient-to-r from-cyan-500 to-blue-500 py-1 px-4 rounded-full"><i class="fa-brands fa-django"></i> Django</span>',
    'html':   '<span class="text-xs bg-gradient-to-r from-cyan-500 to-blue-500 py-1 px-4 rounded-full"><i class="fa-brands fa-html5"></i> HTML</span>',
    'css':    '<span class="text-xs bg-gradient-to-r from-cyan-500 to-blue-500 py-1 px-4 rounded-full"><i class="fa-brands fa-css3"></i> CSS</span>',
    'js':     '<span class="text-xs bg-gradient-to-r from-cyan-500 to-blue-500 py-1 px-4 rounded-full"><i class="fa-brands fa-square-js"></i> JavaScript</span>',
}

def get_tech_tags(tech:str):
    if tech in TECHNOLOGIES:
        return TECHNOLOGIES[tech.lower()]
    else:
        return f'<span class="text-xs bg-gradient-to-r from-cyan-500 to-blue-500 py-1 px-4 rounded-full"><i class="fa-brands fa-{tech.lower()}"></i> {tech}</span>'

def get_search_categories():
    CATEGORIES_PER_LINE = 3
    tabled_categories = [[] for i in range(CATEGORIES_PER_LINE)]

    categories = Category.objects.all()

    i = row = 0
    while  i < len(categories):
        tabled_categories[row].append(categories[i])
        i += 1
        if i%CATEGORIES_PER_LINE == 0:
            row += 1
    return tabled_categories

# Create your views here.
def index (request):
    blogs = Blog.objects.all()
    random_blogs = random.sample(list(blogs), 3)

    context = {'random_blogs': random_blogs, "categories": get_search_categories()}
    return render(request, 'index.html', context)

def about (request):
    skills = Skill.objects.all()
    about = About.objects.first()
    about.text = about.text.replace("\n", "<br>")
    
    NB_COLUMNS = 2
    columns = [[] for _ in range(NB_COLUMNS)]

    for i in range(len(skills)):
        columns[i%NB_COLUMNS].append(skills[i])

    return render(request, 'about.html', context={"about": about, "skills": columns, "categories": get_search_categories()})

def thanks(request):
    return render(request, 'thanks.html', context={ "categories": get_search_categories()})

def contact (request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        invalid_imput = ['', ' ']
        if name in invalid_imput or email in invalid_imput or phone in invalid_imput or message in invalid_imput:
            messages.error(request, 'One or more fields are empty!')
        else:
            email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
            phone_pattern = re.compile(r'^[0-9]{10}$')

            if email_pattern.match(email) and phone_pattern.match(phone):
                form_data = {
                'name':name,
                'email':email,
                'phone':phone,
                'message':message,
                }
                message = '''
                From:\n\t\t{}\n
                Message:\n\t\t{}\n
                Email:\n\t\t{}\n
                Phone:\n\t\t{}\n
                '''.format(form_data['name'], form_data['message'], form_data['email'],form_data['phone'])
                send_mail('You got a mail!', message, '', ['dev.ash.py@gmail.com'])
                messages.success(request, 'Your message was sent.')
                # return HttpResponseRedirect('/thanks')
            else:
                messages.error(request, 'Email or Phone is Invalid!')
    return render(request, 'contact.html', context={"categories": get_search_categories()})

def projects(request):
    limit = 5
    if request.method == 'GET':
        if 'all' in request.GET:
            if request.GET['all'] == '1':
                limit = None

    projects_items = Project.objects.all().order_by('-date')

    total_projects = len(projects_items)
    
    # Limit the number of projects to display
    if limit:
        projects_items = projects_items[:limit]

    all_there = len(projects_items) == total_projects

    # Convert technologies to HTML tags
    for project in projects_items:
        techs = project.technologies.split(',')
        project.technologies = [get_tech_tags(tech) for tech in techs]

    # split the featured projects from lines to list
    for project in projects_items:
        project.features = project.features.split('\n')

    return render(request, 'projects.html', {'projects': projects_items, "all": all_there, "categories": get_search_categories()})

def blog(request):
    blogs = Blog.objects.all().order_by('-time')
    paginator = Paginator(blogs, 5)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    context = {'blogs': blogs, "categories": get_search_categories()}
    return render(request, 'blog.html', context)

def category(request, category):
    category = Category.objects.filter(name=category)
    posts = Blog.objects.all()
    category_posts = []
    for post in posts:
        if category in post.categories.all():
            category_posts.append(post)
    if not category_posts:
        message = f"No posts found in category: '{category}'"
        return render(request, "category.html", {"message": message})
    paginator = Paginator(category_posts, 3)
    page = request.GET.get('page')
    category_posts = paginator.get_page(page)
    return render(request, "category.html", {"category": category, 'category_posts': category_posts, "categories": get_search_categories()})

def categories(request):
    all_categories = Category.objects.values('name')
    return render(request, "categories.html", {'all_categories': all_categories, "categories": get_search_categories()})

def search(request):
    query = request.GET.get('q')
    query_list = query.split()
    results = Blog.objects.none()
    for word in query_list:
        results = results | Blog.objects.filter(Q(title__contains=word) | Q(content__contains=word)).order_by('-time')
    paginator = Paginator(results, 3)
    page = request.GET.get('page')
    results = paginator.get_page(page)
    if len(results) == 0:
        message = "Sorry, no results found for your search query."
    else:
        message = ""
    return render(request, 'search.html', {'results': results, 'query': query, 'message': message, "categories": get_search_categories()})


def blogpost (request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        context = {'blog': blog, "categories": get_search_categories()}
        return render(request, 'blogpost.html', context)
    except Blog.DoesNotExist:
        context = {'message': 'Blog post not found', "categories": get_search_categories()}
        return render(request, '404.html', context, status=404)


# def blogpost (request, slug):
#     blog = Blog.objects.filter(slug=slug).first()
#     context = {'blog': blog}
#     return render(request, 'blogpost.html', context)
