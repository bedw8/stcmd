
import streamlit as st
from pathlib import Path
from typing import Optional

def fileToDownload(path: Path, label: Optional[str] = 'Descargar', finalFilename: Optional[str] = None):
    if not finalFilename:
        finalFilename = path.name
    st.download_button(label, data = path.open('rb'), file_name=finalFilename)


def uploadFile(label,parent=st):
    upDir = Path('uploads')
    upDir.mkdir(exist_ok=True)

    return parent.file_uploader(label)

def writeUploadedFileData(data_file):
    upDir = Path('uploads')
    name = upDir / data_file.name
    f = open(name,'wb')
    f.write(data_file.getbuffer())
    f.close()
    return name


