from django.shortcuts import render, redirect
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from datetime import datetime
from rango.google_search import google_search


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).seconds > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        # visits = 1
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits


def index(request):
    request.session.set_test_cookie()
    # return render(request, 'rango/index.html', context=context_dict)

    # get 5 most liked categories
    category_list = Category.objects.order_by('-likes')[:5]

    # get 5 most viewed pages
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list,
                    'pages': page_list}

    # return render(request, 'rango/index.html', context_dict)
#     instead return:

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context_dict)

    return response


def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()

    print(request.method)
    print(request.user)
    name = "Koyynrad"
    context_dict = {'your_name': name}

    # return render(request, 'rango/about.html', context_dict)
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/about.html', context_dict)
    return response


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict["pages"] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    context_dict['query'] = category.name

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = google_search(query, 5)
            if len(result_list) == 0:
                context_dict['not_find'] = 'not_find'

            context_dict['query'] = query
            context_dict['result_list'] = result_list

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=True)
            print(cat, cat.slug)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0

                try:
                    Page.objects.get(url=page.url)
                except Page.DoesNotExist:
                    page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    content_dict = {'form': form, 'category': category}

    return render(request, 'rango/add_page.html', content_dict)


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})


def search(request):
    result_list = 0
    if request.method == 'POST':
        query = request.POST['query'].strip()
        search_name = query
        if query:
            result_list = google_search(query, 5)
    else:
        search_name = ''
    return render(request, 'rango/search.html', {'result_list': result_list,
                                                 'search_name': search_name})


def track_url(request):
    url = '/rango/'
    if request.method == 'GET':
        print("GET metodh")
        if 'page_id' in request.GET:
            print("page _id in GEt")
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                print('znaleziono')
                page.views += 1
                page.save()
                url = page.url
            except:
                print("problem")
                pass
    return redirect(url)


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('rango:index')
        else:
            print(form.errors)
    context_dict = {'form': form}

    return render(request, 'rango/profile_registration.html', context_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('rango:index')

    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm(
        {'website': userprofile.website, 'picture': userprofile.picture})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('rango:profile', user.username)
        else:
            print(form.errors)

    return render(request, 'rango/profile.html',
                  {'userprofile': userprofile, 'selecteduser': user, 'form': form})


@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()

    return render(request, 'rango/list_profiles.html',
                  {'userprofile_list': userprofile_list})


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        # cat_id = request.GET.get('category_i.d', '0')
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
            return HttpResponse(likes)
        else:
            return HttpResponse('dupa')


def get_category_list(max_results=0, start_with=''):
    cat_list = []
    if start_with:
        cat_list = Category.objects.filter(name__istartswith=start_with)

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]
    return cat_list


def suggest_category(request):
    cat_list = []
    start_with = ''

    if request.method == 'GET':
        start_with = request.GET['suggestion']
    cat_list = get_category_list(8, start_with)

    return render(request, 'rango/cats.html', {'cats': cat_list})


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category,
                                           title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            context_dict['pages'] = pages
    return render(request, 'rango/page_list.html',context_dict)
