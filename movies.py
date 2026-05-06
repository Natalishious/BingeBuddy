import random

def movies():
    movies = [
    "The Godfather",
    "Pulp Fiction",
    "The Shawshank Redemption",
    "Forrest Gump",
    "Fight Club",
    "Inception",
    "The Matrix",
    "Mad Max: Fury Road",
    "Interstellar",
    "John Wick",
    "Superbad",
    "The Hangover",
    "Step Brothers",
    "Anchorman",
    "Groundhog Day",
    "The Conjuring",
    "Hereditary",
    "Get Out",
    "A Quiet Place",
    "The Shining",
    "The Green Mile",
    "Whiplash",
    "Parasite",
    "Joker",
    "La La Land",
    "Spirited Away",
    "Toy Story",
    "The Lion King",
    "Wall-E",
    "Into the Spider-Verse",
    "Oldboy",
    "City of God",
    "Amélie",
    "Pan's Labyrinth",
    "Memento",
    "Donnie Darko",
    "The Truman Show",
    "Everything Everywhere All at Once"
]
    
    x = random.randint(0,len(movies)-1)
    return movies[x]
    
    
def genras():   
    genras = [
    "Inception", 
    "sci-fi",
    "Fantasy", 
    "comedy",
    "Hereditary", 
    "horror",
    "Thriller"
]
    
    y = random.randint(0,len(genras)-1)

    return genras[y]

def rating():
    x=random.randint(0,10)
    y=random.randint(0,9)

    o=f'{x}.{y}'
    float(o)

    return o