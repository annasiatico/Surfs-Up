from flask import Flask, jsonify

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#################################################
# Database Setup
#################################################
engine = create_engine(
    "sqlite:///Resources/hawaii.sqlite",
    connect_args={"check_same_thread": False},
    echo=True,
)

Base = automap_base()

Base.prepare(engine, reflect=True)

# Assign tables to variables
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return """<html>
    <h1>Honolulu, HI API</h1>
    <ul>
    <br>
    <li>
    Last 12 months of precipitation data:
    <br>
    <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
    </li>
    <br>
    <li>
    List of stations from the dataset: 
    <br>
   <a href="/api/v1.0/stations">/api/v1.0/stations</a>
   </li>
    <br>
    <li>
    Twelve months of temperature data for station with the 
    <br>highest number of temperature observations (USC00519281):
    <br>
    <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
    </li>
    <br>
    </ul>
    </html>
    """

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Design a query to retrieve the last 12 months of precipitation data
    twelve_mos_prcp = (
        session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    )

    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.datetime.strptime(twelve_mos_prcp[0], "%Y-%m-%d") - dt.timedelta(
        days=366
    )

    # Perform a query to retrieve the data and precipitation scores
    data_prcp_qry = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )

    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value
    prcp_dict = dict(data_prcp_qry)

    # Return the JSON representation of your dictionary
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():

    # Return a JSON list of stations from the dataset
    stations_available = session.query(Measurement.station).distinct().all()

    return jsonify(stations_available)


@app.route("/api/v1.0/tobs")
def tobs():

    # List of stations and their observation counts
    stations_active = (
        session.query(Measurement.station, func.count(Measurement.station))
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .all()
    )

    # Choose the station with the highest number of temperature observations.
    highest_tempobs_station = stations_active[0][0]

    # Query the last 12 months of temperature observation data for this station
    twelve_mos_prcp = (
        session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    )

    one_year_ago = dt.datetime.strptime(twelve_mos_prcp[0], "%Y-%m-%d") - dt.timedelta(
        days=366
    )

    temp_obs = (
        session.query(Measurement.tobs)
        .filter(Measurement.date >= one_year_ago)
        .filter(Measurement.station == highest_tempobs_station)
        .all()
    )

    # Return a JSON list 
    return jsonify(temp_obs)


if __name__ == "__main__":
    app.run(debug=True)
