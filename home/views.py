import re
from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages 
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth  import authenticate,  login, logout
from jsonschema import ValidationError
from .models import Episode, Video
from .csv_add import load
from .models import *
from django.http import JsonResponse
from django.template.loader import render_to_string
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
import pandas as pd
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django import forms
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Email')


def validate_email_address(value):
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False


def recommend(genre, title):
    model_data = Animedata.objects.filter(genre__icontains=genre).values()
    data = pd.DataFrame(model_data)  # Convert queryset to a pandas DataFrame
    vectorizer = CountVectorizer(stop_words='english')
    selected_cols = ['synopsis']
    document_term_matrix = vectorizer.fit_transform(data[selected_cols].fillna('').apply(lambda x: ' '.join(x), axis=1))
    n_features = document_term_matrix.shape[1]
    n_components = min(n_features, 100)
    svd = TruncatedSVD(n_components=n_components)
    svd_matrix = svd.fit_transform(document_term_matrix)
    scaler = StandardScaler()
    num_attributes = scaler.fit_transform(data[['score']].fillna(0))

    feature_matrix = pd.concat([pd.DataFrame(svd_matrix), pd.DataFrame(num_attributes)], axis=1)
    cosine_sim = cosine_similarity(feature_matrix, feature_matrix)

    def get_recommendations(cosine_sim, df, title):
        if title not in df['title'].values:
            return {'similar_anime': "No similar recommendations found for given anime title."}
        idx = df[df['title'] == title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]
        anime_indices = [i[0] for i in sim_scores]
        similar_anime = df[['title', 'id','img_url']].iloc[anime_indices]
        similar_anime_dict = similar_anime.to_dict('records')
        return similar_anime_dict

    similar_anime_dict = get_recommendations(cosine_sim, data, title)
    print(similar_anime_dict)
    return similar_anime_dict


def landing(request):
    # Get all the anime objects
    all_anime = Animedata.objects.all()
    # Paginate 12 items per page
    paginator = Paginator(all_anime, 12)
    # Get the page number from the GET request
    page_number = request.GET.get('page')
    # Get the objects for the requested page
    all_anime = paginator.get_page(1) if page_number is None else paginator.get_page(page_number)
    # Create the context dictionary
    context = {'all_anime': all_anime}
    # Render the landing page template with the context
    return render(request, 'landing.html', context)

def signup(request):
    if request.method == "POST":
        # Get the post parameters
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # Check for erroneous input
        if len(username) < 5:
            # If username is less than 5 characters, show error message and redirect to signup page
            messages.error(request, 'Username must be at least 5 characters long')
            return redirect('signup')

        if pass1 != pass2:
            # If passwords do not match, show error message and redirect to signup page
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        if not re.search("[A-Z]", pass1):
            # If password does not contain an uppercase character, show error message and redirect to signup page
            messages.error(request, 'Password must contain at least one uppercase character')
            return redirect('signup')

        # Check if the email is valid
        if not validate_email_address(email):
            # If email is invalid, show error message and redirect to signup page
            messages.error(request, 'Please enter a valid email address')
            return redirect('signup')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            # If username already exists, show error message and redirect to signup page
            messages.error(request, 'Username already taken')
            return redirect('signup')

        # Check if the email is already in use
        if User.objects.filter(email=email).exists():
            # If email is already in use, show error message and redirect to signup page
            messages.error(request, 'Email already in use')
            return redirect('signup')

        # Create a new user with the provided credentials
        myuser = User.objects.create_user(username=username, email=email, password=pass1)
        myuser.save()

        # Show success message and redirect to login page
        messages.success(request, "Your Anime account has been successfully created")
        return redirect('login')
    else:
        # Render the signup page template
        return render(request, 'signup.html')

def userlogin(request):
    # If the request method is POST
    if request.method == "POST":
        # Get the post parameters
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        # Authenticate the user
        user = authenticate(username=loginusername, password=loginpassword)
        if user is not None:
            if user.is_authenticated:
                # Log the user in and redirect them to the home page
                login(request, user)
                messages.success(request, "Successfully logged in")
                return redirect("home")
            else:
                # Display an error message and redirect them back to the login page
                messages.error(request, 'User is not authenticated')
                return redirect("login")
        else:
            # Display an error message and redirect them back to the login page
            messages.error(request, 'Invalid username or password')
            return redirect("login")

    # If the request method is GET, display the login page
    return render(request, 'login.html')

def forgotpass(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Display an error message if the email is not associated with an account
                form.add_error('email', 'This email is not associated with any account.')
                return render(request, 'forgotpass.html', {'form': form})

            # Generate a unique token and save it to the user's account
            token = default_token_generator.make_token(user)

            # Create the password reset URL
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            )

            # Send an email to the user with the password reset URL
            message = f'Click the link below to reset your password:\n{reset_url}'
            send_mail('Password reset request', message, 'from@example.com', [email])

            return render(request, 'password_reset_sent.html', {'email': email})
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgotpass.html', {'form': form})

