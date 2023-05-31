import streamlit as st
import pandas as pd
import folium
import geopandas as gpd
from streamlit_folium import st_folium


@st.cache_data
def load_turism_data()-> pd.DataFrame:
    #===================================================================
    # Preproceso de datos turísticos


    turistas = pd.read_csv("trabajoFinal/data/52047.csv",sep=";")
    turistas["year"] = turistas["Periodo"].apply(lambda x: x[:4])
    turistas["Total"] = turistas["Total"].str.replace(".","")
    turistas["Total"] = turistas["Total"].str.replace(",",".")
    turistas["Total"] = turistas["Total"].str.replace(r'^\s*$', "0", regex=True)
    turistas["Total"] = turistas.Total.fillna(0).astype(float)

    turistas["month"] = turistas["Periodo"].apply(lambda x: x[5:])
    turistas["day"] = 1
    turistas["fecha"] = pd.to_datetime(turistas[["month","year","day"]])
    name_fix = {"Alicante/Alacant":"Alacant",
                "Balears, Illes":"Illes Balears",
                "Castellón/Castelló":"Castelló",
                "Coruña, A":"A Coruña",
                "Rioja, La":"La Rioja",
                "Valencia/València":"València",
                "Gipuzkoa":"Gipuzcoa",
                "Araba/Álava":"Araba",
                "Palmas, Las":"Las Palmas"}
    turistas["Provincia de destino"] = turistas["Provincia de destino"].apply(lambda x: name_fix[x] if x in name_fix else x)
    turistas.drop(columns="RESIDENCIA/ORIGEN",inplace=True)

    prov_geo = 'trabajoFinal/data/provincias.geojson'
    provs = gpd.read_file(prov_geo)
    turistas = turistas.merge(right=provs[["codigo","provincia"]],right_on="provincia",left_on="Provincia de destino",how="left")
    turistas.codigo.fillna("00",inplace=True)
    # viajeros = turistas[turistas["Concepto turístico"] == "Turistas"].groupby(["year","Provincia de destino"]).sum(numeric_only=True).reset_index()
    # viajeros.rename(columns={"Provincia de destino":"NAMEUNIT"},inplace=True)
    # provincias_viajeros = provincias.merge(right=viajeros,on="NAMEUNIT")
    return turistas




APP_TITLE = 'Turismo por provincia'
APP_SUB_TITLE = 'Fuente: Ine'


def filter_turismo_df(df:pd.DataFrame,continente,pais,con_turistico,periodo)-> pd.DataFrame:
    if continente is not None:
        match_continente = df["Continentes"] == continente
    else:
        match_continente = df["Continentes"].isna()

    if pais is not None:
        match_pais = df["Países"] == pais
    else:
        match_pais = df["Países"].isna()

    match_concepto = df["Concepto turístico"] == con_turistico
    if periodo:
        match_periodo = df["Periodo"] == periodo
    else:
        match_periodo = df["Periodo"].all()

    df = df[match_concepto & match_continente & match_periodo & match_pais]    

    return df

def display_turismo_map(df,tipo="Turistas",color="YlGn"):
    df = df[df["Provincia de destino"] != "Total Nacional"]

    m = folium.Map(location=[40.42,  -3.7], zoom_start=5,max_zoom=7,min_zoom=5,max_bounds=True,max_lat=50,min_lat=20,max_lon=10,min_lon=-20)
    coropletas = folium.Choropleth(
        geo_data=prov_geo,
        name="choropleth",
        data=df,
        columns=["codigo", "Total"],
        key_on="properties.codigo", 
        fill_color=color,
        fill_opacity=0.7,
        line_opacity=1.0,
        legend_name=tipo
    )
    coropletas.add_to(m)

    for feature in coropletas.geojson.data['features']:
       code = feature['properties']['codigo']
       feature['properties']['Provincia'] = prov_dict[code]
       feature["properties"]["texto"] = df[df["codigo"]==code]["Total"].tolist()[0]
    coropletas.geojson.add_child(folium.features.GeoJsonTooltip(['Provincia',"texto"], labels=False))

    folium.LayerControl().add_to(m)
    st_map = st_folium(m, width=700, height=450)
    codigo = '00'
    provincia = "Todas"
    if st_map['last_active_drawing']:
        codigo = st_map['last_active_drawing']['properties']['codigo']
        provincia = st_map['last_active_drawing']['properties']['provincia']
    return codigo, provincia


def show_table(df,continente,pais,con_turistico,periodo):
    match_continente = df["Continentes"] == continente
    match_pais = df["Países"] == pais
    match_concepto = df["Concepto turístico"] == con_turistico
    match_periodo = df["Periodo"] == periodo

    st.table(df[match_concepto & match_continente & match_periodo & match_pais])

# def display_metrica_nacional(df_turismo,)


st.set_page_config(APP_TITLE,menu_items={
    #'Get Help': 'https://www.extremelycoolapp.com/help',
    #'Report a bug': "https://www.extremelycoolapp.com/bug",
    #'About': "# This is a header. This is an *extremely* cool app!"
})

st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)

prov_geo = 'trabajoFinal/data/provincias.geojson'
prov_paro = 'trabajoFinal/data/TasaParoProvSeTr.csv'
prov_data = pd.read_csv(prov_paro, encoding='utf-8')

prov_data['codigo'] = prov_data['codigo'].astype(str).str.zfill(2)

prov_list = list(prov_data['Provincia'].unique())
prov_dict = pd.Series(prov_data.Provincia.values,index=prov_data.codigo).to_dict()
#Display Metrics

pais = None
df_turistmo = load_turism_data()

continente = st.selectbox('Continentes',["Todos"]+df_turistmo["Continentes"].dropna().unique().tolist())
    
if continente == "Todos":
    continente = None
else:
    turismo_continente = df_turistmo[df_turistmo["Continentes"] == continente]
    pais = st.selectbox('País',["Todos"] + df_turistmo[(df_turistmo["Continentes"] == continente)]["Países"].dropna().unique().tolist())

if pais == "Todos":
    pais = None

conceptos_list = df_turistmo["Concepto turístico"].dropna().unique().tolist()
concepto = st.selectbox('Concepto turístico', conceptos_list)

color_list = ["YlGn","BuGn", "BuPu","GnBu", 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'RdPu', 'YlGnBu', 'YlOrBr']
color_i = conceptos_list.index(concepto)
if color_i < len(color_list):
    color = color_list[color_i]
else:
    color = color_list[0]
periodo = st.selectbox('Periodo', df_turistmo["Periodo"].dropna().unique())


df_filtered = filter_turismo_df(df_turistmo,continente,pais,concepto,periodo)

st.metric("Total Nacional (" + concepto+")",int(df_filtered[df_filtered["Provincia de destino"] == "Total Nacional"]["Total"].values[0]))
code, provincia_seleccionada = display_turismo_map(df_filtered,tipo=concepto,color=color)

if code != "00":
    st.subheader(provincia_seleccionada)
    df_vis = filter_turismo_df(df_turistmo,continente,pais,concepto,None)
    st.line_chart(df_vis[df_vis["codigo"] == code].set_index("fecha").Total)

    # show_table(df_turistmo,continente,pais,concepto,periodo)
