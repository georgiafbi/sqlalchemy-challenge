import numpy as np
# Statistical analysis
from scipy import stats
from numpy import mean
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import matplotlib.pyplot as plt
from flask import Flask, jsonify
from matplotlib import style
style.use('fivethirtyeight')
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect the tables
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect = True)

# View all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    
    prcp_results=[]

    recent_date = session.query(Measurement.date, Measurement.prcp, Measurement.station).\
        order_by(Measurement.date.asc()).all()

    session.close()

    for d, p, s in recent_date:
        prcp_dict = {"Date":d,"Station ID":s,"Precipitation":p}
        prcp_results.append(prcp_dict)
    return (jsonify(prcp_results))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_results=[]
    stations = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()
    for station, name, lat, lng, el in stations:
        station_dict = {"Station ID": station, "Station Name": name,"Latitude":lat,"Longitude":lng,"Elevation":el}
        station_results.append(station_dict)

    return(jsonify(station_results))

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    recent_date = session.query(Measurement.date).order_by(Measurement.date.asc()).all()[-1][0]

    most_active_12 = session.query(Measurement.station).\
        filter(Measurement.date>(dt.datetime.strptime(recent_date,"%Y-%m-%d")-dt.timedelta(days=365))).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    most_active_tobs = session.query(Measurement.tobs,Measurement.date,Measurement.station).\
        filter(Measurement.station == most_active_12).\
        filter(Measurement.date>(dt.datetime.strptime(recent_date,"%Y-%m-%d")-dt.timedelta(days=365))).all()
    session.close()
    tobs_results = []

    for t, d, s in most_active_tobs:
        tobs_dict = {"Date": d, "Station ID": s, "TOBS": t}
        tobs_results.append(tobs_dict)
    return jsonify(tobs_results)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_or_end(start=None, end=None):
    session = Session(engine)
    if end == None:
        TMIN, TAVG, TMAX = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
            filter(Measurement.date >= (dt.datetime.strptime(start,"%Y-%m-%d"))).all()[0]
        return jsonify([{"TMIN":TMIN, "TAVG":round(TAVG,1), "TMAX":TMAX, "Start Date":start, "End Date": end}])
    if end !=None:
        TMIN, TAVG, TMAX = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
            filter(Measurement.date >= (dt.datetime.strptime(start,"%Y-%m-%d"))).\
            filter(Measurement.date <= (dt.datetime.strptime(end,"%Y-%m-%d"))).all()[0]
        return jsonify([{"TMIN":TMIN, "TAVG":round(TAVG,1), "TMAX":TMAX, "Start Date":start, "End Date":end}])
    session.close()
 

if __name__ == '__main__':
    app.run(debug=True)