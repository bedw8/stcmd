
import streamlit as st
from pathlib import Path

def fileToDownload(path: Path, label: Optional[str] = 'Descargar', finalFilename: Optional[str] = None):
    if not finalFilename:
        finalFilename = path.name
    st.download_button(label, data = path.open('rb'), file_name=finalFilename)
