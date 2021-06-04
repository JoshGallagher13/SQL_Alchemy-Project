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
Base = automap_base()
Base.prepare(engine, reflect=True)
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/measurements<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date   (YYYY-MM-DD)<br/>"
        f"/api/v1.0/start date/end date (YYYY-MM-DD)"
    )

@app.route("/api/v1.0/measurements")
def measurements():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()

    measure_data = []
    for date, prcp in results:
        measure_dict = {}
        measure_dict["date"] = date
        measure_dict["prcp"] = prcp
        measure_data.append(measure_dict)

    return jsonify(measure_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
 
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent = session.query(measurement).order_by(measurement.date.desc()).first()
    most_recent_split = most_recent.date.split("-")
    yearago = str(int(most_recent_split[0])-1)+"-"+most_recent_split[1]+"-"+most_recent_split[2]
    stayshs=session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    staysh=stayshs[0][0]
    temp_last_year = session.query(measurement.date, measurement.tobs).filter(measurement.date <= f"{most_recent}").filter(measurement.date >= f"{yearago}").filter(measurement.station == f"{staysh}")
    session.close()
    
    lastyear_data = []
    for date, tobs in temp_last_year:
        lastyear_dict = {}
        lastyear_dict["date"] = date
        lastyear_dict["tobs"] = tobs
        lastyear_data.append(lastyear_dict)

    return jsonify(f"One year of measurements for station: {staysh}    "
                   f"{lastyear_data}")
    
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= f"{start}")
    session.close()
    
    start_data = []
    for min_T, avg_T, max_T in results:
        start_dict = {}
        start_dict["Min Temp"] = min_T
        start_dict["Avg Temp"] = avg_T
        start_dict["Max Temp"] = max_T
        start_data.append(start_dict)
        
    return jsonify(f"From start date: {start}   "
                   f"{start_data}")
    
    
@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= f"{start}").filter(measurement.date <= f"{end}")
    session.close()
    
    startend_data = []
    for min_T, avg_T, max_T in results:
        startend_dict = {}
        startend_dict["Min Temp"] = min_T
        startend_dict["Avg Temp"] = avg_T
        startend_dict["Max Temp"] = max_T
        startend_data.append(startend_dict)
        
    return jsonify(f"From start date: {start} to {end}    "
                   f"{startend_data}")
    
    
    
    
if __name__ == '__main__':
    app.run(debug=True)