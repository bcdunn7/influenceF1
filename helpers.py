"""Helper functions for app.py"""

from flask import g, redirect, flash

from models import Season, Race, Finish, Driver

from colors import line_colors

from itertools import accumulate

def is_logged_in():
    if not g.user:
        flash("Must login first!", "info")
        return redirect(url_for('login'))

def get_data_for_simulator(year):
    """Gathers data from postgres and manipulates it into a race labels array and a dataset array for the chart."""

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
        # find driver color in line_colors_array
        color = line_colors[year][d.code]

        # create data array (race finishing points) for each driver
        points = [0] #first value is before season, at zero points
        for fin in finishes:
            if fin.driver_id == d.id:
                points.append(fin.points)
        # values need to be accumulated for chart
        points_accum = list(accumulate(points))
        driver_obj = {
            'label': d.code,
            'borderColor': color,
            'backgroundColor': color,
            'data': points_accum
        }
        datasets.append(driver_obj)

    return (season_races_abbrs,datasets)


def get_blurbs_for_races(year):
    """Gets race blurb data from postgres and returns an object.
    
        race_blurbs = {'BHR': "text text text", 'MON': "text text text", etc.}
    """

    # get races for this season
    season_races = Race.query.filter(Race.season_year == year).all()

    blurbs = {race.abbreviation: race.blurb for race in season_races if race.blurb != None}

    return blurbs