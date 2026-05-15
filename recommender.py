
'''
Enkel recommender-funktion
Nedan är väsentligen copy-paste från recommender_prototype.ipynb
Där det finns mer utförliga kommentarer
'''

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


df = pd.read_csv("data/movies_cleaned_old.csv")



df["features"] = df["genres"].str.replace("|", " ", regex=False)

tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["features"])

similarity = cosine_similarity(tfidf_matrix)

def recommend_movies(movie_title):
    '''
    Tar in en titel, och om den finns i datasettet, så matchas dess features mot andra filmer
    och ger tillbaka en lista med de 5 mest liknande
    '''

    if movie_title not in df["title"].values:
        return "Movie not found"
    
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

    sim_scores = sim_scores[:5] # fem första

    # gammal kod
    # sim_scores = sim_scores[1:6] # hoppar över första filmen (som användaren angav) och ger tillbaka de nästkommande 5 högst rankade

    # lägger indexet för ovan filmer i en egen lista
    movie_indices = []
    for i in sim_scores:
        movie_indices.append(i[0])

    # använder ovan index för att med iloc lokalisera och returnera titlarna som en lista
    return df["title"].iloc[movie_indices].tolist() 