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

    if request.method == 'POST':
        f_name = request.form['first_name_field']
        l_name = request.form['last_name_field']
        uni = request.form['uni_field']
        school = request.form['school_field']
        year = request.form['year_field']
        interests = request.form['interests_field']

        # connect to db
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('use cuLunch')

        # check if uni is already registered
        unique = check_registered_user(uni)

        form_input = Form(f_name, l_name, uni, school, year, interests)
        user_check, error = form_input.form_input_valid()

        print (form_input.uni + " " + form_input.f_name + " " + form_input.l_name + " " + form_input.school +
               " " + form_input.interests + " " + form_input.school)

        '''if not user_check:
            error = error
            db.close()'''


        if user_check and unique:

            name = form_input.f_name + ' ' + form_input.l_name
            user = User(uni, name, year, interests, school)
            # else send error to user

            # store in database
            insert_query = "INSERT INTO users VALUES ('%s', '%s', '%s', '%s', '%s')" % (user.uni, user.name,
                                                                                       user.year, user.interests, user.school)
            # print('query generated')
            # print(query)

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

        elif not user_check and error == 'bad pass':
            error = 'Password is not valid: length of password is at least 8, and it should contain at all three of the \
                    following: digits, uppercase letters, and lowercase letters.'
            db.close()

        elif not unique:
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
    cafeteria = request.form['Cafeteria']
    timestamp = request.form['timestamp']
    needSwipe = request.form.get('needswipe') != None
    # print(cafeteria, timestamp, needSwipe)

    query = None
    if request.method == 'POST':
        cafeteria = request.form['Cafeteria']
        date = request.form['date']
        time = request.form['time']
        needSwipe = request.form.get('needswipe') != None
        # print(cafeteria, timestamp, needSwipe)
        timestamp = date + "T" + time

        query = "INSERT INTO listings VALUES ('%s', '%s', '%d', '%s')" % (timestamp, 'cl3403', needSwipe, cafeteria)
        # print('query generated')
        # print(query)

    # store in database
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute('use cuLunch')

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

@app.route("/listform", methods=["GET"])
def show_listings():
    return render_template('/listings/index.html')


@app.route('/listings', methods=["GET"])
def output():
    user = users.get_current_user()

    # can't see listings if you don't have an account :^)
    if not user or not check_registered_user(email_to_uni(user.email())):
        return redirect("/")

    # then fetch the listings
    uni = email_to_uni(user.email())

    cursor = get_cursor()
    # grab the relevant information and make sure the user doesn't see their own listings there
    query = "SELECT u.uni, u.name, u.schoolYear, u.interests, u.schoolName, l.expiryTime, l.needsSwipes, l.Place from " \
            "users u JOIN listings l ON u.uni=l.uni WHERE NOT u.uni = '{}'".format(uni)

    # serve index template

    #  Need to: get listings and associated users from db
    #  sort listings by date and time

    u1 = User('cck2127', 'Carson Kraft', 2019, 'skiing', 'Barnard')
    u2 = User('jds2246', 'Jonathan Shapiro', 2018, 'singing', 'Columbia College')
    u3 = User('test', 'John Doe', 2000, 'interests', 'General Studies')

    l1 = Listing(datetime.date(2018, 7, 18), datetime.time(7, 30, 0), 'cck2127', 'Diana Center')
    l2 = Listing(datetime.date(2018, 6, 20), datetime.time(13, 30, 0), 'jds2246', 'Diana Center')
    l3 = Listing(datetime.date(2018, 5, 11), datetime.time(18, 30, 0), 'test', 'Diana Center')

    lp1 = ListingPost(l1, u1)
    lp2 = ListingPost(l2, u2)
    lp3 = ListingPost(l3, u3)

    listingposts = [lp1, lp2, lp3]

    return render_template('/listings/index.html', listingposts=listingposts, name=user.nickname(), logout_link=users.create_logout_url("/"))

  
def valid_uni(email):
    if re.match("\S+@(columbia|barnard)\.edu", email) is not None:
        return True
    else:
        return False


# given an email, checks if it corresponds to a registered user in the database
def check_registered_user(uni):
    cursor = get_cursor()

    query = "SELECT * FROM users WHERE users.uni = '{}'".format(uni)
    cursor.execute(query)

    if not cursor.rowcount:
        return False
    else:
        return True


def email_to_uni(email):
    return email.split('@')[0]


def get_cursor():
    db = connect_to_cloudsql()
    cursor = db.cursor()
    cursor.execute("use cuLunch")
    return cursor


if __name__ == '__main__':
    app.run(debug=True)
