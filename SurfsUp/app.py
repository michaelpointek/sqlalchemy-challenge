# Import the dependencies.
import numpy as np
import pandas as pd
import markdown

import datetime as dt
from datetime import datetime
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify, g

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Useful vars
#################################################
# Flask Setup
app = Flask(__name__)

# Function to get the session within the application context
def get_session():
    if 'session' not in g:
        g.session = Session(engine)
    return g.session

@app.teardown_appcontext
def teardown_db(exception):
    session = g.pop('session', None)
    if session is not None:
        session.close()

#################################################
# Flask Routes
#################################################
# start at the homepage
# list all the available routes
@app.route('/')
def welcome():
    return markdown.markdown('''
# Climate App
## Module 10 Challenge

---

Active routes:

- [Precipitation Measurements All Stations from the last recorded 12 months](/api/v1.0/precipitation): /api/v1.0/precipitation
- [All Stations](/api/v1.0/stations): /api/v1.0/stations
- [Temperature of the Most Active Station](/api/v1.0/tobs): /api/v1.0/tobs
- [Up Til Now](/api/v1.0/2016-08-23): /api/v1.0/**[[YYYY-MM-DD]]**
- [Between Two Dates](/api/v1.0/2016-08-23/2017-08-23): /api/v1.0/**[[YYY-MM-DD]]**/**[[YYY-MM-DD]]**
''')

# - Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from 2017-08-23
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query to access the date and precipitation for the past year
    session = get_session()
    prcp_data = session.query(Measurement.date, Measurement.prcp)\
                      .filter(Measurement.date >= one_year_ago)\
                      .order_by(Measurement.date)\
                      .all()

    # Constructing a dictionary with date as key and precipitation as value
    prcp_dict = {date: prcp for date, prcp in prcp_data}

    return jsonify(prcp_dict)

# - Return a JSON list of all stations.
@app.route("/api/v1.0/stations")
def stations():
    session = get_session()
    # Query all stations
    all_stations = session.query(Station.station, Station.name).all()
    session.close()  # Close the session after use

    # Constructing a list of dictionaries with station ID and name
    stations_list = [{"station": station, "name": name} for station, name in all_stations]

    return jsonify(stations_list)
# - Query the dates and temperature observations of the most-active station
#   for the previous year of data.
# - Return a JSON list of temperature observations for the previous year.
@app.route('/api/v1.0/tobs')
def tobs():
    session = get_session()

    # Calculate the date one year from 2017-08-23
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    stations_activity = session.query(Measurement.station, func.count(Measurement.station))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .all()

    most_active_station = stations_activity[0][0]

    top_station_one_year = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.date >= one_year_ago)\
        .filter(Measurement.station == most_active_station)\
        .all()

    result = []

    for measurement in top_station_one_year:
        d = {}
        d[measurement.date] = measurement.tobs
        result.append(d)

    session.close()  # Close the session after use
    return jsonify(result)


# - Return a JSON list of the minimum temperature, the average temperature,
#   and the maximum temperature for a specified start or start-end range.
# - For a specified start, calculate TMIN, TAVG, and TMAX for all the dates
#   greater than or equal to the start date.
@app.route('/api/v1.0/<start>')
def start_date(start):
    session = get_session()
    canon_start = start

    measurements_since = session.query(Measurement.date,
                                       func.min(Measurement.tobs),
                                       func.avg(Measurement.tobs),
                                       func.max(Measurement.tobs))\
                                .filter(Measurement.date >= canon_start)\
                                .group_by(Measurement.date)\
                                .all()

    result = []

    for measurement in measurements_since:
        d = {}
        d["Date"] = measurement[0]
        d["TMIN"] = measurement[1]
        d["TAVG"] = measurement[2]
        d["TMAX"] = measurement[3]
        result.append(d)

    session.close()  # Close the session after use
    return jsonify(result)


# - For a specified start date and end date, calculate TMIN, TAVG, and TMAX
#   for the dates from the start date to the end date, inclusive.
@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
    session = get_session()
    canon_start = start
    canon_end = end

    measurements_between = session.query(Measurement.date,
                                         func.min(Measurement.tobs),
                                         func.avg(Measurement.tobs),
                                         func.max(Measurement.tobs))\
                                  .filter(Measurement.date >= canon_start)\
                                  .filter(Measurement.date <= canon_end)\
                                  .group_by(Measurement.date)\
                                  .all()

    result = []

    for measurement in measurements_between:
        d = {}
        d["Date"] = measurement[0]
        d["TMIN"] = measurement[1]
        d["TAVG"] = measurement[2]
        d["TMAX"] = measurement[3]
        result.append(d)

    session.close()  # Close the session after use
    return jsonify(result)

# Debug
if __name__ == "__main__":
    app.run(debug=True)
