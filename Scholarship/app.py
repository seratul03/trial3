from flask import Flask, render_template
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from data.scholarships import scholarships

@app.route("/")
def index():
    return render_template("index.html", scholarships=scholarships)

@app.route("/detail")
def detail():
    return render_template("detail.html")

if __name__ == "__main__":
    app.run(debug=True)
