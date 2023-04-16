from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages 
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required
from django.contrib.auth  import authenticate,  login, logout
from .csv_add import load
from .models import *
import json

# Create your views here
def home(request):
    print(request.user)
    if request.user.is_authenticated:
        return redirect('/aap')
    else:
        return redirect('/landing')
#    return render(request, 'home.html')

def signup(request):
    if request.method=="POST":
        # Get the post parameters
       
        username=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        # check for errorneous input
        if len(username)<5:
            return redirect('signup')

        
        if (pass1!= pass2):  
             return redirect('signup')

        # Check if the user already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            # Return an error message
            messages.error(request, 'User already exists')
            return redirect('signup')
        else:
            # Create a new user
            myuser = User.objects.create_user(username=username, email=email, password=pass1)
            myuser.save()
            messages.success(request, " Your Anime account has been successfully created")
            # Redirect to the login page
            return redirect('login')
    else:
        # Render the registration template
        return render(request, 'signup.html')

def userlogin(request):
    if request.method == "POST":
        # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user = authenticate(username=loginusername, password=loginpassword)
        if user is not None and user.is_authenticated:
            login(request, user)
            messages.success(request, "Successfully logged in")
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials! Please try again")
            return redirect("login")

    return render(request, 'login.html')


def logoutuser(request):
    logout(request)
    return redirect('/')


def landing(request):
    all_anime = Animedata.objects.all()
    paginator = Paginator(all_anime, 12) # paginate 12 items per page
    page_number = request.GET.get('page')
    all_anime = paginator.get_page(1) if page_number is None else paginator.get_page(page_number)
    context = {'all_anime': all_anime}
    return render(request, 'landing.html', context)

def anime_detail(request, pk):
    anime = get_object_or_404(Animedata, pk=pk)
    context = {'anime': anime,
               'episodes':range(anime.episodes),}
    return render(request, 'anime_detail.html', context)


def nav(request):
   return render(request, 'nav.html')

def footer(request):
   return render(request, 'footer.html')


@login_required(login_url='/login/')
def aap(request):
    if request.method=='GET':
        query = request.GET.get('query')
        if query:
            all_anime = Animedata.objects.filter(title__contains=query)
        else:
            all_anime = Animedata.objects.all()
        #notifications = Notification.objects.filter(user=User.objects.get(username=request.user))
        paginator = Paginator(all_anime, 24) # paginate 10 items per page
        page_number = request.GET.get('page')
        all_anime = paginator.get_page(1) if page_number is None else paginator.get_page(page_number)
        context = {'all_anime': all_anime,} #'notification':notifications,
        return render(request, 'aap.html', context)
@login_required(login_url='/login/')
def add_watchlist(request):
    if request.method=='POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            status = data.get('status')
            anime = Animedata.objects.get(id=id)
            user = request.user
            if WatchList.objects.filter(user=user,anime=anime).exists():
                return HttpResponse({"message":f"already in watchlist"},status=406)
            WatchList.objects.create(user=user,anime=anime,status=status)
            return HttpResponse({"message":"success"},status=200)
        except Exception as e:
            return HttpResponse({"message":f"failed {e}"},status=406)
@login_required(login_url='/login/')
def watchlists(request):
    user = request.user
    lists = WatchList.objects.filter(user=user)
    paginator = Paginator(lists, 24) 
    page_number = request.GET.get('page')
    watchlists = paginator.get_page(1) if page_number is None else paginator.get_page(page_number)
    return render(request, 'watchist.html', {"watchlists":watchlists})


def csvadd(request):
    load()
def epsiode(request,num):
    data = Episode.objects.filter(episode_number=num)
    return HttpResponse(data,status=200)

def add_watchlist(request):
   return render(request, 'add_watchlist.html')