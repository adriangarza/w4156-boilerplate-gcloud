from __future__ import print_function
from google.appengine.ext import vendor
import os
import re
from code.user import User, Form
from code.listing import *
from datetime import timedelta

vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
from flask import Flask, make_response, request, url_for, redirect, render_template, json
import MySQLdb


# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ['CLOUDSQL_CONNECTION_NAME']
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

app = Flask(__name__, template_folder=tmpl_dir)

from google.appengine.api import users

schools = {"cc" : 'Columbia College', "barnard" : 'Barnard', "seas" : 'SEAS', "general_studies" : 'General Studies'}

def connect_to_cloudsql():

    # When deployed to App Engine, the `SERVER_SOFTWARE` environment variable
    # will be set to 'Google App Engine/version'.
    if os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
        # Connect using the unix socket located at
        # /cloudsql/cloudsql-connection-name.
        cloudsql_unix_socket = os.path.join(
            '/cloudsql', CLOUDSQL_CONNECTION_NAME)

        db = MySQLdb.connect(
            unix_socket=cloudsql_unix_socket,
            user=CLOUDSQL_USER,
            passwd=CLOUDSQL_PASSWORD)

    # If the unix socket is unavailable, then try to connect using TCP. This
    # will work if you're running a local MySQL server or using the Cloud SQL
    # proxy, for example:
    #
    #   $ cloud_sql_proxy -instances=your-connection-name=tcp:3306
    #
    else:
        # just connect directly to cloud SQL lul
        db = MySQLdb.connect(
            host='35.227.27.169', user=CLOUDSQL_USER, passwd=CLOUDSQL_PASSWORD)

    return db


@app.route('/databases')
def showDatabases():
    """Simple request handler that shows all of the MySQL SCHEMAS/DATABASES."""

    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('SHOW SCHEMAS')

    res = ""
    for r in cursor.fetchall():
        res += ('{}\n'.format(r[0]))

    response = make_response(res)
    response.headers['Content-Type'] = 'text/json'

    # disconnect from db after use
    db.close()

    return response


@app.route('/', methods=['POST'])
def create_user():
    error = None

    f_name = request.form['first_name_field']
    l_name = request.form['last_name_field']
    school = request.form['school_field']
    year = int(request.form['year_field'])
    interests = request.form['interests_field']
    curr_user = users.get_current_user()
    uni = email_to_uni(curr_user.email())

    # connect to db
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use cuLunch')

    # check if uni is already registered
    registered = check_registered_user(uni)

    form_input = Form(f_name, l_name, uni, school, year, interests)
    user_check, error = form_input.form_input_valid()

    print (form_input.uni + " " + form_input.f_name + " " + form_input.l_name + " " + form_input.school +
            " " + form_input.interests + " " + form_input.school)

    '''if not user_check:
        error = error
        db.close()'''


    if user_check and not registered:

        name = form_input.f_name + ' ' + form_input.l_name
        # else send error to user

        # store in database
        insert_query = "INSERT INTO users VALUES ('%s', '%s', '%d', '%s', '%s')" % (uni, name, year, interests, school)
        # print('query generated')
        print(insert_query)

        try:
            cursor.execute(insert_query)
            # commit the changes in the DB
            db.commit()
        except:
            # rollback when an error occurs
            db.rollback()
            print("USERS Insert failed!")

        # disconnect from db after use
        db.close()
        return redirect(url_for('output'))

    elif not user_check and error == 'empty':
        error = 'Empty answer in one field'
        db.close()

    elif registered:
        error = 'This UNI has been registered already.'
        db.close()

    else:
        # return redirect(url_for('static', filename='index.html', error=error))
        db.close()

    return render_template('index.html', error=error)


@app.route('/', methods=['GET'])
def landing_page():
    curr_user = users.get_current_user()
    if curr_user:
        logout_url = users.create_logout_url('/')

        # then check if it's a valid uni and they have an account
        if valid_uni(curr_user.email()):
            # if they have an account
            if check_registered_user(email_to_uni(curr_user.email())):
                # redirect them to the listings page for their user
                return redirect("/listings")
            else:
                # render the account creation page
                return render_template("index.html",
                                       account_creation=True,
                                       user_logged_in=True,
                                       logout_url=logout_url,
                                       uni=email_to_uni(curr_user.email()))

        else:
            # then immediately log them out (unauthorized email)
            return redirect(logout_url)

    else:
        login_url = users.create_login_url('/')
        return render_template("index.html", user_logged_in=False, login_url=login_url)


