from flask import Flask,jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

engine = create_engine(f"sqlite:///Resources/hawaii.sqlite")
Base=automap_base()
Base.prepare(engine,reflect=True)
Measurement=Base.classes.measurement
Station=Base.classes.station

app=Flask(__name__)

@app.route("/")
def home():
    return (
        f" /api/v1.0/precipitation<br/>"
        f" /api/v1.0/stations<br/>"
        f" /api/v1.0/tobs<br/>"
        f" /api/v1.0/<start><br/>"
        f" /api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session=Session(engine)
    last_date_q=session.query(func.max(func.strftime("%Y-%m-%d",Measurement.date))).first()
    last_date=dt.datetime.strptime(last_date_q[0],"%Y-%m-%d")
    start_date=last_date-dt.timedelta(days=365)
    res=session.query(Measurement.date,Measurement.prcp).\
                filter(func.strftime("%Y-%m-%d",Measurement.date)>=start_date).all()
    session.close()
    prec=[]
    for date, prcp in res:
        daily_result={}
        daily_result["date"]=date
        daily_result["prcp"]=prcp
        prec.append(daily_result)
    return jsonify(prec)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    station_results=session.execute("select * from Station").fetchall()
    session.close()
    stations_list=[]
    for id,station,name,latitude,longitude,elevation in station_results:
        station_info={}
        station_info["id"]=id
        station_info["station"]=station
        station_info["name"]=name
        station_info["latitude"]=latitude
        station_info["longitude"]=longitude
        station_info["elevation"]=elevation
        stations_list.append(station_info)
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    last_date_query=session.query(func.max(func.strftime("%Y-%m-%d",Measurement.date))).first()
    last_date=dt.datetime.strptime(last_date_query[0],"%Y-%m-%d")
    start_date=last_date-dt.timedelta(days=365)
    station_rows=session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station=station_rows[0][0]
    tobs_results=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==most_active_station).\
                filter(func.strftime("%Y-%m-%d",Measurement.date)>=start_date).all()
    session.close()
    temp_list=[]
    for date,tob in tobs_results:
        temp={}
        temp["station"]=most_active_station
        temp["date"]=date
        temp["tobs"]=tob
        temp_list.append(temp)
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def cal_temp1(start):
    start_date=func.strftime("%Y-%m-%d",start)
    session=Session(engine)
    temperatures=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()
    result={}
    result["minimum temperature"]=temperatures[0][0]
    result["average temperature"]=round(temperatures[0][1],4)
    result["maximum temperature"]=temperatures[0][2]
    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def cal_temp2(start,end):
    start_date=func.strftime("%Y-%m-%d",start)
    end_date=func.strftime("%Y-%m-%d",end)
    session=Session(engine)
    temperatures=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=start_date).filter(Measurement.date<=end_date).all()
    session.close()
    result={}
    result["minimum temperature"]=temperatures[0][0]
    result["average temperature"]=round(temperatures[0][1],4)
    result["maximum temperature"]=temperatures[0][2]
    return jsonify(result)       

if __name__=="__main__":
    app.run(debug=True)