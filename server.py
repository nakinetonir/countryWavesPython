{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "import pandas as pd\n",
    "from decimal import Decimal\n",
    "from flask_cors import CORS, cross_origin\n",
    "from werkzeug.wrappers import Request, Response\n",
    "from flask import Flask, jsonify, request\n",
    "import os\n",
    "from datetime import timedelta, date,datetime\n",
    "from os import remove"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app \"__main__\" (lazy loading)\n",
      " * Environment: production\n",
      "   WARNING: This is a development server. Do not use it in a production deployment.\n",
      "   Use a production WSGI server instead.\n",
      " * Debug mode: off\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)\n",
      "127.0.0.1 - - [04/Oct/2020 18:39:19] \"\u001b[37mGET /prueba HTTP/1.1\u001b[0m\" 200 -\n",
      "127.0.0.1 - - [04/Oct/2020 18:39:20] \"\u001b[33mGET /favicon.ico HTTP/1.1\u001b[0m\" 404 -\n"
     ]
    }
   ],
   "source": [
    "app = Flask(__name__)\n",
    "\n",
    "cors = CORS(app)\n",
    "data_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'  \n",
    "data = pd.read_csv(data_url)\n",
    "\n",
    "app.config['CORS_HEADERS'] = 'Content-Type'\n",
    "\n",
    "lista = data.iloc[:,4:].columns\n",
    "dataRegion = pd.melt(data, id_vars =['Country/Region','Province/State'], value_vars =lista)\n",
    "\n",
    "groupData = dataRegion.groupby(['Country/Region','variable'])['value'].sum().reset_index()\n",
    "groupData['Date'] =pd.to_datetime(groupData.variable)\n",
    "\n",
    "def estado(df, columna):\n",
    "    for i in range(1,len(df)):\n",
    "        if (df[columna].loc[i] - df[columna].loc[i-1])>25:\n",
    "            df.loc[i-1,'estado'] = True\n",
    "            df.loc[i,'estado'] = False\n",
    "        else:\n",
    "            df.loc[i-1,'estado'] = False\n",
    "    return df\n",
    "\n",
    "def pais(pais,df):\n",
    "    country = df[df[\"Country/Region\"]==pais]\n",
    "    country['Date'] =pd.to_datetime(country.variable)\n",
    "    country = country.sort_values(by=['Date'])\n",
    "    countryDf = country.reset_index()[::30].reset_index()\n",
    "    total = countryDf[\"value\"].max()\n",
    "    countryDf[\"porcentaje\"]= countryDf[\"value\"].astype(\"int\").div(total)*100\n",
    "    countryDf = estado(countryDf,\"porcentaje\")\n",
    "    labelY = list(countryDf.loc[:,\"Date\"].astype(\"string\"))\n",
    "    lenRows = countryDf.shape[0]\n",
    "    valuesDf = countryDf.loc[:,\"value\"]\n",
    "    rowGrow = countryDf[countryDf[\"estado\"]==True]\n",
    "    totalMeses = pd.DataFrame()\n",
    "    for index,row in rowGrow.iterrows():\n",
    "        porpais = df[df[\"Country/Region\"]==pais].reset_index()\n",
    "        index = porpais[porpais[\"variable\"]==row[\"variable\"]].index\n",
    "        porpais = porpais.sort_values(by=['Date'])\n",
    "        hotMonth = porpais.iloc[index[0]:index[0]+30]\n",
    "        hotMonthY = list(hotMonth.loc[:,\"Date\"].astype(\"string\"))\n",
    "        hotMonthRows = hotMonth.shape[0]\n",
    "        hotMonthDf = hotMonth.loc[:,\"value\"]\n",
    "        dataFrameMes = pd.concat([pd.DataFrame(hotMonthY).reset_index(drop=True), pd.DataFrame(hotMonthDf).reset_index(drop=True)], axis=1)\n",
    "        totalMeses = pd.concat([totalMeses.reset_index(drop=True), dataFrameMes.reset_index(drop=True)], axis=0)\n",
    "        #datos = jsonify({'datosFecha' : {'fechas': pd.DataFrame(hotMonthY).to_json(), 'valores': pd.DataFrame(hotMonthDf).to_json()}})\n",
    "        #datosPorJson.append(datos)\n",
    "    totalDatos = pd.concat([pd.DataFrame(labelY).reset_index(drop=True), pd.DataFrame(valuesDf).reset_index(drop=True)], axis=1)\n",
    "    totalDatos.columns = ['fechaTotal','datosTotal']\n",
    "    totalMeses.columns = ['fecha','datos']\n",
    "    totalDatos = totalDatos.reset_index(drop=True)\n",
    "    totalMeses = totalMeses.reset_index(drop=True)\n",
    "    return totalDatos,totalMeses\n",
    "\n",
    "@app.route('/prueba', methods=['GET'])\n",
    "@cross_origin()\n",
    "def getPrueba():\n",
    "    return \"Hola\"\n",
    "\n",
    "@app.route('/postDataCountry', methods=['POST'])\n",
    "@cross_origin()\n",
    "def getDataCountry():\n",
    "    global groupData\n",
    "    country = request.get_json()\n",
    "    print(country)\n",
    "    totalDatos, totalMeses = pais(country,groupData)\n",
    "    print(totalDatos,totalMeses)\n",
    "    return jsonify({'totalDatos': totalDatos.to_json(), 'totalMeses': totalMeses.to_json()})\n",
    "    #return 'ds'\n",
    "    \n",
    "if __name__ == \"__main__\":\n",
    "    app.run()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
