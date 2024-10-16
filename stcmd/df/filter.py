import streamlit as st
import pandas as pd
from pathlib import Path
from dataclasses import dataclass, field
from typing import Union, Literal, Dict

@dataclass
class FilteredDF():
    df: pd.DataFrame 
    filter_dict: dict = field(default_factory=lambda : {})
    label: Union[str,None] = None
    
    def __post_init__(self):
        self.df = self.load_data(self.df.copy())
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
            isnum = pd.api.types.is_numeric_dtype(column)

            if isstr:
                df[selector_colname] = df[selector_colname].str.upper()

            column = df[selector_colname]

            if not opts:
                opts = pd.Series(column.unique()).sort_values(ignore_index=True).to_list()
            
            subset = type_(selector_name,options=opts,**kwargs)

            if subset is not None:
                if type_ is not st.multiselect:
                    # subset is category
                    bool_series = column == subset
                else:
                    # subset is list of admissible values
                    bool_series = column.isin(subset)
                    if len(subset) == 0:
                        self.avoid_show = True
                        bool_series = column == column

                df.query('@bool_series',inplace=True)
            else:
                pass

            return subset

        if check:
            show = st.checkbox('Filtrar por '+selector_name)
        else:
            show = True
        if show:
            return filter_df(self.df,**kwargs)
        
        return show