@app.route('/listform', methods=['POST'])
def create_listing():
    error = None
    user = users.get_current_user()
    uni = email_to_uni(user.email())
    cafeteria = request.form['Cafeteria']
    date = request.form['date']
    time = request.form['time']
    needSwipe = request.form.get('needswipe') != None
    # print(cafeteria, timestamp, needSwipe)

    # store in database
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use cuLunch')

    listform_input = ListForm(cafeteria, date, time, needSwipe)
    listing_check, error = listform_input.listform_datetime_valid()

    if listing_check: 

        expirytime = date + " " + time
        query = "INSERT INTO listings VALUES ('%s', '%s', '%d', '%s')" % (expirytime, uni, needSwipe, cafeteria)
        # print('query generated')
        print(query)

        try:
            cursor.execute(query)
            # commit the changes in the DB
            db.commit()
        except:
            # rollback when an error occurs
            db.rollback()
            print("LISTINGS Insert failed!")

        # disconnect from db after use
        db.close()
        return redirect(url_for('output'))

    elif not listing_check and error == 'empty':
        error = 'Empty answer in one field'
        db.close()

    elif not listing_check and error == 'bad time':
        error = cafeteria + " is not open at the time selected"
        db.close()

    elif not listing_check and error == 'past time':
        error = 'You chose a time or date of the past'
        db.close()

    else:
        db.close()

    return render_template('/listform/index.html', error=error)


@app.route("/listform", methods=["GET"])
def show_listform():
    user = users.get_current_user()
    if user:
        return render_template('/listform/index.html')
    else:
        login_url = users.create_login_url('/')
        return render_template("index.html", user_logged_in=False, login_url=login_url)



@app.route('/listings', methods=["GET"])
def output():
    user = users.get_current_user()

    # can't see listings if you don't have an account :^)
    if not user or not check_registered_user(email_to_uni(user.email())):
        return redirect("/")

    # then fetch the listings
    # TODO: make this a self-contained function to get listings of not a current UNI?
    uni = email_to_uni(user.email())

    
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use cuLunch')

    # grab the relevant information and make sure the user doesn't see their own listings there
    query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName, l.expiryTime, l.needsSwipes, l.Place from " \
            "users u JOIN listings l ON u.uni=l.uni WHERE NOT u.uni = '{}' ORDER BY l.expiryTime".format(uni)

    me = find_user(uni)
    try:
        cursor.execute(query)
        
    except:
        print("SELECT for listings failed!")
        
    swipes = 0
    num_listings = 0
    posts = []
    for r in cursor.fetchall():
        u = User(r[0], r[1], r[2], r[3], r[4])
        # we need to convert datetime into a separate date and time for the listing object
        l = Listing(r[5], r[0], r[7], r[6])
        if l.expiryDateTime > (datetime.datetime.now() - timedelta(hours=4)):
            num_listings += 1
            if l.needSwipe:
                swipes += 1
            posts.append(ListingPost(l, u))
        print(str(l.expiryDateTime) + " ")

    db.close()
    d = get_popular_place()
    best_hall = d["place"]
    best_count = d["count"]

    # serve index template
    return render_template('/listings/index.html', numlistings = num_listings, swipes=swipes, current_user=me,
                           listingposts=posts, name=user.nickname(), logout_link=users.create_logout_url("/"),
                           best_hall=best_hall, best_count=best_count)

  
def valid_uni(email):
    if re.match("\S+@(columbia|barnard)\.edu", email) is not None:
        return True
    else:
        return False

