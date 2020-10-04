import json
import pandas as pd
from decimal import Decimal
from flask_cors import CORS, cross_origin
from werkzeug.wrappers import Request, Response
from flask import Flask, jsonify, request
import os
from datetime import timedelta, date,datetime
from os import remove


app = Flask(__name__)

cors = CORS(app)
data_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'  
data = pd.read_csv(data_url)

app.config['CORS_HEADERS'] = 'Content-Type'

lista = data.iloc[:,4:].columns
dataRegion = pd.melt(data, id_vars =['Country/Region','Province/State'], value_vars =lista)

groupData = dataRegion.groupby(['Country/Region','variable'])['value'].sum().reset_index()
groupData['Date'] =pd.to_datetime(groupData.variable)

def estado(df, columna):
    for i in range(1,len(df)):
        if (df[columna].loc[i] - df[columna].loc[i-1])>25:
            df.loc[i-1,'estado'] = True
            df.loc[i,'estado'] = False
        else:
            df.loc[i-1,'estado'] = False
    return df

def pais(pais,df):
    country = df[df["Country/Region"]==pais]
    country['Date'] =pd.to_datetime(country.variable)
    country = country.sort_values(by=['Date'])
    countryDf = country.reset_index()[::30].reset_index()
    total = countryDf["value"].max()
    countryDf["porcentaje"]= countryDf["value"].astype("int").div(total)*100
    countryDf = estado(countryDf,"porcentaje")
    labelY = list(countryDf.loc[:,"Date"].astype("string"))
    lenRows = countryDf.shape[0]
    valuesDf = countryDf.loc[:,"value"]
    rowGrow = countryDf[countryDf["estado"]==True]
    totalMeses = pd.DataFrame()
    for index,row in rowGrow.iterrows():
        porpais = df[df["Country/Region"]==pais].reset_index()
        index = porpais[porpais["variable"]==row["variable"]].index
        porpais = porpais.sort_values(by=['Date'])
        hotMonth = porpais.iloc[index[0]:index[0]+30]
        hotMonthY = list(hotMonth.loc[:,"Date"].astype("string"))
        hotMonthRows = hotMonth.shape[0]
        hotMonthDf = hotMonth.loc[:,"value"]
        dataFrameMes = pd.concat([pd.DataFrame(hotMonthY).reset_index(drop=True), pd.DataFrame(hotMonthDf).reset_index(drop=True)], axis=1)
        totalMeses = pd.concat([totalMeses.reset_index(drop=True), dataFrameMes.reset_index(drop=True)], axis=0)
        #datos = jsonify({'datosFecha' : {'fechas': pd.DataFrame(hotMonthY).to_json(), 'valores': pd.DataFrame(hotMonthDf).to_json()}})
        #datosPorJson.append(datos)
    totalDatos = pd.concat([pd.DataFrame(labelY).reset_index(drop=True), pd.DataFrame(valuesDf).reset_index(drop=True)], axis=1)
    totalDatos.columns = ['fechaTotal','datosTotal']
    totalMeses.columns = ['fecha','datos']
    totalDatos = totalDatos.reset_index(drop=True)
    totalMeses = totalMeses.reset_index(drop=True)
    return totalDatos,totalMeses

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
    totalDatos, totalMeses = pais(country,groupData)
    print(totalDatos,totalMeses)
    return jsonify({'totalDatos': totalDatos.to_json(), 'totalMeses': totalMeses.to_json()})
    #return 'ds'
    
if __name__ == "__main__":
    app.run()