# Project 1

Web Programming with Python and JavaScript

Project1 CS50W - Book Search Application

This application allows the user to search for a book, write and read reviews for a particular book, see the average and total number of ratings for that book imported from the goodreads API and for others to access this applications API.

The languages and tools used are HTML, CSS, SASS, Python, FLASK, JINJA2, POSTGRESQL

There are 5 html pages.

Home page: Includes link buttons to register and login pages if the user is not logged in. If the user is logged in, it has a search box where a book can be searched by it's author, title or isbn number. The book can be found by only typing in part of the book's credentials. Once a search has been made, a list of books is shown, the user can select which book they want.

Register page: The user can type in their details to register which get's stored into the database in a users table, the password is hashed. Incorporating defensive design to make sure all fields are filled in and the username is unique, if an error is made the error.html page is rendered to display a message to the user.

Login page: The user can input their username and password, this selects the user from the users table and logs them in.

Book page: The book's details and image of the front page, chosen from the search results in the index page is displayed. The user can see reviews left by other users on the application. Average and number of ratings left by goodreads' users is imported from the goodreads' API and there is a form which allows the user to leave a review on that book.

Layout file: This is the basic layout the website has on each page, other pages can extend from this. It includes the basic layout template for all other pages.

It has a book cvs file which includes all the books that are imported into the database by the import.py file.

Access to the application's own api can be made by making a http get request to the api and the particular isbn number for the book you want to access details for.

The user can logout once finished.

Each page has a navigation bar with links to logout and index page, if logged in. A register, login and index page link if the user is not logged in, a footer with links to an email and phone number. The layout is based on bootstrap grids.

There is also a static folder which includes images for the headers, a css style file and a scss file.
