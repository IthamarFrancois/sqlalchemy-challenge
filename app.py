## Part 2 - Climate App
## Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.
## Use Flask to create your routes.

import numpy as np
import pandas as pd
import datetime as dt
import os
from flask import Flask, jsonify
import json

## Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy import create_engine, func, Column, Integer, String, Float, desc, inspect, or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base


#############################   Database Setup  #############################

## Create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

## reflect an existing database into a new model
Base = automap_base()

## To reflect the returned tables 
Base.prepare(engine, reflect=True)


## Save references to each table
Measurement = Base.classes.measurement
Station  = Base.classes.station 

## Create session 
session = Session(bind=engine)


#############################  Define Variables #############################


## Find the most recent date in the data set. 
MostRecentDate = session.query(Measurement.date).order_by(Measurement.date.desc()).first() ## Using descending order, return 'first' Measurement date
MostRecentDate = MostRecentDate[0]  ## Convert date to just a string
#print(MostRecentDate)

## Calculates the date one year from the last date in data set
OneYearPriorDate = dt.datetime.strptime(MostRecentDate, '%Y-%m-%d') - dt.timedelta(365,0,0)
OneYearPriorDate = OneYearPriorDate.date()
#print(OneYearPriorDate)

## Close session/check to not leave it open
session.close


## Reprint of table data for reference
## Measurement Table
## id INTEGER
## station TEXT
## date TEXT
## prcp FLOAT
## tobs FLOAT
## 
## Station Table
## id INTEGER
## station TEXT
## name TEXT
## latitude FLOAT
## longitude FLOAT
## elevation FLOAT

#############################  Initialize Flask #############################

app = Flask(__name__)

##########################################################    FLASK / API Routes   ##########################################################

@app.route("/")
## Home page

def WelcomePage():
    ## Create session to start page
    session = Session(engine)
    
    ## List all routes that are available.
    return(
    
    "<h1> Welcome to Honolulu, Hawaii! </h1><br>"   
    "Please Select Available Routes Below for More Info: <br>"    
    "***************************************<br><br>"
    
    "View the temperature precipitation on specific dates <br>"
    "<strong> /api/v1.0/precipitation </strong><br><br>"

    "View the reporting weather stations, and their loctaions <br>"
    "<strong> /api/v1.0/stations </strong><br><br>"

    "View the temerature observation data from the most active station for the last recorded year <br>"
    "<strong> /api/v1.0/tobs </strong><br><br>"
    
    "View the minimum, average, and maximum temeratures recorded from a start date <br>"
    "<strong> /api/v1.0/start </strong><br><br>"
    
    "View the minimum, average, and maximum temeratures recorded in between a start and end date <br>"
    "<strong> /api/v1.0/start/end </strong><br>"
    
    "***************************************"            
    )

# ------------------------------------- #

@app.route("/api/v1.0/precipitation")
def precipitation():

    ## Create session to start page
    session = Session(engine)

    ## Convert the query results to a dictionary using `date` as the key and `prcp` as the value
    QResults = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= OneYearPriorDate).order_by(Measurement.date).all()
    
    session.close()
    
    ## Changes returned query to dict
    Precip_Dict = dict(QResults)
    #Precip_Dict

    ## Convert Dictionary to Dataframe, add column titles for labeling, and drop any Null values in order to convert DF back to json
    Precip_DF = pd.DataFrame(list(Precip_Dict.items()), columns = ["Date", "Precipitation"])
    Precip_DF = Precip_DF.dropna(how = 'any')
    Precip_DF.head(10)

    ## Covert DataFrame to json in order return via jsonify
    Precip_DF = json.loads(Precip_DF.to_json(orient = 'records'))
    #Precip_DF
    
    ## Return the JSON representation of your dictionary.
    return jsonify(Precip_DF)

# ------------------------------------- #


@app.route("/api/v1.0/stations")
## Return a JSON list of stations from the dataset.

def stations():
    ## Create session to start page
    session = Session(engine)
    
    ## Query for list of stations
    StationsQuery = session.query(Station.station, Station.name).all()
    
    ## Close session/check to not leave it open
    session.close()
    
    ## Changes returned query to dictionary
    Stations_Dict = dict(StationsQuery)
    
    ## Convert Dictionary to Dataframe, add column titles for labeling, and drop any Null values in order to convert DF back to json
    Stations_DF = pd.DataFrame(list(Stations_Dict.items()), columns = ["Station ID", "Location"])
    Stations_DF = Stations_DF.dropna(how = 'any')
    Stations_DF.head(10)

    ## Covert DataFrame to json in order return via jsonify
    Stations_DF = json.loads(Stations_DF.to_json(orient = 'records'))
    #Precip_DF
    
    ## Return the JSON representation.
    return jsonify(Stations_DF)

