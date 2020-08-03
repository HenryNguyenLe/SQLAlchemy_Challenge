# import SQLAlchemy toolkit
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# import datetime module to calculate delta time
import datetime as dt

# other dependencies from pandas and numpy modules
import numpy as np
import pandas as pd
import requests
import json

# set up app by flask
from flask import Flask, jsonify, render_template, url_for, redirect, request
import logging

logging.basicConfig(level=logging.DEBUG)


# create connection and map out database using SQLAlchemy
engine = create_engine("sqlite:///Resources/hawaii.sqlite") # , connect_args={'check_same_thread': False}
Base = automap_base()
Base.prepare(engine, reflect=True)

# assign table names from database
station = Base.classes['station']
measurement = Base.classes['measurement']

# create session connection to query data
# session = Session(engine)

#################################################
#                   Flask Setup
#################################################
app = Flask(__name__)


#################################################
#               Flask RESTful APIs
#################################################

# create Home page and list all routes that are available.
@app.route("/")
def welcome():
    # Homepage
    return render_template("index.html")

# access database and get all temperature data
# covert all temps to json format
@app.route("/api/precipitation")
def get_precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).all()
    prcp_dict = dict(results)
    return jsonify(prcp_dict)
    session.close()

# create a json list of stations from the dataset
@app.route("/api/stations")
def get_stations():
    session = Session(engine)
    results = session.query(measurement.station).group_by(measurement.station).all()
    # list comprehension
    station_list = [station[0] for station in results] 
    return jsonify(station_list) 
    session.close()

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/tobs")
def get_1yr_temp():

    session = Session(engine)
    # query entire table to find all station, group by station name and count # of data points
    # sort from largest to smallest by # of data points
    prp_station = session.query(measurement.station,func.count(measurement.station))\
        .group_by(measurement.station)\
        .order_by(func.count(measurement.station).desc()).all()

    # return the top station name 
    top_station_id = prp_station[0][0]
      
    # find this top station temperature data
    tempQuery = session.query(measurement.date, measurement.prcp).all()
    last_date = dt.datetime.strptime(tempQuery[-1][0], '%Y-%m-%d')

    # Calculate the date 1 year ago from the last data point in the database & convert data into dataframe
    query_date  = last_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    most_active_station_temp = session.query(measurement.tobs)\
        .filter(measurement.date > query_date)\
        .filter(measurement.station == top_station_id).all()
    # list comprehension to get all temps into a list
    temp_list = [temp[0] for temp in most_active_station_temp]
    
    # convert name and temps into a dictionary
    temp_dict = {top_station_id : temp_list}
    return jsonify(temp_dict)
    session.close() 



# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/startdate=<start>")
def get_temps_start(start):
    session = Session(engine)
    # get the first and last date of the whole dataset
    prp_tpl = session.query(measurement.date, measurement.prcp).all() 
    first_date = dt.datetime.strptime(prp_tpl[0][0], '%Y-%m-%d')
    last_date = dt.datetime.strptime(prp_tpl[-1][0], '%Y-%m-%d')

    # convert the input to datetime format
    start = dt.datetime.strptime(start, '%Y-%m-%d')

    # Test to see if the input date is within range, if not return error
    if start < first_date or start > last_date:
        return jsonify({"error" : "Input date is out of range!"},
                {"the first available date" : first_date},
                {"the last available date" : last_date}  
        ), 404
    else:
        tempQ= session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
        tempdict = {
            "min" : tempQ[0][0],
            "avg" : round(tempQ[0][1], 2),
            "max" : tempQ[0][2],
        }
        return jsonify(tempdict)
    session.close() 


# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/startdate=<start>/enddate=<end>/")
def get_temps_start_end(start, end):
    session = Session(engine)

    # get the first and last date of the whole dataset
    prp_tpl = session.query(measurement.date, measurement.prcp).all() 
    first_date = dt.datetime.strptime(prp_tpl[0][0], '%Y-%m-%d')
    last_date = dt.datetime.strptime(prp_tpl[-1][0], '%Y-%m-%d')

    # convert the input to datetime format
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    end_date_com = end_date
    start_date_com = start_date

    # Test to see if the input date is within range, if not return error
    if start_date < first_date or start_date > last_date:
        return jsonify({
            "error": "start_date_is_out_of_range!",
            "the_first_available_date": first_date,
            "the_last_available_date": last_date
        }), 404

    elif end_date < first_date or end_date > last_date:
        return jsonify({
            "error": "end_date_is_out_of_range!",
            "the_first_available_date": first_date,
            "the_last_available_date": last_date
        }), 404

    else:
        
    # if the start date and end date were reversely input, auto-correct
        if start_date > end_date:
            start_date = end_date_com
            end_date = start_date_com
        tempQ= session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date >= end_date).all()
        tempdict = {
            "min" : tempQ[0][0],
            "avg" : round(tempQ[0][1], 2),
            "max" : tempQ[0][2],
        }
        return jsonify(tempdict)
    session.close() 

# example route to allow user input date in each box and get results back
# using Flask POST method
@app.route('/example', methods = ['POST'])
def example():
    if request.method == 'POST':
        # get input from html forms
        sdate = request.form["sdate"]
        edate = request.form["edate"]

        # get current hosting URL
        base_url = request.host_url

        # build custom JSON URL to get data from other Flask Route
        q_url = base_url + f'api/startdate={sdate}/enddate={edate}/'
        # parse data from json formatted response
        response = json.loads(requests.get(q_url).text)
    
    # reponse then display on index with jinja connection    
    return render_template('index.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)
