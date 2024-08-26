import pandas as pd
import geopandas as gpd
import streamlit as st
import copy
import folium 
from folium.plugins import BeautifyIcon
import shapely
from pathlib import Path
from streamlit_folium import st_folium, folium_static
from pandas.api.types import is_string_dtype
from dataclasses import dataclass, field
from typing import Union, Literal, Dict
import json

@dataclass
class Mapa():
    df_path: str
    filter_dict: dict = field(default_factory=lambda : {})
    lat_col: str = 'latitud'
    long_col: str = 'longitud'
    color: Union[str,None] = None
    label: Union[str,None] = None
    df_gtype:Literal['llcols','gpd'] = 'llcols'
    
    def __post_init__(self):
        self.df = self.load_data(self.df_path)
        self.avoid_show = False
        self.layers = []

    @st.cache_data
    def load_data(_self,_path: Union[Path,pd.DataFrame]):
        path = _path
        self = _self
        if isinstance(_path,Path):
            if path.suffix in ['.xlsx','.xls']:
                df = pd.read_excel(path)
            if path.suffix == '.dta':
                df = pd.read_stata(path,convert_categorical=False)

            df[[self.lat_col,self.long_col]] = df[[self.lat_col,self.long_col]].apply(lambda c: c.str.replace(',','.') if is_string_dtype(c.dtype) else c).astype(float)

        if isinstance(path,pd.DataFrame):
            df = path

        return df

    def create_filter(self,selector_name,type_=st.selectbox,opts=None,check=True,**kwargs):
        if isinstance(selector_name,str):
            selector_colname = self.filter_dict[selector_name]
        # if dict
        else:
            name = selector_name.keys()[0]
            selector_colname = selector_name[name]
            selector_name = name


        # make st.selectbox a parameter
        def filter_df(df,opts=opts,**kwargs):            
            self.avoid_show = False
            column = df[selector_colname]
            isstr = pd.api.types.is_string_dtype(column)

            if isstr:
                df[selector_colname] = df[selector_colname].str.upper()
                column = df[selector_colname]

            if not opts:
                opts = pd.Series(column.unique()).sort_values(ignore_index=True).to_list()
            
            subset = type_(selector_name,options=opts,**kwargs)

            if isstr:
                bool_series = column == subset
            else:
                bool_series = column.isin(subset)
                if len(subset) == 0:
                    self.avoid_show = True
                    bool_series = column == column

            df.query('@bool_series',inplace=True)

        if check:
            show = st.checkbox('Filtrar por '+selector_name)
        else:
            show = True
        if show:
             filter_df(self.df,**kwargs)
        
        return show
    
    def _addPoints(_self,gdf,color='#49a561',popup=None,popupAlias=None,layer=None):
        if len(gdf) == 0:
            return
        geojson = gdf.to_json()
        folGJ = folium.GeoJson(geojson,
                               marker = folium.CircleMarker(fill=True),
                               style_function = lambda f: {"color": color, "fillColor": color},
                               popup=folium.GeoJsonPopup(fields=popup,aliases=popupAlias,labels=True) if popup else None
                               )
        
        if layer:
            fg = folium.FeatureGroup(name=layer, show=True).add_to(_self.m)
            _self.layers.append(fg)
            destination = _self.layers[-1]
        else:
            destination = _self.m
        
        folGJ.add_to(destination) 
        for feature in folGJ.data['features']:
            point = folium.Marker(location=feature['geometry']['coordinates'][::-1],
                          icon=folium.plugins.BeautifyIcon(
                            iconShape='rectangle',
                            iconsSize=[20,20],
                            iconAnchor=[10,-14],
                            border_color='#00000000',
                            borderWidth=5,
                            background_color='#00000000',
                            html=f'<div style="font-size: 10pt">{feature["properties"][_self.label]}</div>' if _self.label else None
                          )
                        )
            point.add_to(destination)

     
    def create_map(self,popup_fields=None, popupAlias=None, label=None,**kwargs):
        if self.avoid_show:
            st.write('No hay registros para el filtro selccionado')
            return

        if not isinstance(self.df, gpd.GeoDataFrame):
            geometry = gpd.points_from_xy(self.df[self.long_col], self.df[self.lat_col])
            geo_df = gpd.GeoDataFrame(self.df,geometry=geometry)
        else:
            geo_df = self.df
            if 'geometry' in popup_fields:
                geo_df['lat'] = geo_df.geometry.y
                geo_df['lon'] = geo_df.geometry.x

                popup_fields += ['lat','lon']
                popupAlias += ['lat', 'lon']
                popup_fields.remove('geometry')
        
        bounds = geo_df.geometry.total_bounds
        bbox_centroid = shapely.geometry.box(*bounds).centroid
        
        self.m = folium.Map(location=list(bbox_centroid.coords)[0][::-1])

        if self.color:
            green = geo_df.query(self.color)
            red = geo_df[~geo_df.index.isin(green.index)]
            
            self._addPoints(green,layer='CDF 110',popup=popup_fields,popupAlias=popupAlias)
            self._addPoints(red,color='#FF0000',layer='Otros',popup=popup_fields,popupAlias=popupAlias)
            folium.LayerControl().add_to(self.m)

        else:
            self._addPoints(geo_df,layer='CDF 110')
            folium.LayerControl().add_to(self.m)


        b = list(bounds)
        
        self.m.fit_bounds([[b[1],b[0]],[b[3],b[2]]])        
