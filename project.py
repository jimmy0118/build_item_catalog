from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Console, Game

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///consolegames.db',
    connect_args={'check_same_thread':False})
Base.metadata = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# JSON APIs to view Restaurant Information
@app.route('/console/JSON')
def showconsoleJSON():
    consoles = session.query(Console).all()
    return jsonify(consoles=[c.serialize for c in consoles])

@app.route('/console/<int:console_id>/game/JSON')
def showgameJSON(console_id):
    console = session.query(Console).filter_by(id=console_id).one()
    items = session.query(Game).filter_by(console_id=console_id).all()
    return jsonify(games=[i.serialize for i in items])

@app.route('/console/<int:console_id>/game/<int:game_id>/JSON')
def gameinfoJSON(console_id, game_id):
    game = session.query(Game).filter_by(id=game_id).one()
    return jsonify(gameinfo=[game.serialize])

# Show all consoles
@app.route('/')
@app.route('/console/')
def showconsole():
    consoles = session.query(Console).order_by(asc(Console.name))
    return render_template('consoles.html', consoles=consoles)

# Show games of one console
@app.route('/console/<int:console_id>/')
@app.route('/console/<int:console_id>/game/')
def showgame(console_id):
    console = session.query(Console).filter_by(id=console_id).one()
    items = session.query(Game).filter_by(console_id=console_id).all()
    return render_template('game.html', console=console, items=items)

# Create route for newgame function
@app.route('/console/<int:console_id>/game/new/', methods=['GET','POST'])
def newgame(console_id):
    console = session.query(Console).filter_by(id=console_id).one()
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
@app.route('/console/<int:console_id>/game/<int:game_id>/edit/',
    methods=['GET', 'POST'])
def editgame(console_id, game_id):
    console = session.query(Console).filter_by(id=console_id).one()
    editedgame = session.query(Game).filter_by(id=game_id).one()
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
@app.route('/console/<int:console_id>/game/<int:game_id>/delete/',
    methods=['GET', 'POST'])
def deletegame(console_id, game_id):
    console = session.query(Console).filter_by(id=console_id).one()
    gametodelete = session.query(Game).filter_by(id=game_id).one()
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
