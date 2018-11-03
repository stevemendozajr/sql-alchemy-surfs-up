import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)

#Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create our session(link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        f"<a href='/api/v1.0/start'>/api/v1.0/start</a><br/>"
        f"<a href='/api/v1.0/start/end'>/api/v1.0/start/end</a><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1)

    #convert query result into a datetime object and set it as a variable
    for date in last_date:
        most_recent_date = date.date

    most_recent_date_2 = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")


    # Calculate the date 1 year ago from today
    one_year_ago = most_recent_date_2 - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()


    all_prcp = []
    for prcp in results:
        prcp_dict = {}
        prcp_dict[prcp[0]] = prcp[1]
        all_prcp.append(prcp_dict)
    
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():

    results = session.query(Station).all()


    all_stations = []
    for station in results:
        station_dict = {}
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1)

    #convert query result into a datetime object and set it as a variable
    for date in last_date:
        most_recent_date = date.date

    most_recent_date_2 = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")

    # Calculate the date 1 year ago from today
    one_year_ago = most_recent_date_2 - dt.timedelta(days=365)

    most_active_stations = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    most_active_station = most_active_stations[0][0]

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).filter(Measurement.station == most_active_station).order_by(Measurement.date).all()

    all_tobs = []
    for tobs in results:
        tobs_dict = {}
        tobs_dict[tobs[0]] = tobs[1]
        all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)


@app.route("/api/v1.0/start")
def start():

    start_date = dt.datetime(2016, 10, 15)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()


    return jsonify(results)


@app.route("/api/v1.0/start/end")
def startend():

    start_date = dt.datetime(2016, 10, 15)
    end_date = dt.datetime(2016, 10, 22)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
