import numpy as np
import datetime as dt

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

# Save reference to the table
measur = Base.classes.measurement
stn = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Precipitation Flask Route
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the database for dates and precipitation
    query_results = session.query(measur.date, measur.prcp).\
        order_by(measur.date).all()

    prcp_date = []

    for date, prcp in query_results:
        dict_prcp_date = {}
        dict_prcp_date[date] = prcp
        prcp_date.append(dict_prcp_date)
    
    session.close()

    #Return a json dictionary of date and precipitation
    
    return jsonify(prcp_date)



# Station Flask Route
@app.route("/api/v1.0/stations")
def stations():
   
   # Create our session (link) from Python to the DB
    session = Session(engine)
    
   # Create dictionary for station id and station name
    Stations_dict = {}

    # Query the database for station id and name
    station_id_name = session.query(stn.station, stn.name).all()

    for stn_id, stn_name in station_id_name:
        Stations_dict[stn_id] = stn_name

    session.close()

    

    # Return json list of stations
    return jsonify(Stations_dict)

#TOBS Flask Route
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query for most active weather station
    Active_Stations = session.query(measur.station, func.count(measur.date)).\
    group_by(measur.station).order_by(func.count(measur.date).desc()).first()[0]

    # Query the latest date recorded for most active station
    most_recent_date = session.query(measur.date).order_by(measur.date.desc()).first()[0]

    # Calculate date from one year ago from latest data of most active station
    one_year_ago = (dt.datetime.strptime(most_recent_date, '%Y-%m-%d'))\
        - dt.timedelta(days = 365)

    # Query date and temperature for one year of most active station
    tobs_data = session.query(measur.station, measur.date, measur.tobs).\
    filter(measur.station == Active_Stations, measur.date >= one_year_ago, measur.date <= most_recent_date).\
    order_by(measur.date.desc()).all()
 
    session.close()

    # Putting tuples together into a list
    station_history = list(np.ravel(tobs_data))

    return jsonify(station_history)

    
#Start Flask Route
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    # Start empty list for data
    start_list = []

    # Query start dates and calculate, min, max, and avg.
    start_result = session.query(measur.date, func.min(measur.tobs), func.max(measur.tobs), func.avg(measur.tobs)).\
    filter(measur.date >= start).group_by(measur.date).all()

    for date, min, max, avg in start_result:
        start_dict = {}
        start_dict["Date"] = date
        start_dict["TMIN"] = min
        start_dict["TMAX"] = max
        start_dict["TAVG"] = avg
        start_list.append(start_dict)
    
    session.close()

    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)

    # Start empty list for data
    se_list =[]

    # Query with start and end dates and then calculate min, max, and avg.
    StartEnd_results = session.query(func.min(measur.tobs), func.max(measur.tobs), func.avg(measur.tobs)).\
    filter(measur.date >= start, measur.date <= end).all()

    for se_min, se_max, se_avg in StartEnd_results:
        se_dict = {}
        se_dict["Start Date"] = start
        se_dict["End Date"] = end
        se_dict["TMIN"] = se_min
        se_dict["TMAX"] = se_max
        se_dict["TAVG"] = se_avg
        se_list.append(se_dict)

    session.close()    
    
    return jsonify(se_list)

if __name__ == '__main__':
    app.run(debug=True)