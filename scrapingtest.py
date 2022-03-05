#Import splinter and beautiful soup, pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

# Initialize the browser, create a data dictionary, end the WebDriver and return the scraped data.
def scrape_all():
    
    #Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}

    #Double astericks(**kwargs) indicate passing x amounts of functions through the variable after the astericks
    #*args is used to pass a non-keyworded variable-length argument list to your function. 
    #**kwargs lets you pass a keyworded variable-length of arguments to your function.

    browser = Browser('chrome', **executable_path, headless = True)

    # Set variables
    news_title, news_paragraph = mars_news(browser)

    # Run scraping functions are store results in dictionary
    data = {"news_title": news_title,
            "news_paragraph": news_paragraph,
            "featured_image": featured_image(browser),
            "facts": mars_facts(),
            "last_modified": dt.datetime.now()
            }

    # Stop webdriver and return data
    browser.quit()
    return data

# Coming back in to define functions
# browser is added to function to tell Python we're using the browser variable
# that we defined outside of the function
def mars_news(browser):

    #Visit the mars nasa news site.
    url = 'https://redplanetscience.com'
    browser.visit(url)

    #Optional delay for loading the page
    #1. Searching for elements with a specific combination of tag (div) and attribute (list_text).
    #2. Waiting 1 second in between searching for components because pages can have a lot of data and be image heavy
    #(ethical scraping, doesn't overload server, already checked terms of service on redplanetscience.com)

    browser.is_element_present_by_css('div.list_text', wait_time = 1)

    #Set up the html parser
    html = browser.html

    news_soup = soup(html, 'html.parser')

    #The . is used for selecting classes, such as list_text, so the code 'div.list_text' pinpoints the <div /> tag 
    #with the class of list_text. CSS works from right to left, such as returning the last item on the list instead of the first. 
    #Because of this, when using select_one, the first matching element returned will be a <li /> element 
    #with a class of slide and all nested elements within it.

    # Upon refractoring, we will add try/except to this part of the function for error handling
    # This is useful when format of website is changed and we get an attribute error
    try:
        slide_elem = news_soup.select_one('div.list_text')

        #Chained .find onto our previously assigned variable, slide_elem. 
        #This variable holds a ton of information, so look inside of that information to find this specific data.
        #The specific data is in a <div /> with a class of 'content_title'."

        #Let's get rid of the html stuff, and only get the title text
        news_title = slide_elem.find('div', class_='content_title').get_text()
    
        # news_title (removed from here to return statement outside of function)

        #Now do the same thing for the summaries instead of the titles
        #Some notes: .find() is used when we want only the first class and attribute we've specified.
        #.find_all() is used when we want to retrieve all of the tags and attributes.
        #If we were to use .find_all() instead of .find() when pulling the summary, 
        #we would retrieve all of the summaries on the page instead of just the first one.

        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
        # news_p (removed from here to return statement outside of function)

    #If an attribute error occurs, it will return nothing instead of title and paragraph.
    except AttributeError:
        return None, None

    #return statment added to function
    return news_title, news_p


#Make a function for the images as well
def featured_image(browser):

    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find a click the "full image" button on the spaceimages-mars.com page
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html

    img_soup = soup(html, 'html.parser')

    try:
        # We can't pull the src link directly, because we want to pull the newest image on the website
        # We will instead have to use a distinguishing attribute
        # Here's the html code for reference: <img class="fancybox-image" src="image/featured/mars1.jpg" alt="">
        #Note, this is a relative link.

        img_url_rel = img_soup.find('img', class_="fancybox-image").get('src')

        # If we copy and paste this link into a browser, it won't work. 
        # This is because it's only a partial link, as the base URL isn't included.
        # Let's get the base URL from the address bar and create an absolute link.
    
    except AttributeError:
        return None
    
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

# We're using an f-string for this print statement because it's a cleaner way to create print statements; 
# they're also evaluated at run-time. This means that it, and the variable it holds, doesn't exist until 
# the code is executed and the values are not constant. 
# This works well for our scraping app because the data we're scraping is live and will be updated frequently.

# Now we're going to scrape a table of facts from a different website
# Tables in HTML are basically made up of many smaller containers. 
# The main container is the <table /> tag. 
# Inside the table is <tbody />, which is the body of the table—the headers, columns, and rows.
# <tr /> is the tag for each table row. Within that tag, the table data is stored in <td /> tags. 
# This is where the columns are established.

# Instead of scraping each row, or the data in each <td />, 
# we're going to scrape the entire table with Pandas' .read_html() function.

# The Pandas function read_html() specifically searches for and returns a list of tables found in the HTML. 
# By specifying an index of 0, we're telling Pandas to pull only the first table it encounters, 
# or the first item in the list. Then, it turns the table into a DataFrame.


def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    # A BaseException is a catchall, raised when any of the built-in exceptions are encountered 
    # and it won't handle any user-defined exceptions. We're using it here because we're using 
    # Pandas' read_html() function to pull data, instead of scraping with BeautifulSoup and Splinter.
    # The data is returned a little differently and can result in errors other than AttributeErrors.
    except BaseException: 
        return None

    df.columns=['Description','Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Pandas also has a way to easily convert our DataFrame back into HTML-ready code using the .to_html() function.

    return df.to_html()

if __name__ == "__main__":
    # If running as script, print scraped data
   print(scrape_all())

# End the automated browsing session. This is an important to add to our web app also. 
# Without it, the automated browser won't know to shut down
# It will continue to listen for instructions and use the computer's resources 
# (it may put a strain on memory or a laptop's battery if left on). 

# We can't automate the scraping using the Jupyter Notebook. 
# To fully automate it, it will need to be converted into a .py file.
# After downloading as .py, we will need to clean up the code in a text editor. 

# Info on noSQL databases, MongoDB
# JSON, JavaScript Object Notation, is a method that sorts and presents data in the form of key:value pairs. 
# It looks much like a Python dictionary and can be traversed through using list notation.
# A Mongo database contains collections. These collections contain documents, and each document contains fields, 
# and fields are where the data is stored.

# Before the code is ready for deployment, we need to integrate scraping code in a way that Flask can handle. 
# That means updating it to include functions and even some error handling. 
# This will help with our app's performance and add a level of professionalism to the end product.

