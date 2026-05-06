from flask import Flask, render_template
from faker import Faker
from movies import movies, genras, rating





x = movies()
y = genras()
o = rating()




app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home/home.html", x=x, y=y,o=o)

if __name__ == "__main__":
    app.run(debug=True)