from django.contrib.auth.forms import PasswordResetForm

def reset_password(request, token):
    try:
        user = User.objects.get(password_reset_token=token)
    except User.DoesNotExist:
        return render(request, 'password_reset_invalid.html')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            if password1 != password2:
                form.add_error('password2', 'Passwords do not match.')
            else:
                user.set_password(password1)
                user.password_reset_token = None
                user.save()
                return render(request, 'password_reset_complete.html')
    else:
        form = PasswordResetForm()

    return render(request, 'password_reset.html', {'form': form})



def home(request):
    print(request.user)
    # If the user is authenticated, redirect them to the aap page
    if request.user.is_authenticated:
        return redirect('/aap')
    # If the user is not authenticated, redirect them to the landing page
    else:
        return redirect('/landing')

#def home(request):
#    return render(request, 'home.html')

def logoutuser(request):
    # Log the user out and redirect them to the home page
    logout(request)
    return redirect('/')

def nav(request):
    # Render the nav.html template
    return render(request, 'nav.html')

def footer(request):
    # Render the footer.html template
    return render(request, 'footer.html')

@login_required(login_url='/login/')
def popularView(request):
    if request.method=='GET':
        # Get the query parameter from the URL if present
        query = request.GET.get('query')
        if query:
            # Filter the anime queryset based on the title that contains the query
            all_anime = Animedata.objects.filter(title__contains=query).order_by('-average_rating')
        else:
            # If no query parameter, retrieve all anime
            all_anime = Animedata.objects.all().order_by('-average_rating')
            
        # Create a paginator object with 24 items per page
        paginator = Paginator(all_anime, 12) 
        # Get the page number from the URL parameter
        page_number = request.GET.get('page')
        # Retrieve the anime queryset for the specified page number or first page if none is specified
        all_anime = paginator.get_page(1) if page_number is None else paginator.get_page(page_number)
        
        notifications = UserProfile.objects.get(user=request.user).notification_audits.all()
        # html = render_to_string('notifications.html', context, request=request)
        count = UserProfile.objects.get(user=request.user).notifications.all().count()
        context = {'all_anime': all_anime,
                   'notifications': notifications, 'count': count}
        return render(request, 'popularView.html', context)

@login_required(login_url='/login/')
def aap(request):
    if request.method=='GET':
        # Get the query parameter from the URL if present
        query = request.GET.get('query')
        if query:
            # Filter the anime queryset based on the title that contains the query
            all_anime = Animedata.objects.filter(title__contains=query)
        else:
            # If no query parameter, retrieve all anime
            all_anime = Animedata.objects.all()
            
        # Create a paginator object with 24 items per page
        paginator = Paginator(all_anime, 12) 
        # Get the page number from the URL parameter
        page_number = request.GET.get('page')
        # Retrieve the anime queryset for the specified page number or first page if none is specified
        all_anime = paginator.get_page(1) if page_number is None else paginator.get_page(page_number)
        
        notifications = UserProfile.objects.get(user=request.user).notification_audits.all()
        # html = render_to_string('notifications.html', context, request=request)
        count = UserProfile.objects.get(user=request.user).notifications.all().count()
        context = {'all_anime': all_anime,
                   'notifications': notifications, 'count': count}
        return render(request, 'aap.html', context)
    
@login_required(login_url='/login/')
def notification_seen(request):
    if request.method=="POST":
        UserProfile.objects.get(user=request.user).notifications.all().delete()
        return HttpResponse({"success":True})
    else:
        return HttpResponse({"success":False},406)

@login_required(login_url='/login/')
def add_watchlist(request):
    if request.method=='POST':
        try:
            # Parse the JSON data sent via AJAX and retrieve the anime ID and status
            data = json.loads(request.body)
            id = data.get('id')
            status = data.get('status')
            # Get the anime object with the given ID
            anime = Animedata.objects.get(id=id)
            # Get the current user
            user = request.user
            # Check if the anime is already in the user's watchlist
            if WatchList.objects.filter(user=user,anime=anime).exists():
                # If the anime is already in the user's watchlist, update the status
                WatchList.objects.filter(user=user, anime=anime).update(status=status)
            else:
                # Add the anime to the user's watchlist with the given status
                WatchList.objects.create(user=user,anime=anime,status=status)
            return HttpResponse({"message":"success"},status=200)
        except Exception as e:
            # Return an error message if something went wrong
            return HttpResponse({"message":f"failed {e}"},status=406)

