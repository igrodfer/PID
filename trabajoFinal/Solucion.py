# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 15:06:35 2022

@author: jlluch
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

APP_TITLE = 'Paro por provincias, sexo y trimestre'
APP_SUB_TITLE = 'Fuente: Ine'

def display_time_filters(df, sex):
    year_list = list(df['Año'].unique())
    year_list.sort(reverse = True )
    year = st.sidebar.selectbox('Año', year_list, 0)
    if year == 2023:
        quarter = st.sidebar.radio('Trimestre', [1])
    else:
        quarter = st.sidebar.radio('Trimestre', [1, 2, 3, 4])
    st.header(f'{year} T{quarter} - {sex}' )
    return year, quarter

def display_prov_filter(df, prov):
    
    return st.sidebar.selectbox('Provincia', prov_list)

def display_sex_filter():
    return st.sidebar.radio('Sexo', ['Ambos sexos', 'Hombres', 'Mujeres'])


def display_map(df, year, quarter, sex):
    df = df[(df['Año'] == year) & (df['Trimestre'] == quarter) & (df['Sexo'] == sex)]

    m = folium.Map(location=[40.42,  -3.7], zoom_start=5)
    coropletas = folium.Choropleth(geo_data=prov_geo,name="choropleth",data=df,columns=["codigo", "Paro"],key_on="properties.codigo", fill_color="YlGn",fill_opacity=0.7,line_opacity=1.0,legend_name="Tasa de Paro (%)")
    coropletas.add_to(m)
    for feature in coropletas.geojson.data['features']:
       code = feature['properties']['codigo']
       feature['properties']['Provincia'] = prov_dict[code]
    coropletas.geojson.add_child(folium.features.GeoJsonTooltip(['Provincia'], labels=False))
    
    folium.LayerControl().add_to(m)
    st_map = st_folium(m, width=700, height=450)
    codigo = '00'
    if st_map['last_active_drawing']:
        codigo = st_map['last_active_drawing']['properties']['codigo']
    return codigo

def display_datos_paro(df, year, quarter, sex, prov_name):
    df = df[(df['Año'] == year) & (df['Trimestre'] == quarter) & (df['Sexo'] == sex) & (df['Provincia'] == prov_name)]    
    st.metric(sex, str(df.Paro.iat[0])+' %')

st.set_page_config(APP_TITLE)
st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)

prov_geo = 'provincias.geojson'
prov_paro = 'TasaParoProvSeTr.csv'
prov_data = pd.read_csv(prov_paro, encoding='utf-8')
#Sexo	Codigo	Provincia	Trimestre	Paro
#El código de provincia en el geojson es str y con cero a la izquierda
prov_data['codigo'] = prov_data['codigo'].astype(str).str.zfill(2)

prov_list = list(prov_data['Provincia'].unique())
prov_dict = pd.Series(prov_data.Provincia.values,index=prov_data.codigo).to_dict()

sex = display_sex_filter()
year, quarter = display_time_filters(prov_data, sex)
prov_code = display_map(prov_data, year, quarter, sex)
prov_name = display_prov_filter(prov_data, '')


#Display Metrics


if (prov_code!='00'):
    prov_name = prov_dict[prov_code]

st.subheader(f'Datos de paro: {prov_name}')    

col1, col2, col3 = st.columns(3)
with col1:
    display_datos_paro(prov_data, year, quarter, 'Ambos sexos', prov_name)
with col2:
    display_datos_paro(prov_data, year, quarter, 'Hombres', prov_name)
with col3:
    display_datos_paro(prov_data, year, quarter, 'Mujeres', prov_name)
