
'''
Lite mer avancerad recommender-funktion som tar in både genres och plot overview
Nedan är väsentligen copy-paste från recommender_prototype.ipynb och tidigare recommender-funktion
Där det finns mer utförliga kommentarer
'''

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

df = pd.read_csv("dataset/movies_cleaned.csv")

# kombinerar flera features
# fillna safeguardar mot eventuella NaN-rader i overview
df["features"] = (
    df["genres"].fillna("").str.replace("|", " ", regex=False) * 4 # viktar kategorin genres hårdare
    + " " +
    df["overview"].fillna("")
)


tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["features"])

similarity = cosine_similarity(tfidf_matrix)

def recommend_movies_advanced(movie_title):
    '''
    Tar in en titel, och om den finns i datasettet, så matchas dess features mot andra filmer
    och ger tillbaka en lista med de 25 mest liknande, rankad efter simularity
    '''

    if movie_title not in df["title"].values:
        return [] # tom lista, får hanteras i jinja
    
    idx = df[df["title"] == movie_title].index[0] # hämtar indexet för den film användaren angav (om filmen finns)

    # hämtar alla similarity scores för angiven film
    # och skapar en lista som med enumerate blir: (film_index, similarity score)
    # ex: [(0, 1.0), (1, 0,5), (2, 0.6), ...]
    sim_scores = list(enumerate(similarity[idx])) 

    # x: x[1] -> similiarity score (x[0] är indexet som det ligger på)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True) # sorterar dessa i fallande ordning efter similarity score

    # tar bort input-filmen från listan, så att den inte kan rekommendera sig själv
    filtered_scores = []
    for score in sim_scores:
        if score[0] != idx:
            filtered_scores.append(score)
    sim_scores = filtered_scores
    sim_scores = sim_scores[:25] # 25 första

    # safeguard
    if not sim_scores:
        return []
    
    # hämtar film (index, score) med högst score
    max_score = sim_scores[0][1]

    # lägger indexet för ovan filmer i en egen lista
    # movie_indices = []
    # for i in sim_scores:
    #     movie_indices.append(i[0])

    # vi kan också skicka tillbaka en lista med dictionaries för titel, similarity score, betyg, bildlänk o.s.v.
    results = []
    for movie in sim_scores:
        movie_index = movie[0] # filmens index
        similarity_score = movie[1] # filmens similarity score
        poster_path = df.iloc[movie_index]["poster_path"] # hämtar TMDBs relativa sökväg för posterbild

        # safeguard om Nan-rad i poster-länk i datasetet
        if pd.notna(poster_path): 
            poster_url = "https://image.tmdb.org/t/p/w500" + str(poster_path) # lägger till relativ sökväg
        else:
            poster_url = None

        results.append({
            "title": df.iloc[movie_index]["title"],
            "genres": df.iloc[movie_index]["genres"],
            "rating": round(df.iloc[movie_index]["movielens_avg_rating"], 1), # avrunda till 1 decimal
            # "similarity": round(similarity_score * 100, 1), # multiplicera med 100 för att få ett värde i %
            "similarity": round((similarity_score / max_score) * 100, 1), # ger relativ ranking istället
            "poster": poster_url # url till filmens poster i jpg-format
        })

    return results


def get_random_movie():
    '''
    Filtrerar samtliga filmer i datasetet med en rating som är 4 eller högre,
    och skickar tillbaka titel + genre + rating
    '''
    high_rated = df[df["movielens_avg_rating"] >= 4] # hämtar alla filmer med score 4 eller högre

    movie = high_rated.sample(1).iloc[0] # väljer ut (1) rad på måfå bland filtrerade filmer

    poster_path = movie["poster_path"]

    if pd.notna(poster_path):
        poster_url = ("https://image.tmdb.org/t/p/w500" + str(poster_path))
    else:
        poster_url = None # safeguard

    return {

        "title": movie["title"],

        "genres": movie["genres"],

        "rating": round(movie["movielens_avg_rating"], 1),

        "overview": movie["overview"],

        "poster": poster_url
    }

def recommend_from_favorites(favorite_titles):
    '''
    Tar in en lista med samtliga filmer i användarens "favoriter",
    hämtar deras index och similarity scores, sumerar poängen och
    returnerar de X antal (10) filmer med högst poäng
    '''
    total_scores = {} # index: sim_score
    
    for title in favorite_titles: # loopa igenom favoritfilmer

        if title not in df["title"].values: # safeguard
            continue

        idx = df[df["title"] == title].index[0] # hämta index från favoritfilm
        sim_scores = similarity[idx] # hämta similarity score för denna film

        for movie_index, score in enumerate(sim_scores): # för varje filmindex och poäng
            movie_title = df.iloc[movie_index]["title"] # om filmen finns bland favorittitlar, hoppa över
            
            if movie_title in favorite_titles: # hoppa över filmer användaren redan gillar
                continue

            if movie_index in total_scores: # om filmen redan finns:
                total_scores[movie_index] += score # lägg till index och score eller plussa på score

            else: # annars skapa ny entry
                total_scores[movie_index] = score
    
    # sortera efter högst total score
    sorted_movies = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    sorted_movies = sorted_movies[:20] # bara de tjugo högst rankade

    # safeguard
    if not sorted_movies:
        return []

    # testar detta so malternativ metod för att visa "score"
    max_score = sorted_movies[0][1]

    # bygg lista med titel, betyg, poster path et.c. för jinja
    results = []
    for movie_index, score in sorted_movies:
        poster_path = df.iloc[movie_index]["poster_path"]
        if pd.notna(poster_path):
            poster_url = ("https://image.tmdb.org/t/p/w500" + str(poster_path))
        else:
            poster_url = None # safeguard
        
        results.append({
            "title": df.iloc[movie_index]["title"],
            "genres": df.iloc[movie_index]["genres"],
            "rating": round(df.iloc[movie_index]["movielens_avg_rating"], 1),
            # "similarity": round(score * 100, 1), # bortkommenterad för nu
            # "similarity": round((score / len(favorite_titles)) * 100, 1), # ger tillbaka medelvärdet i % med 1 decimal
            "similarity": round((score / max_score) * 100, 1), # ger oss relativ matchningspoäng
            "poster": poster_url
        })
        
    return results



def get_all_movies():
    

    l1=[[],[],[],[]]

    for i in df['title']:
        l1[0].append(i)
    
    for i in df['genres']:
        l1[1].append(i)
    
    for i in df['movielens_avg_rating']:
        x=round(i,1)
        l1[2].append(x)

    for i in df['poster_path']:
        if pd.notna(i):
            poster_url = "https://image.tmdb.org/t/p/w500" + str(i)
        else:
            poster_url = None

        l1[3].append(poster_url)
    

    return l1






# test för att se att utskrift sker korrekt i terminal
if __name__ == "__main__":

    print("=== RECOMMENDATIONS ===")

    recommendations = recommend_movies_advanced("Toy Story (1995)")

    for movie in recommendations:
        print(movie)

    print("\n=== RANDOM MOVIE ===")

    print(get_random_movie())