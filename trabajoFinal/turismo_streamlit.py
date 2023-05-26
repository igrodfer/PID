import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium


@st.cache_data
def load_turism_data()-> pd.DataFrame:
    #===================================================================
    # Preproceso de datos turísticos


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
    turistas.drop(columns="RESIDENCIA/ORIGEN",inplace=True)

    provs = turistas["Provincia de destino"].unique().tolist()
    p_list = list(zip(provs,range(len(provs))))
    p_map = dict()
    for p,i in p_list:
        p_map[p] = i
    turistas["codigo"] = turistas["Provincia de destino"].map(p_map)
    # viajeros = turistas[turistas["Concepto turístico"] == "Turistas"].groupby(["year","Provincia de destino"]).sum(numeric_only=True).reset_index()
    # viajeros.rename(columns={"Provincia de destino":"NAMEUNIT"},inplace=True)
    # provincias_viajeros = provincias.merge(right=viajeros,on="NAMEUNIT")
    return turistas




APP_TITLE = 'Turismo por provincia'
APP_SUB_TITLE = 'Fuente: Ine'

def display_time_filters(df, sex):
    year_list = list(df['Año'].unique())
    year_list.sort(reverse = True )
    year = st.selectbox('Año', year_list, 0)
    if year == 2023:
        quarter = st.radio('Trimestre', [1])
    else:
        quarter = st.radio('Trimestre', [1, 2, 3, 4])
    st.header(f'{year} T{quarter} - {sex}' )
    return year, quarter

def display_prov_filter(df, prov):
    
    return st.selectbox('Provincia', prov_list)

def display_sex_filter():
    return st.radio('Sexo', ['Ambos sexos', 'Hombres', 'Mujeres'])


def display_map(df, year, quarter, sex):
    df = df[(df['Año'] == year) & (df['Trimestre'] == quarter) & (df['Sexo'] == sex)]

    m = folium.Map(location=[40.42,  -3.7], zoom_start=5)
    coropletas = folium.Choropleth(geo_data=prov_geo,name="choropleth",data=df,columns=["codigo", "Paro"],key_on="properties.codigo", fill_color="YlGn",fill_opacity=0.7,line_opacity=1.0,legend_name="Tasa de Paro (%)")
    coropletas.add_to(m)
    for feature in coropletas.geojson.data['features']:
       code = feature['properties']['codigo']
       feature['properties']['Provincia'] = prov_dict[code]
    coropletas.geojson.add_child(folium.features.GeoJsonTooltip(['Provincia'], labels=False))
    
    folium.LayerControl().add_to(m)
    st_map = st_folium(m, width=700, height=450)
    codigo = '00'
    if st_map['last_active_drawing']:
        codigo = st_map['last_active_drawing']['properties']['codigo']
    return codigo

def display_turismo_map(df,continente,pais,con_turistico,periodo,total_nacional:bool):
    match_continente = df["Continentes"] == continente
    match_pais = df["Países"] == pais
    match_concepto = df["Concepto turístico"] == con_turistico
    match_periodo = df["Periodo"] == periodo

    match_nacional = df["Provincia de destino"] == "Total Nacional"
    if not total_nacional:
       match_nacional = ~match_nacional

    df = df[match_concepto & match_continente & match_periodo & match_pais & match_nacional]
    m = folium.Map(location=[40.42,  -3.7], zoom_start=5)
    coropletas = folium.Choropleth(geo_data=prov_geo,name="choropleth",data=df,columns=["codigo", "Total"],key_on="properties.codigo", fill_color="YlGn",fill_opacity=0.7,line_opacity=1.0,legend_name="Turistas")
    coropletas.add_to(m)

    for feature in coropletas.geojson.data['features']:
       code = feature['properties']['codigo']
       feature['properties']['Provincia'] = prov_dict[code]
    coropletas.geojson.add_child(folium.features.GeoJsonTooltip(['Provincia'], labels=False))

    folium.LayerControl().add_to(m)
    st_map = st_folium(m, width=700, height=450)
    codigo = '00'
    if st_map['last_active_drawing']:
        codigo = st_map['last_active_drawing']['properties']['codigo']
    return codigo

def display_datos_paro(df, year, quarter, sex, prov_name):
    df = df[(df['Año'] == year) & (df['Trimestre'] == quarter) & (df['Sexo'] == sex) & (df['Provincia'] == prov_name)]    
    st.metric(sex, str(df.Paro.iat[0])+' %')

def show_table(df,continente,pais,con_turistico,periodo):
    match_continente = df["Continentes"] == continente
    match_pais = df["Países"] == pais
    match_concepto = df["Concepto turístico"] == con_turistico
    match_periodo = df["Periodo"] == periodo

    st.table(df[match_concepto & match_continente & match_periodo & match_pais])



st.set_page_config(APP_TITLE)
st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)

prov_geo = 'data/provincias.geojson'
prov_paro = 'data/TasaParoProvSeTr.csv'
prov_data = pd.read_csv(prov_paro, encoding='utf-8')

prov_data['codigo'] = prov_data['codigo'].astype(str).str.zfill(2)

prov_list = list(prov_data['Provincia'].unique())
prov_dict = pd.Series(prov_data.Provincia.values,index=prov_data.codigo).to_dict()

prov_dict
sex = "Hombres"
year, quarter = display_time_filters(prov_data, sex)
prov_code = display_map(prov_data, year, quarter, sex)


#Display Metrics

df_turistmo = load_turism_data()
provincia_nacional = st.radio('Por provincia o Total Nacional', ['Por provincia',"Total Nacional"])
continente = st.selectbox('Continentes', df_turistmo["Continentes"].unique().tolist())
turismo_continente = df_turistmo[df_turistmo["Continentes"] == continente]
pais = st.selectbox('País', df_turistmo[df_turistmo["Continentes"] == continente]["Países"].unique().tolist())
concepto = st.selectbox('Concepto turístico', df_turistmo["Concepto turístico"].unique().tolist())
periodo = st.selectbox('Periodo', df_turistmo["Periodo"].unique().tolist())

display_turismo_map(df_turistmo,continente,pais,concepto,periodo,provincia_nacional=="Total Nacional")
show_table(df_turistmo,continente,pais,concepto,periodo)
