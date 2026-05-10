from flask import Flask, redirect, render_template, request, url_for
from database import init_db, create_user, get_user
from movies import movies, genras, rating

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


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home/home.html", x=x, y=y, o=o)

@app.route('/2nd')
def recomendation():
    return render_template('inlogsida/2nd.html')

@app.route('/about')
def about():
    return render_template('about/about.html')


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
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Hämtar user från databasen
        user = get_user(username)

        # user finns och lösenord matchar
        if user and user["password"] == password:
            return redirect(url_for('recomendation'))

        return "Fel username eller password"

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
