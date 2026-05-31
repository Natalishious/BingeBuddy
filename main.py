from flask import Flask, redirect, render_template, request, url_for, session
from database import init_db, create_user, get_user, get_favorites, add_favorite, remove_favorite
from movies import movies, genras, rating
from recommender import recommend_movies, df
from recommender_advanced import recommend_movies_advanced, get_random_movie, recommend_from_favorites, get_all_movies
import pandas as pd
import math


init_db()  # Skapar db

# Lägger till användare:
success = create_user("Jimpan", "test123")
print(f"User created: {success}!")

# Hämta användare
user = get_user("Jimpan")
print(f"User retrieved: {user}")

x = movies()
y = genras()
o = rating()

# laddar in aktuellt dataset
df = pd.read_csv("dataset/movies_cleaned.csv")

app = Flask(__name__)
# Secret key
app.secret_key = "SECRET_KEY"


@app.route("/")
def home():

    recently = get_random_movie()

    return render_template(
        "home/home.html",
        recently=recently,
        # Skickar med username här så man kan visa i HTML om någon är inloggad
        username=session.get("username")
    )


@app.route('/2nd', methods=["GET", "POST"])
def recomendation():
    '''
    Skickar en request med titel och hämtar en lista med de mest liknande filmerna
    '''
    recommendations = []  # container
    if request.method == "POST":  # detta block körs endast om användaren klickar
        # hämta det användaren skrev i input-field
        movie_title = request.form.get("movie_title")
        # anropar ML-funktionen och ge tillbaka en lista
        recommendations = recommend_movies_advanced(movie_title)

    return render_template('inlogsida/2nd.html',
                           recommendations=recommendations,  # för jinja
                           # SAMTLIGA filmtitlar för t.ex. autofill i input-field
                           movies=df["title"].tolist(),
                           username=session.get("username"))


@app.route('/about')
def about():
    return render_template('about/about.html', username=session.get("username"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if not username or not password:
            return "Fyll i username och password!"

        created = create_user(username, password)
        if created:
            # Går tillbaka till home och skapad
            return redirect(url_for("home"))
        else:
            return "Username doesn not exist!"
    return render_template("register.html", username=session.get("username"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Hämtar user från databasen
        user = get_user(username)

        # user finns och lösenord matchar
        if user and user["password"] == password:
            session["username"] = username
            return redirect(url_for("profile"))
        return "Fel username eller password!"

    return render_template("login.html", username=session.get("username"))


@app.route("/logout")
def logout():
    # Tar bort user från session när man loggar ut
    session.pop("username", None)
    return redirect(url_for("home"))

# ====================
# profil-baserad logik
# ====================


@app.route("/profile")
def profile():

    if "username" not in session:
        return redirect(url_for("login"))

    user = get_user(session["username"])
    favorites = get_favorites(user["id"])  # hämtar listan med favoriter
    favorite_movies = []  # place holder för titel, rating, länkar

    # loopa igenom favoriterna och hämta titel, rating och länkar
    for row in favorites:
        title = row["movie_title"]
        movie_data = df[df["title"] == title].iloc[0]

        # bygger poster-url
        poster_path = movie_data["poster_path"]

        if pd.notna(poster_path):  # alltså bara om det inte är en null-rad
            poster_url = "https://image.tmdb.org/t/p/w500" + str(poster_path)

        else:
            poster_url = None

        favorite_movies.append({
            "title": movie_data["title"],
            "genres": movie_data["genres"],
            "rating": round(movie_data["movielens_avg_rating"], 1),
            "poster": poster_url
        })

    # bygger lista med favorittitlar och kallar på recommender-funktionen
    favorite_titles = []
    for row in favorites:
        favorite_titles.append(row["movie_title"])
    recommended_movies = recommend_from_favorites(favorite_titles)

    return render_template(
        "profile.html",
        user=user,
        favorites=favorites,
        movies=df["title"].tolist(),
        favorite_movies=favorite_movies,
        recommended_movies=recommended_movies,
        username=session.get("username")
    )


@app.route("/add_favorite", methods=["POST"])
def add_favorite_route():
    # lägger till favoritfilm för den inloggade användaren
    if "username" not in session:
        return redirect(url_for("login"))

    movie_title = request.form.get("movie_title")
    user = get_user(session["username"])
    add_favorite(user["id"], movie_title)

    return redirect(url_for("profile"))


@app.route("/remove_favorite", methods=["POST"])
def remove_favorite_route():
    # tar bort favoritfilm för den inloggade användaren via en knapp i listan med favoriter
    if "username" not in session:
        return redirect(url_for("login"))

    movie_title = request.form.get("movie_title")
    user = get_user(session["username"])
    remove_favorite(user["id"], movie_title)

    return redirect(url_for("profile"))
# =========================
# Profil-baserad logik slut
# =========================

@app.route('/sökmotor')
def sökmotor():
    
    l1 = get_all_movies()

    # Convert columns into rows
    movies = list(zip(l1[0], l1[1], l1[2]))

    # Get search query
    q = request.args.get("q", "").strip()

    # Filter movies if a search query exists
    if q:
        q_lower = q.lower()

        movies = [
            movie for movie in movies
            if q_lower in movie[0].lower()      # title
            or q_lower in movie[1].lower()      # genre
            or q == str(movie[2])               # rating
        ]

    # Pagination
    page = request.args.get("page", 1, type=int)
    per_page = 100

    start = (page - 1) * per_page
    end = start + per_page

    paginated_movies = movies[start:end]

    total_pages = math.ceil(len(movies) / per_page)

    return render_template(
        "sökmotor.html",
        movies=paginated_movies,
        page=page,
        total_pages=total_pages,
        q=q
    )


if __name__ == "__main__":
    app.run(debug=True)
