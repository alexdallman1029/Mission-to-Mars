# This is where we'll use Flask and Mongo to begin creating the web app. 

# Use flask to render a template, redirecting to another url, and creating a url.
from flask import Flask, render_template, redirect, url_for

# Use PyMongo to interact w Mongo db
from flask_pymongo import PyMongo

# To use scraping code, convert from Jupyter Notebooks to Python.
import scraping

# Set up flask
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
# app.config["MONGO_URI"] tells python app will connect to Mongo
# using a uniform resource id (URI)
# This specific URI is saying that the app can reach mongo thru local
# localhost server, port 27017, using database called mars_app
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

#set up app routes
#flask routes bind URLs to functions
#e.g., URL "ourpage.com/" brings us to the homepage of app
#and URL "ourpage.com/scrape" will activate scraping code
@app.route("/")
def index():
    # The code below uses pymongo to find "mars" collections in our db.
    # This will be created when we convert Jupyter scraping code to python script
    # Also, we assign that path to variable "mars" for later.
    mars = mongo.db.mars.fund_one()
    # The code below tells flask to return an HTML template using an index.html file,
    # which we will create after we build the flask routes
    # mars = mars tells python to use the "mars" collection in mongodb
    return render_template("index.html", mars = mars)

# Make scraping button
# This line allows us to access the db, scrape new data using scraping.py script, 
# update the db, and return a message when successful.
@app.route("/scrape")
# Define the function
def scrape():
    # Assign a new variable pointing to mongo db
    mars = mongo.db.mars
    # Create a new variable to hold newly scraped data
    # In this line, we're referencing scrape_all funtion in scraping.py file 
    # exported from Jupyter Notebooks
    mars_data = scraping.scrape_all()
    # Now that new data is added, we need to update the db using
    # .update_one(query_parameter, {"$set": data}, options)
    # This means we're inserting data but not if an identical record already exists
    # query_parameter means we can specify a field (e.g., {"new_tile":"Mars Landing Successful"})
    # in which case mongodb will update a document with a matching news_title
    # or it can be left empty {} to update the first matching document in the collection
    # Next, we'll use the data we have stored in mars_data 
    # {"$set":data} means tha the document will be modified with the data in question.
    # upsert=True tells mongo to create a new document if one doesn't already exist, 
    # and new data will always be saved (even if no doc has been created for it)
    mars.update_one({}, {"$set":mars_data}, upsert=True)
    #redirect to / where we can see the updated content
    return redirect('/', code=302)

#Tell flask to run.
if __name__ == "__main__":
    app.run()