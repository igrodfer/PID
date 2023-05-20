import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date as dt

import matplotlib

sns.color_palette("summer",as_cmap=True)

import pandas as pd
import geopandas as gpd
pd.options.display.max_columns = 25




def contains_any(nombre:str,lista):
    for ciudad in lista:
        if ciudad in nombre:
            return True
    return False

#==================================================================#
#                             PREPROCESO                           #
#==================================================================#
# Preproceso de datos geográficos de autopistas


provincias = gpd.read_file('data/lineas_limite.zip!SHP_ETRS89/recintos_provinciales_inspire_peninbal_etrs89')
provincias = provincias.to_crs(crs=3395)
provincias['latitud'] = provincias.centroid.map(lambda p: p.y)


autopistas = gpd.read_file('data/RT_Espana_PorModos.zip!RT_VIARIA_CARRETERA/rt_tramo_vial.shp')
autopistas = autopistas.to_crs("+proj=cea EPSG:4326")
autopistas = autopistas.to_crs(crs=3395)
#
autopistas = autopistas[(autopistas["claseD"] == "Autovía o autopista li") | (autopistas["claseD"] == "Autopista de peaje")]
peajes = autopistas[(autopistas["claseD"] == "Autopista de peaje")]
peajes["estadofisD"] = "Autopista de peaje"
autopistas = pd.concat([autopistas,peajes])

#===================================================================
# Preproceso de datos de transporte

transporte = pd.read_csv('data/20239.csv', sep=';')
transporte = transporte[transporte['Viajeros y tasas'] == "Viajeros transportados"]


interurbano = transporte[transporte["Tipo de transporte: Nivel 2"] == "Transporte interurbano regular"]
#
ferrocarril = interurbano[interurbano["Tipo de transporte: Nivel 3"] == "Interurbano por ferrocarril"].copy()
aereo = interurbano[interurbano["Tipo de transporte: Nivel 3"] == "Interurbano Aéreo (interior)"].copy()
autobus = interurbano[interurbano["Tipo de transporte: Nivel 3"] == "Interurbano por autobús regular"].copy()



ave = ferrocarril[ferrocarril["Tipo de transporte: Nivel 5"] == "Alta Velocidad"]
ave = ave.rename(columns={"Tipo de transporte: Nivel 1":"Modo de transporte"})
ave = ave.drop(columns=["Tipo de transporte: Nivel 2","Tipo de transporte: Nivel 3","Tipo de transporte: Nivel 4","Tipo de transporte: Nivel 5","Viajeros y tasas"])
ave = ave.sort_values(by="Periodo")
ave = ave.dropna()
ave["Total"] = ave["Total"].str.replace(".","")
ave["Total"] = ave["Total"].astype(int)
ave = ave.groupby(by="Periodo").sum().reset_index()



aereo = aereo.drop(columns=["Tipo de transporte: Nivel 2","Tipo de transporte: Nivel 3","Tipo de transporte: Nivel 4","Tipo de transporte: Nivel 5","Viajeros y tasas"])
aereo = aereo.rename(columns={"Tipo de transporte: Nivel 1":"Modo de transporte"})
#
aereo = aereo.dropna()
aereo = aereo.sort_values(by="Periodo")
aereo["Total"] = aereo["Total"].str.replace(".","")
aereo["Total"] = aereo["Total"].astype(int)
aereo = aereo.groupby("Periodo").sum().reset_index()


autobus = autobus.rename(columns={"Tipo de transporte: Nivel 1":"Modo de transporte"})
#
autobuses_tipos =['Transporte interurbano regular por autobús: Media distancia',
       'Transporte interurbano regular por autobús: Larga distancia']
autobus = autobus[autobus["Tipo de transporte: Nivel 4"].isin(autobuses_tipos)]
autobus = autobus.drop(columns=["Tipo de transporte: Nivel 2","Tipo de transporte: Nivel 3","Tipo de transporte: Nivel 4","Tipo de transporte: Nivel 5","Viajeros y tasas"])
autobus = autobus.dropna()
autobus = autobus.sort_values(by="Periodo")
autobus["Total"] = autobus["Total"].str.replace(".","")
autobus["Total"] = autobus["Total"].astype(int) 
autobus = autobus.groupby("Periodo").sum().reset_index()


autobus["Modo de transporte"] = "Autobus"
ave["Modo de transporte"] = "Alta Velocidad"
aereo["Modo de transporte"] = "Aéreo"


