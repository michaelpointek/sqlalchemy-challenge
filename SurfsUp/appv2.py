# Import the dependencies.
import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


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

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Main page of the API that shows the different routes available
@app.route("/")
def welcome():
    return(
        f"<h1>Welcome to the Climate Analysis API!</h1>"
        f"<h2>Available Routes:</h2>"
        f"<ul>"
        f"<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>"
        f"<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>"
        f"<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>"
        f"<li>/api/v1.0/&lt;start&gt;</li>"
        f"<li>/api/v1.0/&lt;start&gt;/&lt;end&gt;</li>"
        f"</ul>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from 2017-08-23
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Query to access the date and precipitation for the past year
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()

    # List comprehension to create a key and value pair 
    prcp_dict = [{"date": date, "percipitation": prcp} for date, prcp in prcp_data]
    
    # Output as JSON 
    return jsonify(list(np.ravel(prcp_dict)))

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query for all stations
    results= session.query(Station.station).all()
    # Output as JSON
    return jsonify(list(np.ravel(results)))

# Tobs route 
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculating the date one year from 2017-08-23
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Query for date and tobs value based on the most active station 
    active_station = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= one_year_ago).all()

    # List comprehension to create a key and value pair 
    most_active_station = [{"date": date, "temp": temp} for date, temp in active_station]
    
    # Output as JSON
    return jsonify(list(np.ravel(most_active_station)))


# Dynamic route for a given start date
@app.route("/api/v1.0/<start>")
def start_date_temps(start=None):
    # Place query elements in variable 'sel'
    sel = [Measurement.date, func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Query the elements and filter according to start_date input by user
    results = session.query(*sel).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    # List comprehension to create key-value pairs
    temps = [{"date": date, "min_temp": min_temp, "avg_temp": avg_temp, "max_temp": max_temp}\
            for date, min_temp, avg_temp, max_temp in results]
    
    # Output as JSON
    return jsonify(list(np.ravel(temps)))

# Dynamic route for a given start and end date
@app.route("/api/v1.0/<start>/<end>")
def date_range_temps(start=None, end=None):
    # Place query elements in variable 'sel'
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Query the elements and filter according to start and end date input by user
    results = session.query(*sel).filter(Measurement.date >= start).\
            filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    # List comprehension to create key-value pairs
    temps = [{"date": date, "min_temp": min_temp, "avg_temp": avg_temp, "max_temp": max_temp}\
             for date, min_temp, avg_temp, max_temp in results]
    
    # Output as JSON
    return jsonify(list(np.ravel(temps)))

if __name__ == '__main__':
    app.run(debug=True)