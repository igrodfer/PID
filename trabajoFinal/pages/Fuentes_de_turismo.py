import streamlit as st
import pandas as pd
import folium
import geopandas as gpd
from streamlit_folium import st_folium
from Turismo_por_provincia import load_turism_data
import countrywrangler as cw
from streamlit_echarts import st_echarts

@st.cache_data
def load_geojson():
    gdf = gpd.read_file("https://gisco-services.ec.europa.eu/distribution/v2/countries/geojson/CNTR_RG_60M_2020_4326.geojson")
    return gdf

@st.cache_data
def load_fuentes_turismo()-> pd.DataFrame:
    df_turismo = load_turism_data()

    turismo_por_pais = df_turismo.dropna(subset=["Continentes","Países"])
    name_mappings = [(name,cw.Normalize.name_to_alpha2(name)) for name in turismo_por_pais["Países"].unique()]

    name_mappings_dict = dict()

    for name,code in name_mappings:
        name_mappings_dict[name] = code
    name_mappings_dict["República Eslovaca"] = "SK"
    name_mappings_dict["Macedonia"] = "MK"
    name_mappings_dict["Rumanía"] = "RO"
    name_mappings_dict["Estados Unidos de América"] = "US"
    name_mappings_dict["Arabia Saudí"] = "SA"
    name_mappings_dict["Bahréin"] = "BH"
    name_mappings_dict["Corea"] = "KR"
    name_mappings_dict["Reino Unido"] = "UK"
    name_mappings_dict["Grecia"] = "EL"
    name_mappings_dict["España"] = "ES"
    name_mappings_dict["Palestina. Estado Observador, no miembro de Naciones Unidas"] = "PS"

    turismo_por_pais["country_code_2"] = turismo_por_pais["Países"].map(name_mappings_dict)
    turismo_por_pais = turismo_por_pais.dropna()
    return turismo_por_pais


APP_TITLE = 'Fuentes del turismo'
APP_SUB_TITLE = 'Fuente: Ine'


def filter_turismo_df(df:pd.DataFrame,provincia,con_turistico,periodo)-> pd.DataFrame:

    if provincia:
        match_provincia = df["provincia"] == provincia
    else:
        match_provincia = df["provincia"].all()

    match_concepto = df["Concepto turístico"] == con_turistico
    if periodo:
        match_periodo = df["Periodo"] == periodo
    else:
        match_periodo = df["Periodo"].all()

    df = df[match_concepto & match_periodo & match_provincia]    

    return df

def display_turismo_map(df:pd.DataFrame):
    df = df[df["Provincia de destino"] != "Total Nacional"]
    colors = ["YlGn","BuGn", "BuPu","GnBu", 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'RdPu', 'YlGnBu', 'YlOrBr']

    m = folium.Map(location=[40.42,  -3.7], zoom_start=2,max_zoom=5,min_zoom=1,max_bounds=True)
    coropletas = folium.Choropleth(
        nan_fill_color="red",
        nan_fill_opacity=0,
        geo_data=prov_geo,
        name="choropleth",
        data=df,
        columns=["country_code_2", "Total"],
        key_on="properties.FID", 
        fill_color=colors[9],
        fill_opacity=0.7,
        line_opacity=1.0
    )
    coropletas.add_to(m)

    # for feature in coropletas.geojson.data['features']:
    #    code = feature['properties']['FID']
    #    feature['properties']['country_code_2'] = prov_dict[code]
    # coropletas.geojson.add_child(folium.features.GeoJsonTooltip(['country_code_2'], labels=False))

    folium.LayerControl().add_to(m)
    st_map = st_folium(m, width=700, height=450)
    codigo = '00'
    provincia = "Todas"
    if st_map['last_active_drawing']:
        codigo = st_map['last_active_drawing']['properties']['FID']
        provincia = st_map['last_active_drawing']['properties']['CNTR_NAME']
    return codigo, provincia


def show_table(df,continente,pais,con_turistico,periodo):
    match_continente = df["Continentes"] == continente
    match_pais = df["Países"] == pais
    match_concepto = df["Concepto turístico"] == con_turistico
    match_periodo = df["Periodo"] == periodo

    st.table(df[match_concepto & match_continente & match_periodo & match_pais])

# def display_metrica_nacional(df_turismo,)



st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)

prov_geo = 'https://gisco-services.ec.europa.eu/distribution/v2/countries/geojson/CNTR_RG_60M_2020_4326.geojson'
prov_paro = 'data/TasaParoProvSeTr.csv'
prov_data = pd.read_csv(prov_paro, encoding='utf-8')

prov_data['codigo'] = prov_data['codigo'].astype(str).str.zfill(2)

prov_list = list(prov_data['Provincia'].unique())
prov_dict = pd.Series(prov_data.Provincia.values,index=prov_data.codigo).to_dict()
#Display Metrics

df_turistmo = load_fuentes_turismo()

provincia = st.selectbox('Provincia',["Todos"] + df_turistmo["provincia"].dropna().unique().tolist())

if provincia == "Todos":
    provincia = None

concepto = st.selectbox('Concepto turístico', df_turistmo["Concepto turístico"].dropna().unique())
periodo = st.selectbox('Periodo', df_turistmo["Periodo"].dropna().unique())


df_filtered = filter_turismo_df(df_turistmo,provincia,concepto,periodo)

st.metric("Total Global (" + concepto+")",int(df_filtered["Total"].sum()))

izq, der = st.columns(2)

code, pais_seleccionado = display_turismo_map(df_filtered)
# st.write(code,pais_seleccionado)
# if code != "00":
#     st.subheader(provincia_seleccionada)
#     df_vis = filter_turismo_df(df_turistmo,continente,pais,concepto,None)
#     st.line_chart(df_vis[df_vis["codigo"] == code].set_index("fecha").Total)

#     # show_table(df_turistmo,continente,pais,concepto,periodo)

pie_data = df_filtered[["Continentes","Total"]]
pie_data = pie_data.rename(columns={"Continentes":"name","Total":"value"}).groupby("name").sum().reset_index()

options = {
    "tooltip": {"trigger": "item"},
    "legend": {"top": "5%", "left": "center"},
    "series": [
        {
            "name": "Distribución por Continente",
            "type": "pie",
            "radius": ["40%", "70%"],
            "avoidLabelOverlap": False,
            "itemStyle": {
                "borderRadius": 10,
                "borderColor": "#fff",
                "borderWidth": 2,
            },
            "label": {"show": False, "position": "center"},
            "emphasis": {
                "label": {"show": True, "fontSize": "40", "fontWeight": "bold"}
            },
            "labelLine": {"show": False},
            "data": pie_data.to_dict(orient="records")
        }
    ],
}

st_echarts(
    options=options, height="500px",
)