from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Console, Game
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
engine = create_engine('sqlite:///consolegames.db',
    connect_args={'check_same_thread':False})
Base.metadata = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        #Reset the user's session
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

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
    return render_template('consoles.html', consoles=consoles)

# Create route for newconsole function
@app.route('/consoles/new', methods=['GET','POST'])
def newconsole():
    if 'username' not in login_session:
        return redirect('login')
    if request.method == 'POST':
        newConsole = Console(name=request.form['name'])
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
        return redirect('login')
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
        return redirect('login')
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
    items = session.query(Game).filter_by(console_id=console_id).all()
    return render_template('game.html', console=console, items=items)

# Create route for newgame function
@app.route('/consoles/<int:console_id>/game/new/', methods=['GET','POST'])
def newgame(console_id):
    console = session.query(Console).filter_by(id=console_id).one()
    if 'username' not in login_session:
        return redirect('login')
    if request.method == 'POST':
        newGame = Game(name=request.form['name'], date=request.form['date'],
            type=request.form['type'], developer=request.form['developer'],
            console_id=console_id)
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
        return redirect('login')
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
        return redirect('login')
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