# This view function requires the user to be authenticated, otherwise it redirects to the login page
@login_required(login_url='/login/')
def watchlists(request, status=None):
    user = request.user
    if status:
        lists = WatchList.objects.filter(user=user, status=status)
    else:
        lists = WatchList.objects.filter(user=user)

    paginator = Paginator(lists, 24)
    page_number = request.GET.get('page')
    watchlists = paginator.get_page(1) if page_number is None else paginator.get_page(page_number)

    return render(request, 'watchlist_all.html', {
        "watchlists": watchlists,
    })

@login_required(login_url='/login/')
def add_to_watchlist(request):
    anime_id = request.POST.get('id')
    status = request.POST.get('status')
    anime = Animedata.objects.get(id=anime_id)
    watchlist, created = WatchList.objects.get_or_create(user=request.user, anime=anime)
    watchlist.status = status
    watchlist.save()
    return JsonResponse({'success': True})

@login_required(login_url='/login/')
def anime_detail(request, pk):
    # Retrieve the anime with specified primary key (pk) or return 404 error
    anime = get_object_or_404(Animedata, pk=pk)
    watchlist_status= None
    if WatchList.objects.filter(user=request.user,anime=anime).exists():
        watchlist_status = WatchList.objects.get(user=request.user,anime=anime).status
    recomend = recommend(anime.genre ,anime.title)
    ratings = AnimeRating.objects.filter(user=request.user,anime=Animedata.objects.get(id=pk))
    if ratings:
        rating = ratings[0].rating
    else:
        rating = ''
    # Create a dictionary to pass the anime details and range of episodes to the template
    context = {'anime': anime,
               'episodes':range(anime.episodes),
               'rating':rating,
               "watchlist":watchlist_status,
               'recommendations':recomend[:5]}
    
    # Render the anime_detail.html template with the context dictionary
    return render(request, 'anime_detail.html', context)



def csvadd(request):
    # This function loads data from a CSV file into the database
    load()

def epsiode(request,num):
    # This function returns the episode data for the given episode number
    data = Episode.objects.filter(episode_number=num)
    return HttpResponse(data,status=200)


def average_rating(self):
        ratings = self.ratings.all()
        if ratings.count() == 0:
            return 0
        else:
            return sum(rating.rating for rating in ratings) / ratings.count()
@csrf_exempt
def submit_rating(request, anime_id, rating):
    anime = get_object_or_404(Animedata, id=anime_id)
    anime_rating, created = AnimeRating.objects.get_or_create(
        anime=anime, user=request.user,
        defaults={'rating': rating}
    )
    if not created:
        anime_rating.rating = rating
        anime_rating.save()
    average_rating = anime.average_rating
    return JsonResponse({'average_rating': average_rating})

@login_required(login_url='/login/')
def anime_list(request):#genre
    genres = [
        ('', 'All genres'),
        ('Action', 'Action'),
        ('Adventure', 'Adventure'),
        ('Sports', 'Sports'),
        ('School', 'School'),
        ('Romance', 'Romance'),
        ('Comedy', 'Comedy'),
        ('Supernatural', 'Supernatural'),
        ('Drama', 'Drama'),
        ('Shounen', 'Shounen'),
        ('Sci-Fi', 'Sci-Fi'),
        ('Historical', 'Historical'),
        ('Slice of Life', 'Slice of Life'),
        ('Fantasy', 'Fantasy'),
        ('Music', 'Music'),
        ('Shoujo Ai', 'Shoujo Ai'),
        ('Shoujo', 'Shoujo'),
    ]
    selected_genre = request.GET.get('genre')
    print(selected_genre)
    if selected_genre:
        anime = Animedata.objects.filter(genre__in=(selected_genre.split(',')))
    else:
        anime = Animedata.objects.all()
    context = {'anime': anime, 'genres': genres, 'selected_genre': selected_genre}
    return render(request, 'anime_list.html', context)

@login_required(login_url='/login/')
def deletewatch(request, id):
    watchlist = get_object_or_404(WatchList, id=id)
    watchlist.delete()
    messages.success(request, 'Watchlist item deleted successfully!')
    return redirect('watchlist')

@login_required(login_url='/login/')
def watching_view(request):
    watchlists = WatchList.objects.filter(status='Watching')
    return render(request, 'watching.html', {'watchlists': watchlists})

@login_required(login_url='/login/')
def plan_to_watch_view(request):
    watchlists = WatchList.objects.filter(status='Plan to Watch')
    return render(request, 'towatch.html', {'watchlists': watchlists})

@login_required(login_url='/login/')
def on_hold_view(request):
    watchlists = WatchList.objects.filter(status='On-Hold')
    return render(request, 'onhold.html', {'watchlists': watchlists})

@login_required(login_url='/login/')
def dropped_view(request):
    watchlists = WatchList.objects.filter(status='Dropped')
    return render(request, 'drop.html', {'watchlists': watchlists})

@login_required(login_url='/login/')
def completed_view(request):
    watchlists = WatchList.objects.filter(status='Completed')
    return render(request, 'completed.html', {'watchlists': watchlists})
