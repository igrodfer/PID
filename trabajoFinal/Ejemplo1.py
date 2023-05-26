# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 13:33:48 2022

@author: jlluch
"""

import pandas as pd
import streamlit as st
import numpy as np
import time

st.set_page_config(layout="wide")

df = pd.read_csv('data/CovidCVMes21.csv')

izq, der = st.columns(2)
izq.write(df)
izq.dataframe(df.style.highlight_max(axis=0))
izq.table(df)
izq.line_chart(df.Casos)
izq.bar_chart(df.UCI) 

np.random.seed(4)
mapa = pd.DataFrame(np.random.randn(1000, 2) / [50, 50] + [39.4697, -0.37739],columns=['lat', 'lon']) 
st.map(mapa)

with der:
    x = st.slider('x')
    st.write(x, 'al cuadrado es ', x * x)
    
    st.text_input("Dime tu nombre:", key="nombre")
    st.write ('Tu nombre es:', st.session_state.nombre)

if st.sidebar.checkbox('DataFrame Visible'):
    st.sidebar.table(df)

opcion = st.sidebar.selectbox('¿Cuál es tu número favorito?',[1, 2, 3, 4, 5, 6, 7, 8, 9])
st.sidebar.write ('Tu número favorito: ', opcion)

st.write('Iniciando proceso...')

# Espacio vacío
iteracion = st.empty()
bar = st.progress(0)

for i in range(100):
  # actualiza el progreso en cada iteración
  iteracion.text(f'Iteracion {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

st.write ('...Finalizado')