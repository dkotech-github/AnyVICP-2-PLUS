from django.http import *
from django.template import loader
from AnyVICP2.models import Website, Announcement
import json
import datetime
import hashlib
from django.contrib.auth import *
from django.contrib.auth.decorators import *

def index(request):
    """
    Index page
    """
    # Render the template with the websites
    template = loader.get_template('index.html')

    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))
    return HttpResponse(template.render(context, request))

def join(request):
    """
    Join page
    """
    # Render the template with the websites
    template = loader.get_template('join.html')

    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))
    return HttpResponse(template.render(context, request))

def joinapi(request:HttpRequest):
    """
    Join api

    No template
    """
    """
    name: 名称
    domain: 域名
    author: 创建者
    createDate: 创建日期
    icpNumber: ICP号码
    status: 状态
    """
    name = request.GET.get('name')
    domain = request.GET.get('domain')
    author = request.GET.get('author')
    createDate = datetime.datetime.now()
    icpNumber = request.GET.get('icpNumber')
    status = True
    
    # Create a new website
    website = Website(name=name, domain=domain, author=author, createdate=createDate, icpNumber=icpNumber, status=status)
    website.save()
    
    # Redirect to result shower
    return HttpResponseRedirect('/result/?domain=' + domain) # type: ignore

def result(request:HttpRequest):
    """
    Result page
    """
    # Render the template with the websites
    template = loader.get_template('result.html')

    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))

    # Find domain in database
    domain = request.GET.get('domain')
    website = Website.objects.filter(domain=domain).first()

    notfound = False
    if not website:
        notfound = True
        return HttpResponse(template.render(context, request))

    context['notfound'] = notfound
    name = website.name
    domain = website.domain
    author = website.author
    createDate = website.createdate.__str__()
    icpNumber = website.icpNumber
    status = website.status

    context['site_name'] = name
    context['site_domain'] = domain
    context['site_author'] = author
    context['site_createdate'] = createDate
    context['site_icpnumber'] = icpNumber
    context['site_status'] = status

    return HttpResponse(template.render(context, request))

def api_adminLogin(request:HttpRequest):
    """
    Admin login api
    """
    # Get config
    config = json.load(open('./AnyVICP2/config.json', "r"))

    # Check if username and password are correct
    username = request.GET.get('username')
    password = request.GET.get('password')
    user = authenticate(request, username=username, password=password) # type: ignore
    if user is not None:
        login(request, user) # type: ignore
        return HttpResponseRedirect("./index/")
    else:
        return HttpResponseRedirect('./login/?error=1')

def admin_login(request:HttpRequest):
    """
    Admin login page
    """
    # Render the template with the websites
    template = loader.get_template('admin/admin_login.html')

    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))

    # Check if error
    error = request.GET.get('error')
    if error == '1':
        context['error'] = '用户名或密码错误. Username or password wrong.'

    return HttpResponse(template.render(context, request))

@login_required
def admin_index(request:HttpRequest):
    """
    Admin index page
    """
    # Render the template with the websites
    template = loader.get_template('admin/admin_index.html')

    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))

    return HttpResponse(template.render(context, request))

@login_required
def admin_website(request:HttpRequest):
    """
    Admin website page
    """
    # Render the template with the websites
    template = loader.get_template('admin/admin_managewebsites.html')

    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))

    # Get all website
    websites = Website.objects.all()
    
    # Set all website edit link
    context["websites"] = {}
    for website in websites:
        context["websites"].update({website:"./webedit/?id="+str(website.name)})

    return HttpResponse(template.render(context, request))

@login_required
def admin_websiteedit(request:HttpRequest):
    """
    Admin website edit page
    """
    # Render the template with the websites
    template = loader.get_template('admin/admin_editwebsite.html')

    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))

    # Get website name
    website_name = request.GET.get('id')

    context["website_source_name"] = website_name

    return HttpResponse(template.render(context, request))

@login_required
def admin_websiteeditpost(request:HttpRequest):
    """
    Admin website edit post page
    """
    name = request.GET.get('name')
    domain = request.GET.get('domain')
    author = request.GET.get('author')
    createDate = datetime.datetime.now()
    icpNumber = request.GET.get('icpNumber')
    source_name = request.GET.get('changewebsite_source_name-_')
    status = True
    
    # Create a new website
    website = Website(name=name, domain=domain, author=author, createdate=createDate, icpNumber=icpNumber, status=status)
    website.save()

    # Remove source website
    Website.objects.filter(name=source_name).delete()
    
    # Redirect to select
    return HttpResponseRedirect('./websitemanage') # type: ignore

@login_required
def admin_announcementcreate(request:HttpRequest):
    """
    Admin announcement create page
    """
    # Render the template with the websites
    template = loader.get_template('admin/admin_announcementmanage.html')

    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))

    return HttpResponse(template.render(context, request))

@login_required
def admin_announcement_createapi(request:HttpRequest):
    """
    Admin announcement create api
    """
    # Get config
    context = json.load(open('./AnyVICP2/config.json', "r"))

    # Get announcement
    ann_name = request.GET.get('name')
    ann_content = request.GET.get('content')
    ann_author = request.GET.get('author')

    # Create a new announcement
    announcement = Announcement(name=ann_name, content=ann_content, author=ann_author)
    announcement.save()

    return HttpResponseRedirect("./index")