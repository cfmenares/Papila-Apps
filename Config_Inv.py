#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 00:09:35 2020

@author: cmenares
"""


import netCDF4  as netCDF4
from netCDF4 import Dataset
import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
from plotly.offline  import plot
import plotly.graph_objects as go


Cont = ['PM10','PM25','O3','NO2']
cont = {'co': 'CO','nh3':'NH3','nox':'NOx','pm25': 'PM25','sox': 'SOx','voc': 'VOc'}
sector = {'Agricultura': 'snap:10', 'Energia' : 'snap:1', 'Otras fuentes'  :'snap:11', 
          'Industrias' : 'snap:3', 'Residencial' : 'snap:2', 'Transporte' : 'snap:7' ,
          'Total':'Total' }


colors = {
    'background': 'white',
    'text': '#7FDBFF',
    'background_2': 'white',
    'background_3': 'turquoise'

}


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 


x = ['PM<sub>10</sub>','PM<sub>2.5</sub>',  'O<sub>3</sub>' , 'NO<sub>2</sub>']

info_con = { 'PM10': 'PM<sub>10</sub> (Material grueso)', 
             'PM25': 'PM<sub>2.5</sub> (Material fino)',  
             'O3': 'O<sub>3</sub> (Ozono)' , 
             'NO2': 'NO<sub>2</sub> (Dioxido de nitrogeno)' ,              
             'NOx': 'NO<sub>x</sub> (Oxidos de nitrogeno)' ,              
             'CO': 'CO (Monoxido de carbono)' ,              
             'SOx': 'SO<sub>x</sub> (Oxidos de azufre)' ,              
             'VOc': 'SO<sub>x</sub> (Compuestos organicos volatiles)' ,              
             'NH3': 'SO<sub>x</sub> (Amoniaco)' ,              
             'AOD': 'AOD> (550nm)'}


model = ['Map-Puntos','Heat-Map']



def emis_map(especie,sector):
    
    
    
    dataset_hour = Dataset("edgar_STGO_" + especie + "_ALL_1x1km.nc")   # I_BBase_F_day   I_F3_Base_day.nc V_F_Base_day.nc
    print (dataset_hour.variables.keys())
    
    
    
    lat = dataset_hour.variables['lat'][:]
    lon = dataset_hour.variables['lon'][:]

    if sector == 'Total':    
        
        edgar_data = dataset_hour.variables[ cont[especie] + '_TOTAL'][:,:]
        
    else:
        edgar_data = dataset_hour.variables[ 'Emis:CHIL:'+ sector][:,:]

        
    aa,bb= np.meshgrid(lon,lat)
    lat_2 = np.reshape(aa,len(lat)*len(lon))
    lon_2 = np.reshape(bb,len(lat)*len(lon))
    
    
    dat_m = np.reshape(edgar_data, len(lat)*len(lon) )
    ppd = pd.DataFrame( { 'ton/año' :  dat_m.data , 'lon' : lat_2 , 'lat' : lon_2  }  )
    
    return(ppd)






app.layout = html.Div([
    
    html.H1(children='PAPILA - (CR)\u00B2     ',  style={'color': 'white', 'fontSize': 64, 'fontFamily': 'Times New Roman' , 'textAlign': 'right', 'font-weight': 0
                                                ,'backgroundColor': colors['background_3']}),
    html.Div([
        html.Div([
            html.H3(''),
            
                    html.Div([
                        
                        html.Label('Contaminante:  '),
                        dcc.Dropdown(
                            id='yaxis1',
                            options=[{'label': i.title(), 'value': i} for i in cont],
                            value='nox'
                            )
                        ],
                        style={'width': '30%', 'float': 'center', 'display': 'inline-block'}),

                    html.Div([
                        html.Label('Sector:  '),
                        dcc.Dropdown(
                            id='yaxis2',
                            options=[{'label': i.title(), 'value': i} for i in sector],
                            value='Total'
                            )
                        ],
                        style={'width': '30%', 'float': 'center', 'display': 'inline-block'}),


                    html.Div([
                    
                        dcc.RadioItems(
                            id='model',
                            options=[{'label': k, 'value': k} for k in model],
                            value='Map-Puntos' ,
                            labelStyle={'display': 'inline-block'} )] ,
                        style={'display': 'iblock'}) ,



            
            dcc.Graph(id='feature-map')
        ] , className="six columns"),
        

        html.Div([
            html.H3(''),
            
            dcc.Graph(id='feature-pie')
        ] ,   style={'marginLeft':75} , className="six columns"),


        
        ], className="row" ) , 
            ])


@app.callback(
    Output('feature-map', 'figure'),
    [Input('yaxis1', 'value'),
     Input('yaxis2', 'value'),
     Input('model', 'value')])
def update_graph(yaxi1_name, yaxi2_name, model_name):
    
    ppd = emis_map(yaxi1_name, sector[yaxi2_name])
#    ppd = ppd.replace(0, np.nan)

    if model_name == 'Map-Puntos':
        mapbox_access_token = 'pk.eyJ1IjoiY21lbmFyZXMiLCJhIjoiY2tlMmhjemdhMDliNDJ0cDhpbnBsM3pwNCJ9.M8QLY8mapIqR7_R70_dovw'
        px.set_mapbox_access_token(mapbox_access_token)
        
        fig = px.scatter_mapbox(ppd, lat="lat", lon="lon",     
                            color="ton/año", range_color = [0,ppd['ton/año'].quantile(0.995)],
                           zoom=8.3, opacity = 0.50, 
                           color_continuous_scale=["white", "orange", "red", "darkred"],
                           height=1100, width = 1200)
        
        # Colores y topografia
        
        # fig.update_layout(
        #     mapbox = {
        #         'style': "outdoors"},
        #     showlegend = False)
        
        # Calles estilo libre
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    elif model_name == 'Heat-Map' :
        
        fig = px.density_mapbox(ppd, lat='lat', lon='lon', z='ton/año', radius=8,
                                   zoom=8, range_color = [0,ppd['ton/año'].quantile(0.995)], 
                                   color_continuous_scale=["white" , "orange", "red", "darkred"],
                                 mapbox_style="stamen-terrain", height=1100, width = 1200)
    
    
    fig.update_layout(
        title= ' Inventario Edgar/Usach ' + info_con[cont[yaxi1_name]]  ,
        titlefont=dict(
        size=26,
        color='dimgrey'
            ),
            font=dict(
            family="Times New Roman",
            size=22,
            color="#7f7f7f"
        )
    )


    
    return fig


@app.callback(
    Output('feature-pie', 'figure'),
    [Input('yaxis1', 'value')])
def update_graph(yaxis1_name):

    labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
    values = [4500, 2500, 1053, 500]
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent',
                                 insidetextorientation='radial' , hole = 0.3
                                )])
    
    fig.update_layout(
    autosize=False,
    width=500,
    height=500,
)
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)





