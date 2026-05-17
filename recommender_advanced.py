
'''
Lite mer avancerad recommender-funktion som tar in både genres och plot overview
Nedan är väsentligen copy-paste från recommender_prototype.ipynb och tidigare recommender-funktion
Där det finns mer utförliga kommentarer
'''

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    och ger tillbaka en lista med de 5 mest liknande
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

    sim_scores = sim_scores[:5] # fem första

    # lägger indexet för ovan filmer i en egen lista
    movie_indices = []
    for i in sim_scores:
        movie_indices.append(i[0])

    # vi kan också skicka tillbaka en lista med dictionary innehållande titel och movie rating för enkel visning i html
    results = []
    for i in movie_indices:
        results.append({
            "title": df.iloc[i]["title"],
            "rating": round(df.iloc[i]["movielens_avg_rating"], 1) # avrunda till 1 decimal
        })

    return results
