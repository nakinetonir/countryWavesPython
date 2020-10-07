import pandas as pd
from decimal import Decimal
from datetime import timedelta, date,datetime

def estado(df, columna):
    for i in range(1,len(df)):
        if i-1 == 0:
            df.loc[i-1,'estado'] = False
        if (df[columna].loc[i] - df[columna].loc[i-1])>20:
            df.loc[i,'estado'] = True
        else:
            df.loc[i,'estado'] = False
    return df

def pais(pais,df):
    country = df[df["Country/Region"]==pais]
    country['Date'] =pd.to_datetime(country.variable)
    country = country.sort_values(by=['Date']).groupby(country['Date'].dt.strftime('%B')).max().sort_values(by=['value']) 
    total = country["value"].max()
    country["porcentaje"]= country["value"].astype("int").div(total)*100
    country["mes"] = country.index
    country.rename(columns = {'Date':'Fecha'}, inplace = True) 
    country = country.reset_index()
    country = estado(country,"porcentaje")
    labelY = list(country.loc[:,"Date"].astype("string"))
    lenRows = country.shape[0]
    valuesDf = country.loc[:,"value"]
    rowGrow = country[country["estado"]==True]
    totalMeses = pd.DataFrame()
    for index,row in rowGrow.iterrows():
        porpais = df[df["Country/Region"]==pais].reset_index()
        disMes = porpais[porpais['MesDate'] == row["mes"]]
        disMes = disMes.sort_values(by=['Date'])
        hotMonthY = list(disMes.loc[:,"variable"])
        hotMonth = list(disMes.loc[:,"MesDate"])
        hotMonthRows = disMes.shape[0]
        hotMonthDf = disMes.loc[:,"value"]
        dataFrameMes = pd.concat([pd.DataFrame(hotMonth).reset_index(drop=True),pd.DataFrame(hotMonthY).reset_index(drop=True), pd.DataFrame(hotMonthDf).reset_index(drop=True)], axis=1)
        totalMeses = pd.concat([totalMeses.reset_index(drop=True), dataFrameMes.reset_index(drop=True)], axis=0)
    totalDatos = pd.concat([pd.DataFrame(labelY).reset_index(drop=True), pd.DataFrame(valuesDf).reset_index(drop=True)], axis=1)
    totalDatos.columns = ['fechaTotal','datosTotal']
    totalMeses.columns = ['MesDate','fecha','datos',]
    totalDatos = totalDatos.reset_index(drop=True)
    totalMeses = totalMeses.reset_index(drop=True)
    return totalDatos,totalMeses,total