@app.route('/listings', methods=["POST"])
def search_listings():

    cafeteria = request.form['Cafeteria']
    show_swipe_needers = request.form.get ('swipe_needers') != None
    show_swipe_offerers = request.form.get ('swipe_offerers') != None

    if show_swipe_needers:
        print("Showing swipe needers")
    if show_swipe_offerers:
        print("Showing swipe offerers")

    user = users.get_current_user()

    # can't see listings if you don't have an account :^)
    if not user or not check_registered_user (email_to_uni (user.email ())):
        return redirect("/")

    # then fetch the listings
    # TODO: make this a self-contained function to get listings of not a current UNI?

    if not show_swipe_needers and not show_swipe_offerers and (cafeteria == '' or cafeteria == 'All Cafeterias'):
        return redirect("/listings")
    elif show_swipe_needers and show_swipe_offerers and (cafeteria == '' or cafeteria == 'All Cafeterias'):
        return redirect("/listings")
    else:
        uni = email_to_uni(user.email())

        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('use cuLunch')
        # grab the relevant information and make sure the user doesn't see their own listings there
        # TODO: determine whether the user should actually see their own listings (would let us consolidate code)

        if (cafeteria == '' or cafeteria == 'All Cafeterias') and show_swipe_offerers:
            query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName, l.expiryTime, l.needsSwipes, l.Place from " \
                    "users u JOIN listings l ON u.uni=l.uni WHERE l.needsSwipes=0 AND NOT u.uni = '{}'".format(uni)

        elif (cafeteria == '' or cafeteria == 'All Cafeterias') and show_swipe_needers:
            query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName, l.expiryTime, l.needsSwipes, l.Place from " \
                    "users u JOIN listings l ON u.uni=l.uni WHERE l.needsSwipes=1 AND NOT u.uni = '{}'".format(uni)

        if cafeteria != '' and cafeteria != 'All Cafeterias' and show_swipe_needers:
            query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName, l.expiryTime, l.needsSwipes, l.Place from " \
                "users u JOIN listings l ON u.uni=l.uni WHERE l.Place = '{}' AND l.needsSwipes=1 AND NOT u.uni = '{}'".format(cafeteria, uni)

        elif cafeteria != '' and cafeteria != 'All Cafeterias' and show_swipe_offerers:
            query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName, l.expiryTime, l.needsSwipes, l.Place from " \
                    "users u JOIN listings l ON u.uni=l.uni WHERE l.Place = '{}' AND l.needsSwipes=0 AND NOT u.uni = '{}'".format(
                    cafeteria, uni)

        elif cafeteria != '' and cafeteria != 'All Cafeterias':
            query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName, l.expiryTime, l.needsSwipes, l.Place from " \
                "users u JOIN listings l ON u.uni=l.uni WHERE l.Place = '{}' AND NOT u.uni = '{}'".format(cafeteria, uni)

        me = find_user(uni)
        try:
            cursor.execute(query)
        
        except:
            print("SELECT for listings failed!")

        loc_swipes = 0
        loc_num_listings = 0
        posts = []
        for r in cursor.fetchall():
            u = User(r[0], r[1], r[2], r[3], r[4])
            # we need to convert datetime into a separate date and time for the listing object
            l = Listing(r[5], r[0], r[7], r[6])
            if l.expiryDateTime > datetime.datetime.now():
                posts.append(ListingPost(l, u))
                print(str(l.expiryDateTime) + " ")
                loc_num_listings += 1
                if l.needSwipe:
                    loc_swipes += 1

        db.close()

        # serve index template
        return render_template('/listings/index.html', locnumlistings=loc_num_listings,
                               locswipes=loc_swipes, place=cafeteria, current_user=me,
                               listingposts=posts, name=user.nickname(),logout_link=users.create_logout_url("/"), needs=show_swipe_needers,
                               offers=show_swipe_offerers)


def check_registered_user(uni):
    """ 
    Given an email, checks if it corresponds to a registered user in the database 
    If user is registered, this function returns True; otherwise, it returns False

    """

    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use cuLunch')

    query = "SELECT * FROM users WHERE users.uni = '{}'".format(uni)
    
    try:
        cursor.execute(query)
        
    except:
        print("SELECT for checking registered users failed!")


    if not cursor.rowcount:
        db.close()
        return False
    else:
        db.close()
        return True


def email_to_uni(email):
    """parse emails to retrieve UNIs"""
    return email.split('@')[0]

def get_user_info():
    """
    gets the user info from the database from a uni
    returns a new User object

    """
    user = users.get_current_user()
    uni = email_to_uni(user.email())

    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use cuLunch')

    
    query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName FROM users u WHERE u.uni='{}'".format(uni)
    
    try:
        cursor.execute(query)
        
    except:
        print("SELECT for getting user info failed!")

    if not cursor.rowcount:
        raise ValueError("User {} not found in database!".format(uni))

    r = cursor.fetchone()
    db.close()
    
    return User(r[0], r[1], r[2], r[3], r[4])


