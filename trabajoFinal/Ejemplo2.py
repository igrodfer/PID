# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 10:12:54 2022

@author: jlluch
"""
import streamlit as st

st.set_page_config(
    page_title="streamlit-folium documentation",
    page_icon=":world_map:️",
    layout="wide",
)

left, right = st.columns(2)

with left:
    with st.echo():

        import folium
        import streamlit as st

        from streamlit_folium import st_folium

        m = folium.Map(location=[39.468, -0.377], zoom_start=12, tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", attr='Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012')
        folium.Marker(
            [39.468, -0.377], popup="Valencia", tooltip="Valencia"
        ).add_to(m) 

        st_data = st_folium(m, width=725)

with right:
    """
    El resultado de `st_folium` se almacena en la variable `st_data`, 
    que contiene la información acerca de lo que se visualiza en la ventana:
    """

    st_data

    """
    Cada vez que el usuario interactúa con el mapa los valores de 'bounds', 'center' y 'zoom' se actualizan.
    Con estos valores podemos limitar los datos a mostrar en la parte visible, cambiar el tamaño de las marcas
    en función del zoom, etc.
    """