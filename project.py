#!/usr/bin/python
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Console, Game, User
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Connect to Database and create database session
engine = create_engine('sqlite:///consolegameswithusers.db',
    connect_args={'check_same_thread':False})
Base.metadata = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Create gconnect function
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['provider'] = 'google'
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if it does not make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Create gdisconnect function
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:
    	response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# Create fbconnect function
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    #Exchange client token for long-lived server-side token with GET / oauth/
    #access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret=
    #{app-secret}&fb_exchange_token={short-lived-token}
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)  # nopep8
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we
        have to split the token first on commas and select the first index which
        gives us the key : value for the server access token then we split it on
        colons to pull out the actual token value and replace the remaining
        quotes with nothing so that it can be used directly in the graph api
        calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token  # nopep8
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # nopep8
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:\
     150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Create fbdisconnect function
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)  # nopep8
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("you have been successfully logged out!")
        return redirect(url_for('showconsole'))
    else:
        flash("You were not logged in to begin with!")
        return redirect(url_for('showconsole'))

# JSON APIs to view Restaurant Information
@app.route('/consoles/JSON')
def showconsoleJSON():
    consoles = session.query(Console).all()
    return jsonify(consoles=[c.serialize for c in consoles])

@app.route('/consoles/<int:console_id>/game/JSON')
def showgameJSON(console_id):
    console = session.query(Console).filter_by(id=console_id).one()
    items = session.query(Game).filter_by(console_id=console_id).all()
    return jsonify(games=[i.serialize for i in items])

@app.route('/consoles/<int:console_id>/game/<int:game_id>/JSON')
def gameinfoJSON(console_id, game_id):
    game = session.query(Game).filter_by(id=game_id).one()
    return jsonify(gameinfo=[game.serialize])

# Show all consoles
@app.route('/')
@app.route('/consoles/')
def showconsole():
    consoles = session.query(Console).order_by(asc(Console.name))
    if 'username' not in login_session:
        return render_template('publicconsoles.html', consoles=consoles)
    else:
        return render_template('consoles.html', consoles=consoles)

# Create route for newconsole function
@app.route('/consoles/new', methods=['GET','POST'])
def newconsole():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newConsole = Console(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(newConsole)
        session.commit()
        flash("New Console Created!")
        return redirect(url_for('showconsole'))
    else:
        return render_template('newconsole.html')

# Create route for editconsole function
@app.route('/consoles/<int:console_id>/edit/', methods=['GET','POST'])
def editconsole(console_id):
    editedconsole = session.query(Console).filter_by(id=console_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            editedconsole.name = request.form['name']
        session.add(editedconsole)
        session.commit()
        flash("Console has been edited")
        return redirect(url_for('showconsole'))
    else:
        return render_template('editconsole.html', console=editedconsole)

# Create route for deleteconsole function
@app.route('/consoles/<int:console_id>/delete/', methods=['GET','POST'])
def deleteconsole(console_id):
    consoletodelete = session.query(Console).filter_by(id=console_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if consoletodelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to\
        delete this console. Please create your own console in order to delete.\
        ');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(consoletodelete)
        session.commit()
        flash("Console %s has been deleted" % consoletodelete.name)
        return redirect(url_for('showconsole'))
    else:
        return render_template('deleteconsole.html', console=consoletodelete)

# Show games of one console
@app.route('/consoles/<int:console_id>/')
@app.route('/consoles/<int:console_id>/game/')
def showgame(console_id):
    console = session.query(Console).filter_by(id=console_id).one()
    creator = getUserInfo(console.user_id)
    items = session.query(Game).filter_by(console_id=console_id).all()
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('publicgame.html',
                                console=console,
                                items=items,
                                creator=creator)
    else:
        return render_template('game.html',
                                console=console,
                                items=items,
                                creator=creator)

# Create route for newgame function
@app.route('/consoles/<int:console_id>/game/new/', methods=['GET','POST'])
def newgame(console_id):
    console = session.query(Console).filter_by(id=console_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGame = Game(name=request.form['name'], date=request.form['date'],
            type=request.form['type'], developer=request.form['developer'],
            console_id=console_id, user_id=console.user_id)
        session.add(newGame)
        session.commit()
        flash("new game info created!")
        return redirect(url_for('showgame', console_id=console_id))
    else:
        return render_template('newgame.html', console_id=console_id)

# Create route for editgame function
@app.route('/consoles/<int:console_id>/game/<int:game_id>/edit/',
    methods=['GET', 'POST'])
def editgame(console_id, game_id):
    console = session.query(Console).filter_by(id=console_id).one()
    editedgame = session.query(Game).filter_by(id=game_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            editedgame.name = request.form['name']
        if request.form['date']:
            editedgame.date = request.form['date']
        if request.form['type']:
            editedgame.type = request.form['type']
        if request.form['developer']:
            editedgame.developer = request.form['developer']
        session.add(editedgame)
        session.commit()
        flash("game info has been edited!")
        return redirect(url_for('showgame', console_id=console_id))
    else:
        return render_template('editgame.html', console_id=console_id,
            game_id=game_id, game=editedgame)

# Create route for deletegame function
@app.route('/consoles/<int:console_id>/game/<int:game_id>/delete/',
    methods=['GET', 'POST'])
def deletegame(console_id, game_id):
    console = session.query(Console).filter_by(id=console_id).one()
    gametodelete = session.query(Game).filter_by(id=game_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if gametodelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to\
        delete this game. Please create your own game in order to delete.');}\
        </script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(gametodelete)
        session.commit()
        flash("game info has been deleted!")
        return redirect(url_for('showgame', console_id=console_id))
    else:
        return render_template('deletegame.html', game=gametodelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
