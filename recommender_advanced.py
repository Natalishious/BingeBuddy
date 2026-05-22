
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
    df["genres"].fillna("").str.replace("|", " ", regex=False)
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
            "rating": round(df.iloc[movie_index]["movielens_avg_rating"], 1), # avrunda till 1 decimal
            "similarity": round(similarity_score * 100, 1), # multiplicera med 100 för att få ett värde i %
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

    return {

        "title": movie["title"],

        "genres": movie["genres"],

        "rating": round(movie["movielens_avg_rating"], 1)
    }

# test för att se att utskrift sker korrekt i terminal
if __name__ == "__main__":

    print("=== RECOMMENDATIONS ===")

    recommendations = recommend_movies_advanced("Toy Story (1995)")

    for movie in recommendations:
        print(movie)

    print("\n=== RANDOM MOVIE ===")

    print(get_random_movie())