transporte = pd.concat([autobus,ave,aereo])
transporte["year"] = transporte["Periodo"].str[:4].astype(int)
transporte["month"] = transporte["Periodo"].str[5:].astype(int)
transporte["date"] = pd.to_datetime(dict(year=transporte.year, month=transporte.month,day=1))


#===================================================================
# Preproceso de datos turísticos

turistas = pd.read_csv("data/52047.csv",sep=";")

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

viajeros = turistas[turistas["Concepto turístico"] == "Turistas"].groupby(["year","Provincia de destino"]).sum(numeric_only=True).reset_index()
viajeros.rename(columns={"Provincia de destino":"NAMEUNIT"},inplace=True)
provincias_viajeros = provincias.merge(right=viajeros,on="NAMEUNIT")



#=======================================================
# Preproceso de datos geográficos de AVE

estaciones = gpd.read_file('RT_Espana_PorModos.zip!RT_FFCC/rt_estacionffcc_p.shp')
estaciones = estaciones.to_crs("+proj=cea EPSG:4326")
estaciones = estaciones.to_crs(crs=3395)


tramos = gpd.read_file('RT_Espana_PorModos.zip!RT_FFCC/rt_tramofc_linea.shp')
tramos = tramos.to_crs("+proj=cea EPSG:4326")

tramos = tramos.to_crs(crs=3395)
tramos.loc[tramos.nombre.str.contains('036'),"uso_ppalD"] = "Uso predominante Alta Velocidad"
tramos.loc[tramos.codigo.str.startswith('0360000'),"uso_ppalD"] = "Uso predominante Alta Velocidad"
tramos.loc[tramos.codigo.str.startswith('0440003'),"uso_ppalD"] = "Uso predominante Alta Velocidad"
tramos.loc[tramos.codigo.str.startswith('0440002'),"uso_ppalD"] = "Uso predominante Alta Velocidad"
tramos.loc[(tramos.codigo.str.contains("12C220010")),"nombre"] = "Ni idea hulio" 
tramos.loc[(tramos.codigo.str.contains("12C220010")),"uso_ppalD"] = "Otros usos" 
lineas_ave = tramos[tramos["uso_ppalD"] == "Uso predominante Alta Velocidad"].dissolve(by="nombre").reset_index()



estaciones_excluir="""Estación de Vigo-
Estación de Ourense-Empalme-contenedores
Estación de Córdoba-El Higuerón
Estación de A Coruña-San Diego-contenedores
Estación de León-Clasificación
Estación de Puertollano-Refinería
Plasencia Jalón
Plasencia de Jalón
Plasencia del Monte
Estación de Badajoz-Frontera
Cargadero de Mérida-Contenedores
Apartadero de Casar de Cáceres
Estación de Girona-Mercaderies
Estación de Zaragoza-Delicias
Estación de La Sagrera
Apeadero de la Universidad de Cádiz""".split("\n")
id_redondela_redundante = 360450000149


estaciones_ave_nombres = """Estación de Albacete
Estación de Castelló de la Plana
Estación de Alacant-Terminal
Antequera-Santa Ana
Estación de Madrid-Puerta de Atocha
Barcelona-Sants
Calatayud
Estación de Camp de Tarragona
Clara Campoamor
Estación de Ciudad Real
Estación de Córdoba
Estación de A Coruña
Estación de Cuenca Fernando Zóbel
Elche
Vilafant
Girona
Estación de Granada
Guadalajara-Yebes
Estación de León
Lleida-Pirineus
Loja
Zambrano
Estación de Medina del Campo Alta Velocidad
Murcia del Carmen
Estación de Ourense-Empalme
Orihuela
Palencia
Estación de Pontevedra
Villanueva de Córdoba
Puente Genil-Herrera
Estación de Puertollano
Redondela
Requena -Utiel
Estación de Alta Velocidad de Sanabria
Santiago de Compostela
Estación de Segovia-A.V.
Sevilla-Santa Justa
Estación de Toledo
Sorolla
Valladolid-Campo Grande
Estación de Vigo
Estación de Villena Alta Velocidad
Zamora
Zaragoza-Delicias
Estación de La Sagrera
Badajoz
Mérida
Cáceres
Estación de Plasencia
Estación de Burgos Rosa Manzano
Cádiz""".split("\n")


anotaciones_derecha = """Antequera
Vigo
Utiel
Sanabria
Murcia
Elche
Sevilla
Badajoz
Pontevedra
Córdoba
Apartadero""".split("\n")



for nombre in estaciones_ave_nombres:
    print(f"{nombre:>50}: {len(estaciones[(estaciones.nombre.str.contains(nombre))&(~estaciones.nombre.apply(lambda x:contains_any(x,estaciones_excluir)))])}")


