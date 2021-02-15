import numpy as np
import pandas as pd
import datetime as dt

# sqlalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# flask 
from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflection
Base = automap_base()
Base.prepare(engine, reflect = True)

# save reference
Station = Base.classes.station
Measurement = Base.classes.measurement

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to Hawaii Weather!<br>"
        f"Available routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&ltstart&gt<br>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt<br>"
        f"&ltstart&gt/&ltend&gt format YYYYMMDD"
        )

@app.route("/api/v1.0/precipitation")
def prcp():
    result = {}
    session = Session(bind=engine)
    prcp = session.query(Measurement.station, Measurement.date, Measurement.prcp)
    session.close()
    for p in prcp:
        if p.station in result:
            result[p.station][p.date] = p.prcp
        else:
            result[p.station] = {p.date : p.prcp}
    return jsonify(result)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(bind = engine)
    stations  = session.query(Station).all()
    session.close()
    result = [{
        "Station ID" : x.id,
        "Station" : x.station,
        "Name" : x.name
    } for x in stations]
    return jsonify(result)

@app.route("/api/v1.0/tobs")
def tobs():
    # use 2017-08-23 as today
    today = dt.date(2017,8,23)
    last_year = today - dt.timedelta(days=365)
    # get the most active station
    session = Session(bind = engine)
    station_count = session.query(Measurement.station, func.count(Measurement.station)).\
        filter(Measurement.date >= last_year).filter(Measurement.date < today).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    most_active = station_count.station
    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active).\
        filter(Measurement.date >= last_year).filter(Measurement.date < today).all()
    session.close()
    result = list(np.ravel(tobs))
    return jsonify(result)

@app.route("/api/v1.0/<int:start>")
def start(start):
    str_start = str(start)
    #result = str_start[0:4] + str_start[4:6] + str_start[6:8]
    start_date = dt.date(int(str_start[0:4]), int(str_start[4:6]), int(str_start[6:8]))
    session = Session(bind = engine)
    temp =  session.query(func.min(Measurement.tobs).label("tmin"), func.max(Measurement.tobs).label("tmax"), func.avg(Measurement.tobs).label("tavg")).\
        filter(Measurement.date >= start_date).first()
    session.close()
    result = {
        "Start Date" : str_start[0:4] + "-" + str_start[4:6] + "-" + str_start[6:8],
        "TMIN" : temp.tmin,
        "TMAX" : temp.tmax,
        "TAVG" : temp.tavg
    }
    return jsonify(result)
    #return result

@app.route("/api/v1.0/<int:start>/<int:end>")
def startend(start, end):
    if start > end:
        tmp = start
        start = end
        end = tmp
    str_start = str(start)
    start_date = dt.date(int(str_start[0:4]), int(str_start[4:6]), int(str_start[6:8]))
    str_end = str(end)
    end_date = dt.date(int(str_end[0:4]), int(str_end[4:6]), int(str_end[6:8]))

    session = Session(bind = engine)
    temp =  session.query(func.min(Measurement.tobs).label("tmin"), func.max(Measurement.tobs).label("tmax"), func.avg(Measurement.tobs).label("tavg")).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).first()
    session.close()
    result = {
        "Start Date" : str_start[0:4] + "-" + str_start[4:6] + "-" + str_start[6:8],
        "End Date" : str_end[0:4] + "-" + str_end[4:6] + "-" + str_end[6:8],
        "TMIN" : temp.tmin,
        "TMAX" : temp.tmax,
        "TAVG" : temp.tavg
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)