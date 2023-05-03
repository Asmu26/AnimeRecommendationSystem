from django.shortcuts import render, redirect, HttpResponse,get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages 
from django.contrib.auth.models import User 
from django.contrib.auth.decorators import login_required
from django.contrib.auth  import authenticate,  login, logout
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
        similar_anime = df[['title', 'id']].iloc[anime_indices]
        similar_anime_dict = similar_anime.to_dict('records')
        return similar_anime_dict

    similar_anime_dict = get_recommendations(cosine_sim, data, title)
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
    if request.method=="POST":
        # Get the post parameters
        username=request.POST['username']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        # check for erroneous input
        if len(username)<5:
            # If username is less than 5 characters, redirect to signup page
            return redirect('signup')

        if (pass1!= pass2):
            # If passwords do not match, redirect to signup page
             return redirect('signup')

        # Check if the user already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            # Return an error message and redirect to signup page
            messages.error(request, 'User already exists')
            return redirect('signup')
        else:
            # Create a new user with the provided credentials
            myuser = User.objects.create_user(username=username, email=email, password=pass1)
            myuser.save()
            # Show success message and redirect to login page
            messages.success(request, " Your Anime account has been successfully created")
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
        if user is not None and user.is_authenticated:
            # Log the user in and redirect them to the home page
            login(request, user)
            messages.success(request, "Successfully logged in")
            return redirect("home")
        else:
            # Display an error message and redirect them back to the login page
            messages.error(request, "Invalid credentials! Please try again")
            return redirect("login")

    # If the request method is GET, display the login page
    return render(request, 'login.html')

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
def watchlists(request,anime_id):
    # Get the anime object with the given ID
    try:
        anime = Animedata.objects.get(id=anime_id)
    except Animedata.DoesNotExist:
        return HttpResponse("Anime not found.", status=404)
    
     # Check if the anime is already in the user's watchlist
    try:
        watchlists = WatchList.objects.get(user=user,anime=anime)
    except WatchList.DoesNotExist:
        watchlists = None
    # Get the current user
    user = request.user
    # Get all the anime in the user's watchlist
    lists = WatchList.objects.filter(user=user)
    paginator = Paginator(lists, 24) 
    page_number = request.GET.get('page')
    watchlists = paginator.get_page(1)  if page_number is None else paginator.get_page(page_number)
    return render(request, 'watchlist_all.html', {"watchlists":watchlists})

@login_required(login_url='/login/')
def edit_watchlist(request, watchlist_id):
    # Get the watchlist object with the given ID
    try:
        watchlist = WatchList.objects.get(id=watchlist_id)
    except WatchList.DoesNotExist:
        return HttpResponse("Watchlist item not found.", status=404)
    
    # Check if the user is the owner of the watchlist item
    if watchlist.user != request.user:
        return HttpResponse("You are not authorized to edit this watchlist item.", status=403)
    
    if request.method == 'POST':
        # Parse the new status from the POST request
        new_status = request.POST.get('status')
        
        # Update the watchlist object with the new status
        watchlist.status = new_status
        watchlist.save()
        
        return redirect('watchlists', anime_id=watchlist.anime.id)
    
    # If the request method is GET, render the edit watchlist template
    return render(request, 'edit_watchlist.html', {'watchlist': watchlist})



@login_required(login_url='/login/')
def anime_detail(request, pk):
    # Retrieve the anime with specified primary key (pk) or return 404 error
    anime = get_object_or_404(Animedata, pk=pk)
    watchlist_status= None
    if WatchList.objects.filter(user=request.user,anime=anime).exists():
        watchlist_status = WatchList.objects.get(user=request.user,anime=anime).status
    recomend = recommend(anime.genre ,anime.title)
    # Create a dictionary to pass the anime details and range of episodes to the template
    context = {'anime': anime,
               'episodes':range(anime.episodes),
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

def submit_rating(request, anime_id, rating):
    anime = get_object_or_404(Animedata, id=anime_id)
    anime_rating, created = AnimeRating.objects.get_or_create(
        anime=anime, user=request.user,
        defaults={'rating': rating}
    )
    if not created:
        anime_rating.rating = rating
        anime_rating.save()
    average_rating = anime.average_rating()
    return JsonResponse({'average_rating': average_rating})

def anime_list(request):
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
    selected_genre = request.GET.get('genre', '')
    if selected_genre:
        anime = Animedata.objects.filter(genre__icontains=selected_genre)
    else:
        anime = Animedata.objects.all()
    context = {'anime': anime, 'genres': genres, 'selected_genre': selected_genre}
    return render(request, 'anime_list.html', context)
