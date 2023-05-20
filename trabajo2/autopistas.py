#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import folium
from shapely.geometry import Point
pd.options.display.max_columns = 25


# In[2]:


provincias = gpd.read_file('data/lineas_limite.zip!SHP_ETRS89/recintos_provinciales_inspire_peninbal_etrs89')
#INSPIREID', 'COUNTRY', 'NATLEV', 'NATLEVNAME', 'NATCODE', 'NAMEUNIT', 'CODNUT1', 'CODNUT2', 'CODNUT3', 'geometry'
provincias = provincias.to_crs(crs=3395)
provincias['latitud'] = provincias.centroid.map(lambda p: p.y)


# In[3]:


autopistas = gpd.read_file('data/RT_Espana_PorModos.zip!RT_VIARIA_CARRETERA/rt_tramo_vial.shp')
autopistas = autopistas.to_crs("+proj=cea EPSG:4326")
autopistas = autopistas.to_crs(crs=3395)


# In[4]:


autopistas["nombre_alt"].unique()


# In[5]:


autopistas["claseD"].unique()


# In[6]:


autopistas = autopistas[(autopistas["claseD"] == "Autovía o autopista li") | (autopistas["claseD"] == "Autopista de peaje")]
peajes = autopistas[(autopistas["claseD"] == "Autopista de peaje")]
peajes["estadofisD"] = "Autopista de peaje"

autopistas = pd.concat([autopistas,peajes])


# In[7]:


autopistas.info()


# In[8]:


def contains_any(nombre:str,lista):
    for ciudad in lista:
        if ciudad in nombre:
            return True
    return False


# In[9]:


fig, (ax) = plt.subplots(ncols=1,figsize=(15,15))
ax = provincias.dissolve().buffer(20000).plot(ax = ax,figsize=(15,15),alpha=0.2,color="orange")
ax = provincias.dissolve().buffer(15000).plot(ax = ax,figsize=(15,15),alpha=0.2,color="orange")
ax = provincias.dissolve().buffer(10000).plot(ax = ax,figsize=(15,15),alpha=0.4,color="orange")
ax = provincias.plot(ax = ax, figsize=(15,15),cmap="winter",column="latitud")
autopistas[autopistas.centroid.y > 4000000].plot(ax = ax,linewidth=1.5,column="estadofisD",cmap="gnuplot",legend=True)
fig.tight_layout()
plt.axis("off")
fig.suptitle("Autopistas y autovías de la península Española y Baleares",fontsize=24)

