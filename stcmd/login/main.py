# streamlit_app.py

import sys
import os
import time
import importlib.resources as ir
import importlib.util
from pathlib import Path

import streamlit as st
import pandas as pd

#os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.sidebar.text_input("Usuario", key="username")
        st.sidebar.text_input("Contraseña", type="password", key="password")
        st.sidebar.button('Ingresar', on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.sidebar.text_input("Usuario", key="username")
        st.sidebar.text_input("Contraseña", value='', type="password", key="password")
        st.sidebar.button('Ingresar', on_click=password_entered)
        st.sidebar.error("Usuario no conocído o contraseña incorrecta")
        return False
    else:
        # Password correct.
        return True


############################################################################
############################################################################
inputPath = ir.files('stcmd.login.input')

st.set_page_config(
        #page_title="Login Test",
        page_icon=str(inputPath / 'icon.jpg'),
        layout="wide",
        initial_sidebar_state="expanded")

st.sidebar.image(str(inputPath / 'cmd.png'))

if check_password():
    st.session_state['username'] = st.session_state['username']
    
    pagePath = Path(sys.argv[1])

    st.session_state['page_mtime'] = os.stat(pagePath).st_mtime
    spec = importlib.util.spec_from_file_location("page.name", pagePath)
    page = importlib.util.module_from_spec(spec)
    sys.modules["page.name"] = page

    spec.loader.exec_module(page)
    #while True:
    #    mtime = os.stat(pagePath).st_mtime
    #    if st.session_state['page_mtime'] != mtime:
    #        st.session_state['page_mtime'] = os.stat(pagePath).st_mtime
    #        spec.loader.exec_module(page)
    #
    #    time.sleep(0.5)
