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
    #prcp=0
    #dates=0
    #station=0
    #prcp_dict = {"date":dates, "prcp":prcp,"station":station}
    results=[]
    recent_date = session.query(Measurement.date, Measurement.prcp, Measurement.station).order_by(Measurement.date.asc()).all()
    for d, p, s in recent_date:
        prcp_dict = {"date":d, "prcp":p,"station":s}
        results.append(prcp_dict)
    return (jsonify(results))

if __name__ == '__main__':
    app.run(debug=True)