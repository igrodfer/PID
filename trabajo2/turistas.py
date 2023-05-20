#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.geometry import Point
pd.options.display.max_columns = 25
sns.color_palette("summer",as_cmap=True)


# In[2]:


turistas = pd.read_csv("data/52047.csv",sep=";")
turistas["Concepto turístico"].unique()


# In[3]:


turistas["Periodo"].unique()


# In[4]:


turistas = pd.read_csv("data/52047.csv",sep=";")
turistas["year"] = turistas["Periodo"].apply(lambda x: x[:4])
turistas["Total"] = turistas["Total"].str.replace(".","")
turistas["Total"] = turistas["Total"].str.replace(",",".")
turistas["Total"] = turistas["Total"].str.replace(r'^\s*$', "0", regex=True)
turistas["Total"] = turistas.Total.fillna(0).astype(float)

name_fix = {"Alicante/Alacant":"Alacant/Alicante",
            "Balears, Illes":"Illes Balears",
            "Castellón/Castelló":"Castelló/Castellón",
            "Coruña, A":"A Coruña",
            "Rioja, La":"La Rioja",
            "Valencia/València":"València/Valencia"}
turistas["Provincia de destino"] = turistas["Provincia de destino"].apply(lambda x: name_fix[x] if x in name_fix else x)


# In[5]:


turistas.head()


# In[6]:


viajeros = turistas[turistas["Concepto turístico"] == "Turistas"].groupby(["year","Provincia de destino"]).sum(numeric_only=True).reset_index()
viajeros.rename(columns={"Provincia de destino":"NAMEUNIT"},inplace=True)


# In[7]:


viajeros.head()


# In[8]:


provincias = gpd.read_file('data/lineas_limite.zip!SHP_ETRS89/recintos_provinciales_inspire_peninbal_etrs89')
#INSPIREID', 'COUNTRY', 'NATLEV', 'NATLEVNAME', 'NATCODE', 'NAMEUNIT', 'CODNUT1', 'CODNUT2', 'CODNUT3', 'geometry'
provincias = provincias.to_crs("+proj=cea EPSG:2062")
provincias['area'] = round(provincias.area/1000000,0)
provincias['latitud'] = provincias.centroid.map(lambda p: p.y)
#Mapa de coropletas: mapa temÃ¡tico con las Ã¡reas sombreadas de diferentes colores en funciÃ³n del valor de una columna
provincias = provincias.to_crs(crs=3395)
#LÃ­mites de las provincias


# In[9]:


provincias.info()


# In[10]:


provincias_viajeros = provincias.merge(right=viajeros,on="NAMEUNIT")


# In[11]:


provincias_viajeros.info()


# In[28]:


fig,(ax,ax1) = plt.subplots(figsize=(20,10),ncols=2)
draw_year = "2020"
paises_agregados = ["Unión Europea (sin España)","América del Norte","Sudamérica","Centro América y Caribe"]
turistas_year = turistas[(turistas["year"] == draw_year) & ~turistas["Países"].isin(paises_agregados)].groupby(by="Países").sum(numeric_only=True).reset_index()


df_plot = provincias_viajeros[(provincias_viajeros["year"] == draw_year)& ~turistas["Países"].isin(paises_agregados)]
ax = df_plot.dissolve().buffer(20000).plot(ax = ax,figsize=(15,15),alpha=0.2)
ax = df_plot.dissolve().buffer(15000).plot(ax = ax,figsize=(15,15),alpha=0.2)
ax = df_plot.dissolve().buffer(10000).plot(ax = ax,figsize=(15,15),alpha=0.4)
df_plot.plot(
    ax = ax,
    column="Total",
    legend=True,
    cmap="summer",
    norm=matplotlib.colors.LogNorm(
        vmin=df_plot.Total.min(), 
        vmax=df_plot.Total.max()
    ), 
    legend_kwds={'location': 'top'}

)
df_plot.apply(
    lambda x: ax.annotate(
        text=round(x.Total / 1_000_000,2),
        xy=x.geometry.centroid.coords[0], 
        ha='center',
        fontsize=10
    ),
    axis=1
)


ax.axis("off")
#sns.set_theme()
with sns.axes_style("darkgrid"):
    ax1 = sns.barplot(data=turistas_year.nlargest(10,"Total"),x="Total",ax=ax1,y="Países",palette="summer_r")
sns.despine(left=True)
fig.suptitle(f"Turistas por provincia y por procedencia en {draw_year}",fontsize=24)
fig.tight_layout()

