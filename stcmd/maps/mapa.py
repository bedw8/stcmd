import pandas as pd
import geopandas as gpd
import streamlit as st
import copy
import folium 
import shapely
from pathlib import Path
from streamlit_folium import folium_static
from pandas.api.types import is_string_dtype
from dataclasses import dataclass

@dataclass
class Mapa():
    df_path: str
    region_col: str = 'GLOSA_REGION'
    comuna_col: str = 'GLOSA_COMUNA'
    upm_col: str = 'cod_upm' 
    lat_col: str = 'latitud'
    long_col: str = 'longitud'
    cod_visita_col: str = 'cod_visita'

    def __post_init__(self):
        self.df = copy.deepcopy(self.load_data(Path(self.df_path)))

    @st.cache()
    def load_data(self,path: Path):
        if path.suffix in ['.xlsx','.xls']:
            df = pd.read_excel(path)
        if path.suffix == '.dta':
            df = pd.read_stata(path,convert_categorical=False)
        
        df[[self.lat_col,self.long_col]] = df[[self.lat_col,self.long_col]].apply(lambda c: c.str.replace(',','.') if is_string_dtype(c.dtype) else c).astype(float)
        df[[self.region_col,self.comuna_col]] = df[[self.region_col,self.comuna_col]].apply(lambda c:c.str.upper())

        return df

    def create_filter(self,selector_name,check=True):
        def filter_df(df): 
            selection = st.selectbox(selector_name,options=pd.Series(df[selector_col].unique()).sort_values(ignore_index=True))
            bool_series = df[selector_col] == selection
            df.query('@bool_series',inplace=True)

        selector_colnames_dict = {'Region':self.region_col,'Comuna':self.comuna_col,'UPM':self.upm_col}
        selector_col = selector_colnames_dict[selector_name]
        if check:
            checked =  st.checkbox('Filtrar por '+selector_name)
            if checked:
                 filter_df(self.df)
            return check
        else:
            filter_df(self.df)
            return True
    
     
    def create_map(self,popup_fields=['id_vivienda']):
        geometry = gpd.points_from_xy(self.df[self.long_col], self.df[self.lat_col])
        geo_df = gpd.GeoDataFrame(self.df,geometry=geometry)

        bounds = geo_df.geometry.total_bounds
        bbox_centroid = shapely.geometry.box(*bounds).centroid
        
        map_ = folium.Map(location=list(bbox_centroid.coords)[0][::-1])
        gj = folium.GeoJson(geo_df.to_json(),
                            marker=folium.Circle(radius = 8,fill=True),
                            style_function=lambda x: {'color':'green','fillColor':'green'} if x['properties'][self.cod_visita_col] == 110 else {'color':'red','fillColor':'red'},
                            popup=folium.features.GeoJsonPopup(fields=popup_fields,labels=True)
                           ).add_to(map_)

        b = list(bounds)
        map_.fit_bounds([[b[1],b[0]],[b[3],b[2]]])
        folium_static(map_)



