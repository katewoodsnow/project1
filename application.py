import os

from flask import Flask, session, request, render_template, redirect, url_for, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    # user submitted the form via post
    if request.method == "POST":

        # error check that user filled out the username field
        if not request.form.get("username"):
            return render_template("error.html", message="Please provide a username")

        # error check that user filled out password field
        elif not request.form.get("password"):
             return render_template("error.html", message="Please provide a password")

        # error check that user filled out password confirmation field
        elif not request.form.get("confirmation"):
             return render_template("error.html", message="Please provide a password confirmation")

        # error check that password and password confirmation matched
        elif not request.form.get("password") == request.form.get("confirmation"):
             return render_template("error.html", message="Please ensure your confirmation password matches")

         # check username doesn't already exist
        username = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": request.form.get("username")}).fetchone()

        if username:
            return render_template("error.html", message= "This username already exists")

        # enter the users details into database by accessing and executing generating a hash and salt for the password
        results = db.execute("INSERT INTO users (username, password) VALUES(:username, :password)",
                             {"username": request.form.get("username"), "password": generate_password_hash(request.form.get("password"))})
        
        #commit changes to the database
        db.commit()

        flash('Your account has been created', 'info')
         # Redirect user to home page
        return redirect("/")

    else: 
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message= "403 Please provide a username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message= "403 Please provide a password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          { "username": request.form.get("username")}).fetchone()

        # Ensure username exists and password is correct
        if rows is None or not check_password_hash(rows.password, request.form.get("password")):
            return render_template("error.html", message= "403 Invalid username and/or password")

        # Remember which user has logged in
        session["id"] = rows.id

        session["username"] = rows.username

        # Redirect user to home page
        return redirect("/")

    return render_template("login.html")
