# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 13:49:21 2023

@author: jlluch
"""

import pandas as pd
import geopandas as gpd
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


pd.options.display.max_columns = 25

#Calcular el Ã¡rea de las provincias, primero hay que proyectar
provincias = gpd.read_file('trabajo2/lineas_limite.zip!SHP_ETRS89/recintos_provinciales_inspire_peninbal_etrs89')
#INSPIREID', 'COUNTRY', 'NATLEV', 'NATLEVNAME', 'NATCODE', 'NAMEUNIT', 'CODNUT1', 'CODNUT2', 'CODNUT3', 'geometry'
provincias = provincias.to_crs("+proj=cea EPSG:2062")
provincias['area'] = round(provincias.area/1000000,0)

#Mapa de coropletas: mapa temÃ¡tico con las Ã¡reas sombreadas de diferentes colores en funciÃ³n del valor de una columna
provincias = provincias.to_crs(crs=3395)
#LÃ­mites de las provincias
provincias.boundary.plot()
#Diferentes ColorMaps
provincias.plot(cmap='Set2', figsize=(15, 15))
provincias.plot(cmap='inferno', figsize=(15, 15), column='area')
#Con leyenda
provincias.plot(cmap='inferno', figsize=(12, 12), column='area', legend=True)
#Con leyenda ajustada al mapa
fig, axis = plt.subplots(1, 1)
divider = make_axes_locatable(axis)
cax = divider.append_axes("right", size="5%", pad=0.1)
provincias.plot(ax = axis, cmap='inferno', column='area', legend=True, cax=cax)
#Leyenda en la parte inferior y eliminar ejes
fig, axis = plt.subplots(1, 1)
axis.set_axis_off()
divider = make_axes_locatable(axis)
cax = divider.append_axes("bottom", size="5%", pad=0.1)
provincias.plot(ax = axis, cmap='inferno', column='area', legend=True, cax=cax, legend_kwds={'label': "Ãrea provincial km2",'orientation': "horizontal"})
#Esquemas percentiles
provincias.plot(cmap='OrRd', figsize=(12, 12), column='area', scheme='percentiles')

#Esquemas cuantiles
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
print(world)
world = world[(world.pop_est>0) & (world.name!="Antarctica")].copy()
world['gdp_per_cap'] = world.gdp_md_est / world.pop_est
world.plot(column='gdp_per_cap', cmap='OrRd', scheme='quantiles')

#Rellenar datos que faltan
world.loc[np.random.choice(world.index, 40), 'pop_est'] = np.nan
world.plot(column="pop_est",legend=True,scheme="quantiles",figsize=(15, 10),
           missing_kwds={"color": "lightgrey","edgecolor": "red","hatch": "///","label": "Missing values"})



