from __future__ import print_function
from google.appengine.ext import vendor
import datetime
import os
import re
import sys
from user import *
from listing import *

vendor.add(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'))
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
from flask import Flask, make_response, request, url_for, redirect, render_template
import MySQLdb


# These environment variables are configured in app.yaml.
CLOUDSQL_CONNECTION_NAME = os.environ['CLOUDSQL_CONNECTION_NAME']
CLOUDSQL_USER = os.environ.get('CLOUDSQL_USER')
CLOUDSQL_PASSWORD = os.environ.get('CLOUDSQL_PASSWORD')

app = Flask(__name__, template_folder=tmpl_dir)

from google.appengine.api import users

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
    year = request.form['year_field']
    interests = request.form['interests_field']
    user = users.get_current_user()
    uni = email_to_uni(user.email())

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
        user = User(uni, name, year, interests, school)
        # else send error to user

        # store in database
        insert_query = "INSERT INTO users VALUES ('%s', '%s', '%s', '%s', '%s')" % (uni, name, year, interests, school)
        # print('query generated')
        print(insert_query)

        try:
            cursor.execute(insert_query)
            # commit the changes in the DB
            db.commit()
        except:
            # rollback when an error occurs
            db.rollback()

        # disconnect from db after use
        db.close()
        return redirect(url_for('create_listing'))

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
    user = users.get_current_user()
    if user:
        logout_url = users.create_logout_url('/')

        # then check if it's a valid uni and they have an account
        if valid_uni(user.email()):
            # if they have an account
            if check_registered_user(email_to_uni(user.email())):
                # redirect them to the listings page for their user
                return redirect("/listings")
            else:
                # render the account creation page
                return render_template("index.html",
                                       account_creation=True,
                                       user_logged_in=True,
                                       logout_url=logout_url,
                                       uni=email_to_uni(user.email()))

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
    listing_check, lerror = listform_input.listform_dateime_valid()

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

        # disconnect from db after use
        db.close()
        return redirect(url_for('output'))

    elif not listing_check and lerror == 'empty':
        error = 'Empty answer in one field'
        db.close()

    elif not listing_check and lerror == 'bad time':
        error = cafeteria + " is not open at the time selected"
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

    cursor = get_cursor()
    # grab the relevant information and make sure the user doesn't see their own listings there
    query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName, l.expiryTime, l.needsSwipes, l.Place from " \
            "users u JOIN listings l ON u.uni=l.uni WHERE NOT u.uni = '{}'".format(uni)

    cursor.execute(query)
    posts = []
    for r in cursor.fetchall():
        #TODO: make schoolYear an int
        u = User(r[0], r[1], int(r[2]), r[3], r[4])
        # we need to convert datetime into a separate date and time for the listing object
        l = Listing(r[5], r[0], r[7], r[6])
        posts.append(ListingPost(l, u))

    # serve index template
    return render_template('/listings/index.html', listingposts=posts, name=user.nickname(), logout_link=users.create_logout_url("/"))

  
def valid_uni(email):
    if re.match("\S+@(columbia|barnard)\.edu", email) is not None:
        return True
    else:
        return False


 
def check_registered_user(uni):
    """ 
    Given an email, checks if it corresponds to a registered user in the database 
    If user is registered, this function returns True; otherwise, it returns False

    """

    cursor = get_cursor()

    query = "SELECT * FROM users WHERE users.uni = '{}'".format(uni)
    print(query)
    cursor.execute(query)


    if not cursor.rowcount:
        return False
    else:
        return True


def email_to_uni(email):
    return email.split('@')[0]


# not great practice but the connection is closed once it leaves scope
def get_cursor():
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute("use cuLunch")
    return cursor


def dt_to_date(dt_string):
    """
    gets an SQL DATETIME string and returns a datetime.date
    1997-07-18 14:00:00 -> [1997, 7, 18]
    delightfully devilish, seymour
    """
    l = [int(x) for x in str(dt_string).split(" ")[0].split("-")]
    return datetime.date(l[0], l[1], l[2])


def dt_to_time(dt_string):
    """
    gets an SQL DATETIME string and returns a datetime.time
    1997-07-18 14:00:00 -> [14, 0, 0]
    """
    l = [int(x) for x in str(dt_string).split(" ")[1].split(":")]
    return datetime.time(l[0], l[1], l[2])

def get_user_info():
    """
    gets the user info from the database from a uni
    returns a new User object

    """
    user = users.get_current_user()
    uni = email_to_uni(user.email())

    cursor = get_cursor()
    query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName FROM users u WHERE u.uni='{}'".format(uni)
    cursor.execute(query)

    if not cursor.rowcount:
        raise ValueError("User {} not found in database!".format(uni))

    r = cursor.fetchone()
    #TODO: make the schoolyear an int (again)
    return User(r[0], r[1], int(r[2]), r[3], r[4])



@app.route('/profile')
def show_profile():
    """ find current user """

    user = users.get_current_user()

    if not user or not check_registered_user(email_to_uni(user.email())):
        return redirect("/")

    uni = email_to_uni(user.email())

    print(uni)

    cursor = get_cursor()
    # grab only the current user's listings
    query = "SELECT l.expiryTime, l.needsSwipes, l.Place, u.uni, u.name, u.schoolYear, u.interests, u.schoolName" \
            " from users u JOIN listings l ON u.uni=l.uni WHERE l.uni = '{}'".format(uni)

    u = None
    cursor.execute(query)
    listingposts = []
    for r in cursor.fetchall():
        # TODO: make schoolYear an int
        u = User(r[3], r[4], int(r[5]), r[6], r[7])
        # we need to convert datetime into a separate date and time for the listing object
        l = Listing(dt_to_date(r[0]), uni, r[2], r[1])
        listingposts.append(ListingPost(l, u))
        print(l.place)


    if not listingposts:
        return render_template('/profile/index.html', current_user=u, listingposts=False, logout_link=users.create_logout_url("/"))

    else:
        return render_template('/profile/index.html', current_user=u, listingposts=listingposts, logout_link=users.create_logout_url("/"))

    # print("Your Listings: " + yourListings)



if __name__ == '__main__':
    app.run(debug=True)
