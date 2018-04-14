from __future__ import print_function
from google.appengine.ext import vendor
import datetime
import os
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


@app.route('/')
def index():
    return "Hello, World (lets see how long a change takes III)!"


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


@app.route('/index.html', methods=['POST', 'GET'])
def create_user():
    error = None

    if request.method == 'POST':
        f_name = request.form['first_name_field']
        l_name = request.form['last_name_field']
        uni = request.form['uni_field']
        password = request.form['password_field']
        school = request.form['school_field']
        year = request.form['year_field']
        interests = request.form['interests_field']


        # connect to db
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('use cuLunch')

        # check if uni is already registered 
        uniqueuni_query = "SELECT uni from users" 
        cursor.execute(uniqueuni_query)
        registered_uni = set([row[0] for row in cursor.fetchall()])
        unique = uni not in registered_uni


        form_input = Form(f_name, l_name, uni, password, school, year, interests)
        user_check, error = form_input.form_input_valid()

        print (form_input.uni + " " + form_input.f_name + " " + form_input.l_name + " " + form_input.school +
               " " + form_input.interests + " " + form_input.school + " " + form_input.pwd)

        if user_check and unique:

            name = form_input.f_name + ' ' + form_input.l_name
            user = User(uni, name, year, interests, school, password)
            # else send error to user

            # store in database

            insert_query = "INSERT INTO users VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (user.uni, user.password, user.name,
                                                                                       user.schoolYear, user.interests, user.school)
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
            return render_template('/listform/index.html')

        elif not user_check and error == 'empty':
            error = 'Empty answer in one field'
            print("empty")
            db.close()
            return render_template('index.html', error=error)

        elif not user_check and error == 'empty':
            error = 'Password is not valid: length of password is at least 8, and it should contain at all three of the \
                    following: digits, uppercase letters, and lowercase letters.'
            db.close()
            return render_template('index.html', error=error)

        elif not unique:
            error = 'This UNI has been registered already.'
            print("not unique")
            db.close()
            return render_template('index.html', error=error)

        else:
            # return redirect(url_for('static', filename='index.html', error=error))
            db.close()

    return render_template('index.html')


@app.route('/listform/index.html', methods=['POST', 'GET'])
def create_listing():

    if request.method == 'POST':
        cafeteria = request.form['Cafeteria']
        timestamp = request.form['timestamp']
        needSwipe = request.form.get('needswipe') != None
        # print(cafeteria, timestamp, needSwipe)
        

        # store in database
        db = connect_to_cloudsql()
        cursor = db.cursor()
        cursor.execute('use cuLunch')

        query = "INSERT INTO listings VALUES ('%s', '%s', '%d', '%s')" % (timestamp, 'cl3403', needSwipe, cafeteria)
        # print('query generated')
        # print(query)

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

    return render_template('/listings/index.html')


@app.route('/listings')
def output():
    # serve index template

    #  Need to: get listings and associated users from db
    #  sort listings by date and time

    u1 = User('cck2127', 'Carson Kraft', 2018, 'skiing', 'Barnard', 'doin Stuff')
    u2 = User('jds2246', 'Jonathan Shapiro', 2018, 'singing', 'Columbia College', 'Being cool')
    u3 = User('test', 'John Doe', '3000', 'interests', 'General Studies', 'Test')

    l1 = Listing(datetime.date(2018, 7, 18), datetime.time(7, 30, 0), 'cck2127', 'Diana Center')
    l2 = Listing(datetime.date(2018, 6, 20), datetime.time(13, 30, 0), 'jds2246', 'Diana Center')
    l3 = Listing(datetime.date(2018, 5, 11), datetime.time(18, 30, 0), 'test', 'Diana Center')

    lp1 = ListingPost(l1, u1)
    lp2 = ListingPost(l2, u2)
    lp3 = ListingPost(l3, u3)

    listingposts = [lp1, lp2, lp3]

    return render_template('/listings/index.html', listingposts=listingposts)


if __name__ == '__main__':
    app.run(debug=True)
