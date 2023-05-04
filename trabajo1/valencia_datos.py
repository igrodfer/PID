#!/usr/bin/env python
# coding: utf-8


# In[261]:


import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import holidays
import matplotlib.dates as mdates
import scipy
sns.set_theme()
sns.set_style("ticks")
semana=["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"]


# In[295]:


_df = pd.read_csv("data.csv",delimiter=";")

# Limpiar malas lecturas
_df = _df[_df["Temperatura"] < 45]
_df = _df[_df["Precipitacion"] < 300]

# Columnas temporales
_df["Hora"] = _df["Hora"].apply(lambda x : x[11:16])
_df["time"] = _df["Fecha"] + "T" +_df["Hora"]
_df["time"] = pd.to_datetime(_df["time"])
_df["Month"] = _df["time"].dt.month
_df.drop(columns=["Fecha baja","Fecha creacion"],inplace=True)

_df.set_index("time",inplace=True)
_df.sort_index(inplace=True)


# In[299]:

# Fin de semana
_df["Dia de la semana numerico"] = _df.index.to_series().dt.weekday
_df["weekend"] = _df["Dia de la semana numerico"] >= 5

# Festivos
es_holidays = holidays.ES()
_df["holidays"] = _df["Fecha"].apply(lambda x : x in es_holidays)
_df["weekend or holidays"] = _df["weekend"] | _df["holidays"]

# Hora en formato datetime
_df["timedelta"] = pd.to_datetime(_df["Hora"])

# Estación por mes
season_map = {1:"Invierno",
              2:"Invierno",
              12:"Invierno",
              3:"Primavera",
              4:"Primavera",
              5:"Primavera",
              6:"Verano",
              7:"Verano",
              8:"Verano",
              9:"Otoño",
              10:"Otoño",
              11:"Otoño",}
_df["Season"] = _df["Month"].map(season_map)


# In[300]:

# Barplot: Óxidos de nitŕogeno 
fig, (ax,ax1,ax2) = plt.subplots(figsize=(12,6),ncols=3)
fig.tight_layout()
sns.barplot(_df,x="weekend",y="NO",ax=ax)
sns.barplot(_df,x="weekend",y="NO2",ax=ax1)
sns.barplot(_df,x="weekend",y="NOx",ax=ax2)
plt.show()


# In[238]:

# Boxplot: Óxidos de nitrógeno en las diferentes estaciones
fig, (ax,ax1,ax2) = plt.subplots(figsize=(12,10),nrows=3)
sns.boxplot(_df,y="NO",x="Season",ax=ax,showfliers=False)
sns.boxplot(_df,y="NO2",x="Season",ax=ax1,showfliers=False)
sns.boxplot(_df,y="NOx",x="Season",ax=ax2,showfliers=False)
plt.show()


# In[319]:
# Violinplot: Hidrocarburos y amoníaco en las diferentes estaciones
fig, (ax,ax1,ax2) = plt.subplots(figsize=(12,10),nrows=3)
sns.violinplot(_df[_df["NH3"] < 10],y="NH3",x="Season",ax=ax,showfliers=False,hue="weekend or holidays",split=True)
sns.violinplot(_df[_df["C7H8"] < 8],y="C7H8",x="Season",ax=ax1,showfliers=False,hue="weekend or holidays",split=True)
sns.violinplot(_df[_df["C6H6"] < 2.5],y="C6H6",x="Season",ax=ax2,showfliers=False,hue="weekend or holidays",split=True)
plt.show()


# In[240]:

# Lineplot: Óxidos de nitrógeno a lo largo del día
fig, (ax,ax1,ax2) = plt.subplots(figsize=(12,10),nrows=3)
sns.lineplot(_df.reset_index(),x="timedelta",y="NO",ax=ax,hue="weekend or holidays")
sns.lineplot(_df.reset_index(),x="timedelta",y="NO2",ax=ax1,hue="weekend or holidays")
sns.lineplot(_df.reset_index(),x="timedelta",y="NOx",ax=ax2,hue="weekend or holidays")

ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
ax2.xaxis.set_major_locator(mdates.HourLocator(interval=2))
# set formatter
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.show()


# In[241]:

# Lineplot: Ozono, moóxido y óxido de azufre a lo largo del día
fig, (ax,ax1,ax2) = plt.subplots(figsize=(12,10),nrows=3)
sns.lineplot(_df.reset_index(),x="timedelta",y="O3",ax=ax,hue="weekend or holidays")
sns.lineplot(_df.reset_index(),x="timedelta",y="CO",ax=ax1,hue="weekend or holidays")
sns.lineplot(_df.reset_index(),x="timedelta",y="SO2",ax=ax2,hue="weekend or holidays")

ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
ax2.xaxis.set_major_locator(mdates.HourLocator(interval=2))
# set formatter
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.show()


# Lineplot: Micropartículas a lo largo del día
fig, (ax,ax1,ax2) = plt.subplots(figsize=(12,10),nrows=3)
sns.lineplot(_df.reset_index(),x="timedelta",y="PM1",ax=ax,hue="weekend or holidays")
sns.lineplot(_df.reset_index(),x="timedelta",y="PM2.5",ax=ax1,hue="weekend or holidays")
sns.lineplot(_df.reset_index(),x="timedelta",y="PM10",ax=ax2,hue="weekend or holidays")

ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))
ax2.xaxis.set_major_locator(mdates.HourLocator(interval=2))
# set formatter
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.show()


# In[272]:

# Histplot: Ozono en las diferentes estaciones
sns.histplot(_df.reset_index(),x="O3",bins=20,hue="Season",kde=True,multiple="layer")


# In[303]:


g = sns.PairGrid(_df[_df["NO"] < 25].reset_index(), vars=["NO","Temperatura"],hue="Season")
g.map_diag(sns.kdeplot)
g.map_offdiag(sns.kdeplot)
g.add_legend()


# In[329]:


g = sns.PairGrid(_df[_df["NH3"] < 11].reset_index(), vars=["NO","NO2","NOx"],hue="Season")
g.map_diag(sns.kdeplot)
g.map_offdiag(sns.regplot)
g.add_legend()

# In[ ]:


fig, ax = plt.subplots()

sns.lineplot(_df.reset_index(),y="Temperatura",x="timedelta",ax = ax,hue="Season")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))


# In[331]:


fig, ax = plt.subplots()

sns.lineplot(_df.reset_index(),y="Radiacion",x="timedelta",ax = ax,hue="Season")
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))

