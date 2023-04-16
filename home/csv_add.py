import csv
from .models import Animedata
def load():
    with open('C:\\Users\\acer\\Dropbox\\My PC (LAPTOP-SC5AQCHT)\\Downloads\\animes\\newAnimes2.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data = Animedata.objects.create(
                title=row['title'],
                synopsis=row['synopsis'],
                genre=row['genre'],
                aired=row['aired'],
                episodes=int(float(row['episodes'])),
                popularity=row['popularity'],
                ranked=int(float(row['ranked'])),
                score=row['score'],
                img_url=row['img_url'],
                link=row['link']
            )