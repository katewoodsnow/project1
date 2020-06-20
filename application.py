import os
import requests

from flask import Flask, session, request, render_template, redirect, url_for, flash, jsonify
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

@app.route("/", methods=["GET", "POST"] )
def index():

    """search for a book"""

    if request.method == "POST":

        if not request.form.get("query"):
            flash('No search was made, please use the search box to find a book', 'warning')
        
        query = request.form.get("query")

        # query database for books when user enters a character included in the book credentials. 
        rows = db.execute("SELECT * FROM books WHERE isbn iLIKE '%"+query+"%'\
         OR author iLIKE '%"+query+"%' OR title iLIKE '%"+query+"%' ORDER BY title").fetchall()

        if not rows:
            return render_template("error.html", message= "No results")

        # return possible books from books.csv file and the amount of books that match the query
        return render_template("index.html", rows=rows, search_count = len(rows))
    
    else:
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    """register user"""

    # Forget any previous user_id
    session.clear()

    # user submitted the form via post
    if request.method == "POST":

        # error checks
        if not request.form.get("username"):
            return render_template("error.html", message="Please provide a username")

        elif not request.form.get("password"):
             return render_template("error.html", message="Please provide a password")

        elif not request.form.get("confirmation"):
             return render_template("error.html", message="Please provide a password confirmation")

        # error check that password and password confirmation matched
        elif not request.form.get("password") == request.form.get("confirmation"):
             return render_template("error.html", message="Please ensure your confirmation password matches")

         # check username doesn't already exist
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": request.form.get("username")}).fetchone()

        if rows:
            return render_template("error.html", message= "This username already exists")

        # enter the users details into database by accessing and executing, generating a hash and salt for the password
        db.execute("INSERT INTO users (username, password) VALUES(:username, :password)",
                             {"username": request.form.get("username"), "password": generate_password_hash(request.form.get("password"))})
        
        #commit changes to the database
        db.commit()

        flash('Your account has been created, please log in', 'info')
         # Redirect user to home page
        return redirect("/")

    else: 
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    """user login"""

    # Forget any previous user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Check fields in the form have been entered
        if not request.form.get("username"):
            return render_template("error.html", message= "403 Please provide a username")

        elif not request.form.get("password"):
            return render_template("error.html", message= "403 Please provide a password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          { "username": request.form.get("username")}).fetchone()

        # Ensure username exists and password is correct using inbuilt password function
        if rows is None or not check_password_hash(rows.password, request.form.get("password")):
            return render_template("error.html", message= "403 Invalid username and/or password")

        # Remember which user has logged in
        session["id"] = rows.id

        session["username"] = rows.username

        # Redirect user to home page
        return redirect("/")

    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

# access the route to the particular book isbn, /book is the route isbn is the variable storing the book isbn found
# in index.html
@app.route("/book/<isbn>", methods = ["GET", "POST"])
# pass isbn into the book function
def book(isbn):

    """list details of a single book according to it's book id"""

    # select the book clicked on by the user from the database using the isbn passed in from the index.html 
    rows=db.execute("SELECT * FROM books where isbn=:isbn",
                    {"isbn": isbn}).fetchone()

    # make sure the book exists                           
    if not rows:
        return render_template("error.html", message="This book doesn't exist")

     # get book id from the database
    book_id, = db.execute("SELECT id FROM books WHERE \
                            isbn = :isbn", {"isbn": isbn}).fetchone()

    # Get goodreads rating information 
    # make a get request to the goodreads api for the particular book(the isbn) and get back a http response (the latest goodreads review information)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "9gclsKUYCJza0ItlImfQ", "isbns": isbn})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    #.json method takes the result of the request and extracts the json data (the javascript object notation data) and
    # save it in a variable called data. (json used because it is machine readable, information can then be passed between apps)
    data = res.json()
    # extract information from the json object, key is books.
    goodreads_average_rating = data["books"][0]["average_rating"]
    goodreads_work_ratings_count = data["books"][0]["work_ratings_count"]

    # if user leaves a review
    if request.method == "POST":

        # defensive design
        if not request.form.get("ratings"):
            return render_template ("error.html", message = "Please select a rating")

        if not request.form.get("description"):
            return render_template ("error.html", message = "Please write a review")
        
        # check to see if the user has already posted a review for the book
        rows2 = db.execute("SELECT * from reviews WHERE user_id = :user_id AND book_id = :book_id",
                            {"user_id": session["id"], "book_id": book_id}).fetchall()

        if rows2:
            return render_template ("error.html", message = "You have already written a review for this book")
        
        db.execute("INSERT INTO reviews (ratings, description, user_id, book_id) \
                    VALUES (:ratings, :description, :user_id, :book_id)",
                    {"ratings": request.form.get("ratings"), 
                    "description": request.form.get("description"), 
                    "user_id": session["id"],
                    "book_id": book_id })

        db.commit()
         
        flash('Your review has been created', 'info')
       

    # fetch the reviews for the book made by all the users on this app
    rows3 = db.execute("SELECT * FROM reviews JOIN users ON reviews.user_id = users.id WHERE book_id = :book_id",
                                {"book_id": book_id}).fetchall()


    return render_template("book.html", rows=rows, rows3=rows3, goodreads_average_rating = goodreads_average_rating, goodreads_work_ratings_count = goodreads_work_ratings_count)

@app.route("/api/<isbn>", methods = ["GET"])
def api(isbn):

    """API route for the application for others to gain access to the book details based on it's isbn"""

    # get the average review ratings and the number of reviews made for the particular book
    rows = db.execute("SELECT isbn, title, author, year, COUNT(reviews.id) as review_count, \
                    AVG(reviews.ratings) as average_rating FROM books INNER JOIN reviews \
                    ON books.id = reviews.book_id WHERE isbn = :isbn GROUP BY title, author, year, isbn",
                    {"isbn": isbn}).fetchone()
    
    #does the book exist in the database
    if rows is None:
        #json object wrapped in a jsonify function. this takes a python dictionary and converts it into a json object
        #and put required http headers on it that will let it have a successful json response
        return jsonify({"error": "Invalid book isbn"}), 404

    #convert query to dictionary
    results = dict(rows.items())

    # round the average ratings to 2 decimal places
    if results['average_rating']:
        results['average_rating'] = float('%.2f'%(results['average_rating']))
    
    else:
        results['average_rating'] = None

    #return the books details in machine readable code, JSON object
    return jsonify(results)
