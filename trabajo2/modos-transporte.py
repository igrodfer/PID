#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# In[177]:


transporte = pd.read_csv('data/20239.csv', sep=';')
transporte = transporte[transporte['Viajeros y tasas'] == "Viajeros transportados"]


# In[178]:


transporte.info()


# In[148]:


interurbano = transporte[transporte["Tipo de transporte: Nivel 2"] == "Transporte interurbano regular"]
#
ferrocarril = interurbano[interurbano["Tipo de transporte: Nivel 3"] == "Interurbano por ferrocarril"].copy()
aereo = interurbano[interurbano["Tipo de transporte: Nivel 3"] == "Interurbano Aéreo (interior)"].copy()
autobus = interurbano[interurbano["Tipo de transporte: Nivel 3"] == "Interurbano por autobús regular"].copy()


# In[149]:


ave = ferrocarril[ferrocarril["Tipo de transporte: Nivel 5"] == "Alta Velocidad"]
ave = ave.rename(columns={"Tipo de transporte: Nivel 1":"Modo de transporte"})
ave = ave.drop(columns=["Tipo de transporte: Nivel 2","Tipo de transporte: Nivel 3","Tipo de transporte: Nivel 4","Tipo de transporte: Nivel 5","Viajeros y tasas"])
ave = ave.sort_values(by="Periodo")
ave = ave.dropna()
ave["Total"] = ave["Total"].str.replace(".","")
ave["Total"] = ave["Total"].astype(int)
ave = ave.groupby(by="Periodo").sum().reset_index()


# In[150]:


aereo = aereo.drop(columns=["Tipo de transporte: Nivel 2","Tipo de transporte: Nivel 3","Tipo de transporte: Nivel 4","Tipo de transporte: Nivel 5","Viajeros y tasas"])
aereo = aereo.rename(columns={"Tipo de transporte: Nivel 1":"Modo de transporte"})

aereo = aereo.dropna()
aereo = aereo.sort_values(by="Periodo")
aereo["Total"] = aereo["Total"].str.replace(".","")
aereo["Total"] = aereo["Total"].astype(int)
aereo = aereo.groupby("Periodo").sum().reset_index()


# In[151]:


autobus = autobus.rename(columns={"Tipo de transporte: Nivel 1":"Modo de transporte"})

autobuses_tipos =['Transporte interurbano regular por autobús: Media distancia',
       'Transporte interurbano regular por autobús: Larga distancia']
autobus = autobus[autobus["Tipo de transporte: Nivel 4"].isin(autobuses_tipos)]
autobus = autobus.drop(columns=["Tipo de transporte: Nivel 2","Tipo de transporte: Nivel 3","Tipo de transporte: Nivel 4","Tipo de transporte: Nivel 5","Viajeros y tasas"])
autobus = autobus.dropna()
autobus = autobus.sort_values(by="Periodo")
autobus["Total"] = autobus["Total"].str.replace(".","")
autobus["Total"] = autobus["Total"].astype(int) 
autobus = autobus.groupby("Periodo").sum().reset_index()


# In[152]:


autobus["Modo de transporte"] = "Autobus"
ave["Modo de transporte"] = "Alta Velocidad"
aereo["Modo de transporte"] = "Aéreo"


# In[153]:


ave.info()
autobus.info()
aereo.info()


# In[163]:


transporte = pd.concat([autobus,ave,aereo])
transporte["year"] = transporte["Periodo"].str[:4].astype(int)
transporte["month"] = transporte["Periodo"].str[5:].astype(int)
transporte["date"] = pd.to_datetime(dict(year=transporte.year, month=transporte.month,day=1))


# In[164]:


transporte["date"]


# In[175]:


from datetime import date as dt
from_date = dt(2019,1,1)
fig ,ax = plt.subplots(figsize=(15,7))
sns.set_style("whitegrid")
sns.lineplot(data=transporte[transporte["date"].dt.date >= from_date], x="date", y="Total", hue="Modo de transporte",ax=ax)
fig.suptitle("Viajeros transportados por Alta Velocidad, Aéreo y Autobus", fontsize=20)
fig.savefig("results/transporte.png")