def sanear_nombre_estacion(nombre:str):
    palabras_redundantes = """Estación de 
Estacion de 
Alta Velocidad de
Alta Velocidad
-Puerta de Atocha
Camp de 
del Carmen
- Joaquin Sorolla
Villanueva de 
Fernanado Zóbel
Miguel Hernández
-Terminal
-Santa Justa
Apartadero de 
-A.V.
E.C.
Fernando Zóbel
-Pirineus
-Campo Grande
-Sants
 Rosa Manzano""".split("\n")
    for word in palabras_redundantes:
        nombre = nombre.replace(word,"")
    
    reemplazos_totales = {"Clara Campoamor":"Zaragoza","María-Zambrano":"Málaga"}
    if nombre in reemplazos_totales:
        nombre = reemplazos_totales[nombre]
    return nombre



gfd_estaciones_ave = estaciones[(estaciones.id_estfc != id_redondela_redundante)&(estaciones.nombre.apply(lambda x:contains_any(x,estaciones_ave_nombres))& (estaciones.nombre.apply(lambda x:not contains_any(x,estaciones_excluir))))]

#==================================================================#
#                              PLOTEOS                             #
#==================================================================#
# Autpoistas y autovías en la península

fig, (ax) = plt.subplots(ncols=1,figsize=(15,15))
ax = provincias.dissolve().buffer(20000).plot(ax = ax,figsize=(15,15),alpha=0.2,color="orange")
ax = provincias.dissolve().buffer(15000).plot(ax = ax,figsize=(15,15),alpha=0.2,color="orange")
ax = provincias.dissolve().buffer(10000).plot(ax = ax,figsize=(15,15),alpha=0.4,color="orange")
ax = provincias.plot(ax = ax, figsize=(15,15),cmap="winter",column="latitud")
autopistas[autopistas.centroid.y > 4000000].plot(ax = ax,linewidth=1.5,column="estadofisD",cmap="gnuplot",legend=True)
fig.tight_layout()
plt.axis("off")
fig.suptitle("Autopistas y autovías de la península Española y Baleares",fontsize=24)
plt.show()


#===================================================================
# Número de viajeros a lo largo del tiempo

from_date = dt(2019,1,1)
fig ,ax = plt.subplots(figsize=(15,7))
sns.set_style("whitegrid")
sns.lineplot(data=transporte[transporte["date"].dt.date >= from_date], x="date", y="Total", hue="Modo de transporte",ax=ax)
fig.suptitle("Viajeros transportados por Alta Velocidad, Aéreo y Autobus", fontsize=20)
fig.savefig("results/transporte.png")
plt.show()

#===================================================================
# Turistas por región
def plot_turistas_anual(draw_year = "2020"):

    paises_agregados = ["Unión Europea (sin España)","América del Norte","Sudamérica","Centro América y Caribe"]


    turistas_year = turistas[(turistas["year"] == draw_year) & ~turistas["Países"].isin(paises_agregados)].groupby(by="Países").sum(numeric_only=True).reset_index()


    fig,(ax,ax1) = plt.subplots(figsize=(20,10),ncols=2)
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
    plt.show()

for year in ["2020","2021","2022"]:
    plot_turistas_anual(year)


#===================================================================
# Estaciones y líneas de AVE


fig, (ax1) = plt.subplots(ncols=1,figsize=(15,15))
ax = provincias.plot(ax = ax1, figsize=(15,15),cmap="summer",column="latitud")
lineas_ave.plot(ax = ax,linewidth=2,column="estadofisD",cmap="copper_r",legend=True)
gfd_estaciones_ave.plot(ax = ax)
gfd_estaciones_ave[gfd_estaciones_ave["nombre"].apply(lambda x: contains_any(x,anotaciones_derecha))].apply(lambda x: ax.annotate(text=sanear_nombre_estacion(x.nombre),
    xy=x.geometry.centroid.coords[0], ha='right',
    fontsize=14),axis=1)
gfd_estaciones_ave[gfd_estaciones_ave["nombre"].apply(lambda x: not contains_any(x,anotaciones_derecha))].apply(lambda x: ax.annotate(text=sanear_nombre_estacion(x.nombre),
    xy=x.geometry.centroid.coords[0], ha='left',
    fontsize=14),axis=1)
fig.tight_layout()
plt.axis("off")
fig.suptitle("Líneas y estaciones de Alta Velocidad Española",fontsize=24)
plt.show()

