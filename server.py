import json
import pandas as pd
from decimal import Decimal
from flask_cors import CORS, cross_origin
from werkzeug.wrappers import Request, Response
from flask import Flask, jsonify, request
import os
from datetime import timedelta, date,datetime
from os import remove
from flask_apscheduler import APScheduler
from modules import countries
class Config(object):
    SCHEDULER_API_ENABLED = True

scheduler = APScheduler()

def initData(data):
    lista = data.iloc[:,4:].columns
    dataRegion = pd.melt(data, id_vars =['Country/Region','Province/State'], value_vars =lista)

    groupData = dataRegion.groupby(['Country/Region','variable'])['value'].sum().reset_index()
    groupData['Date'] =pd.to_datetime(groupData.variable)
    groupData['MesDate'] = groupData['Date'].dt.strftime('%B')
    return groupData

app = Flask(__name__)

cors = CORS(app)
data_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
data = pd.read_csv(data_url)
groupData = initData(data)

@scheduler.task('cron', id='cargarDatos', hour=10, minute=10)
def cargarDatos():
    data_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    global data
    global groupData
    data = pd.read_csv(data_url)
    print(data)
    groupData = initData(data)


app.config['CORS_HEADERS'] = 'Content-Type'





@app.route('/', methods=['GET'])
@cross_origin()
def getPrueba():
    return "Hola"

@app.route('/postDataCountry', methods=['POST'])
@cross_origin()
def getDataCountry():
    global groupData
    country = request.get_json()
    print(country)
    totalDatos, totalMeses, total = countries.pais(country,groupData)
    print(totalDatos,totalMeses)
    return jsonify({'totalDatos': totalDatos.to_json(), 'totalMeses': totalMeses.to_json(), 'totalCasos' : str(total)})
    #return 'ds'

if __name__ == "__main__":

    app.config.from_object(Config())

    # it is also possible to enable the API directly
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()
    app.run()