# ------------------------------------- #  
    
    
@app.route("/api/v1.0/tobs")
## Return a JSON list of temperature observations (TOBS) for the previous year.

def tobs():
    
    ## Create session
    session = Session(engine)
    
    ## Querying the total stations and their row of data count to narrow down the most active station for the last year of data.
    MostActiveStations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).filter(Measurement.date >= OneYearPriorDate).filter(Measurement.date <= MostRecentDate).\
            order_by(func.count(Measurement.station).desc()).all()

    ## First station listed (index[0] = 'USC00519397', 361) is the most active with 361 rows for this date range, so will use this for filtering
    TheMostActiveStation = MostActiveStations[0][0]     #TheMostActiveStation   # = Station ID: 'USC00519397'
    
    ## Using the most active station ID/string, we will only look for that station's tobs and date data to convert to dataframe
    ActiveStationTobs  = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= OneYearPriorDate).filter(Measurement.date <= MostRecentDate).\
            filter(Measurement.station == TheMostActiveStation).all()

    ## Close session/check to not leave it open
    session.close()
    
    ## Changes returned query to dictionary
    ActiveTobs_Dict = dict(ActiveStationTobs)
    ActiveTobs_Dict

    ## Convert Dictionary to Dataframe, add column titles for labeling, and drop any Null values in order to convert DF back to json
    ActiveTobs_DF = pd.DataFrame(list(ActiveTobs_Dict.items()), columns = ["Date", "Observed Temp (TOBS)"])
    ActiveTobs_DF = ActiveTobs_DF.dropna(how = 'any')
    ActiveTobs_DF.head(10)

    ## Covert DataFrame to json in order return via jsonify
    ActiveTobs_DF = json.loads(ActiveTobs_DF.to_json(orient = 'records'))
    ActiveTobs_DF

    print (f"<h1> Welcome to Honolulu, Hawaii! </h1><br>")
    
    ## Return the JSON representation.
    return jsonify(ActiveTobs_DF)
    
# ------------------------------------- #


@app.route("/api/v1.0/<start>")
## Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start

def StartRange(start):
    
    ## Create session 
    session = Session(engine)
    
    ## When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    StartQuery = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= OneYearPriorDate).group_by(Measurement.date).all()
    #StartQuery

    ## Close session/check to not leave it open
    session.close()

    ## Changes returned query to dictionary
    Start_List = list(StartQuery)
    #StartQuery


    ### Convert Dictionary to Dataframe, add column titles for labeling, and drop any Null values in order to convert DF back to json
    Start_DF = pd.DataFrame(Start_List, columns = ["Date", "TMIN", "TAVG", "TMAX"])
    Start_DF = Start_DF.dropna(how = 'any')
    Start_DF.head(10)

    ### Covert DataFrame to json in order return via jsonify
    Start_DF = json.loads(Start_DF.to_json(orient = 'records'))
    #Start_DF
    
    ## Return the JSON representation.
    return jsonify(Start_DF)

# ------------------------------------- #

@app.route("/api/v1.0/<start>/<end>")
## Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a start-end range

def StartEndRange(start, end):
    
    ## Create session 
    session = Session(engine)
    
    ## When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    StartEndQuery = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= OneYearPriorDate).filter(Measurement.date <= MostRecentDate).all()
    #StartEndQuery

    ## Close session/check to not leave it open
    session.close()

    ## Changes returned query to dictionary
    StartEnd_List = list(StartEndQuery)
    #StartEnd_List


    ### Convert Dictionary to Dataframe, add column titles for labeling, and drop any Null values in order to convert DF back to json
    StartEnd_DF = pd.DataFrame(StartEnd_List, columns = ["Date", "TMIN", "TAVG", "TMAX"])
    StartEnd_DF = StartEnd_DF.dropna(how = 'any')
    StartEnd_DF.head(10)

    ### Covert DataFrame to json in order return via jsonify
    StartEnd_DF = json.loads(StartEnd_DF.to_json(orient = 'records'))
    #StartEnd_DF
    
    ## Return the JSON representation.
    return jsonify(StartEnd_DF)

    

#############################  Flask End  #############################

if __name__ == "__main__":
    app.run(debug=True)

## ________________________________________ Ithamar Francois ______________________________________________________ ##
