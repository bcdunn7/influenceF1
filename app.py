from flask import Flask, render_template, session, g
from flask_debugtoolbar import DebugToolbarExtension

from itertools import accumulate

from models import db, connect_db, User, Season, Finish, Race

# from helpers import is_logged_in

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///influenceF1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = "secret"

debug = DebugToolbarExtension(app)

CURR_USER_KEY = "current_user"


# ***********************************************
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If logged in, add user to Flask global obj."""

    if CURR_USER_KEY in session: 
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def session_login(user):
    """'Log in' user: store user id in session."""

    session[CURR_USER_KEY] = user.id


def session_logout():
    """'Log out' user: delete user id from session."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


# ***********************************************
# Base ROUTING

@app.route('/')
def homepage():
    """Homepage with info and demo of app."""

    return render_template('home.html')


@app.route('/how-it-works')
def tutorial():
    """Tutorial page explaining the app and how the simulator works."""

    return render_template('tutorial.html')


# ***********************************************
# Simulator

@app.route('/simulator/<int:year>')
def simulator(year):
    """Main functionality page of application: show simulator."""

    # is_logged_in()

    # get season (to access season.drivers)
    season = Season.query.get(year)

    # get races for that season
    season_races = Race.query.filter(Race.season_year == year).all()

    # get abbreviations for those races and make them into a race_labels array
    season_races_abbrs = [race.abbreviation for race in season_races]
     # first data point will be 'before the season'
    season_races_abbrs.insert(0,'')

    # get id for season races in order to get finishes for season
    season_races_ids = [race.id for race in season_races]

    # get finishes for the season races
    finishes = Finish.query.filter(Finish.race_id.in_(season_races_ids)).all()

    # create datasets obj to pass to template and chart
    datasets = []
    for d in season.drivers:
        # create data array (race finishing points) for each driver
        points = [0] #first value is before season, at zero points
        for fin in finishes:
            if fin.driver_id == d.id:
                points.append(fin.points)
        # values need to be accumulated for chart
        points_accum = list(accumulate(points))
        driver_obj = {
            'label': d.code,
            'data': points_accum
        }
        datasets.append(driver_obj)

    return render_template('simulator.html', race_labels=season_races_abbrs, datasets=datasets)