@app.route('/profile', methods=['GET'])
def show_profile():
    """ find current user """
    user = users.get_current_user()

    if not user or not check_registered_user(email_to_uni(user.email())):
        return redirect("/")

    uni = email_to_uni(user.email())

    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use cuLunch')
    # grab only the current user's listings
    query = "SELECT l.expiryTime, l.needsSwipes, l.Place, u.uni, u.name, u.schoolYear, u.interests, u.schoolName" \
            " from users u JOIN listings l ON u.uni=l.uni WHERE l.uni = '{}'".format(uni)

    u = find_user(uni)
    print(u.name, u.school)
    
    try:
        cursor.execute(query)
        
    except:
        print("SELECT for show_profile failed!")

    listingposts = []
    for r in cursor.fetchall():
        u = User(r[3], r[4], r[5], r[6], schools[r[7]])
        l = Listing(r[0], uni, r[2], r[1])
        if l.expiryDateTime > (datetime.datetime.now()- timedelta(hours=4)):
            listingposts.append(ListingPost(l, u))
    db.close()

    return render_template('/profile/index.html',
                           current_user=u,
                           listingposts=listingposts if listingposts else False,
                           logout_link=users.create_logout_url("/"),
                           user_email=user.email())

@app.route('/profile', methods=['POST'])
def update_profile():
    """ find current user """
    error = None
    user = users.get_current_user()
    uni = email_to_uni(user.email())

    new_name = request.form['new_name']
    new_school = request.form['new_school']
    new_year = int(request.form['new_year'])
    new_interests = request.form['new_interests']

    if new_name == '' or new_interests == '':
        error = "No field should be empty!"

    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use cuLunch')

    if error is None:

        update_query = "UPDATE users SET name = '%s', schoolYear = %d, interests = '%s', schoolName = '%s'" \
            " WHERE uni='%s'" % (new_name, new_year, new_interests, new_school, uni)
        print(update_query)

        try:
            cursor.execute(update_query)
            # commit the changes in the DB
            db.commit()
        except:
            # rollback when an error occurs
            db.rollback()
            print("UPDATE failed!")

    # grab only the current user's listings
    get_query = "SELECT l.expiryTime, l.needsSwipes, l.Place, u.uni, u.name, u.schoolYear, u.interests, u.schoolName" \
            " from users u JOIN listings l ON u.uni=l.uni WHERE l.uni = '{}'".format(uni)

    u = find_user(uni)
    print(u.name, u.school)

    try:
        cursor.execute(get_query)
        
    except:
        print("SELECT for update_profile failed!")

    listingposts = []
    for r in cursor.fetchall():
        u = User(r[3], r[4], r[5], r[6], schools[r[7]])
        l = Listing(r[0], uni, r[2], r[1])
        listingposts.append(ListingPost(l, u))
        print(l.place)

    db.close()

    return render_template('/profile/index.html',
                           current_user=u,
                           listingposts=listingposts if listingposts else False,
                           logout_link=users.create_logout_url("/"),
                           user_email = user.email(),
                           error = error)


""" this has to be post so flask will accept a request body """
@app.route("/profile/delete", methods=['POST'])
def delete_posting():
    """ get the current user """
    curr_user = users.get_current_user()
    uni = email_to_uni(curr_user.email())
    if not curr_user or not check_registered_user(uni):
        print("unauthorized DELETE request from {}".format(uni))
        return redirect("/", code=401)


    post_info = request.get_json()
    uni = post_info["uni"]
    """ this datetime exactly matches the SQL datetime format, no parsing needed """
    datetime = post_info["datetime"]
    print("delete request from uni {} for datetime {}".format(uni, datetime))

    """ then make sure it exists in the database and remove it with commit/rollback if it fails """
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute("use cuLunch")

    query = "DELETE FROM listings WHERE uni='{}' AND expiryTime='{}'".format(uni, datetime)
    print(query)

    try:
        cursor.execute(query)
        db.commit()
        db.close()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except:
        # rollback when an error occurs
        db.rollback()
        db.close()
        return json.dumps({'success': False}), 404, {'ContentType': 'application/json'}

def find_user(uni):
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute("use cuLunch")

    query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName from users u WHERE u.uni = '{}'".format(uni)
    u = None

    try:
        cursor.execute(query)
        
    except:
        print("SELECT for find_user failed!")

    for r in cursor.fetchall():
        u = User(r[0], r[1], r[2], r[3], schools[r[4]])

    db.close()
    return u


def get_popular_place():
    query = "SELECT place, COUNT(place) AS place_occurrence FROM listings GROUP BY place ORDER BY place_occurrence DESC LIMIT 1"
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute("use cuLunch")

    try:
        cursor.execute(query)

    except:
        print("finding most popular place failed!")
        db.close()
        return

    row = cursor.fetchone()
    db.close()
    return {
        "place":row[0],
        "count":row[1]
    }


if __name__ == '__main__':
    app.run(debug=True)
