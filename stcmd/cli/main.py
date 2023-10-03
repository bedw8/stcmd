

import os
import typer
import importlib.resources as ir
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated

app = typer.Typer(no_args_is_help=True,
                  context_settings={"allow_extra_args": True,
                                    "ignore_unknown_options": True,
                                    "help_option_names":['-h','--help']
                                    })

def writeDefaultSecrets(path: Path):
    secretsFile = path.open('w')
    secretsFile.write('''
[passwords]
# La regla es: usuario = "contraseña"
cmd = "user"

''')
    secretsFile.close()
    print('''Se creó archivo de contraseñas en .streamlit/secrets.toml 
Por defecto se agrega el usuario 'cmd' con contraseña 'user' (sin comillas). Recuerda editar estos valores en el archivo.''')

def writeDefaultPage(path: Path):
    pageFile = path.open('w')
    pageFile.write('''
import streamlit as st
        
st.markdown('## pagina de ejemplo')
st.write("holi")

''')
    pageFile.close()
    print('''Se creó el archivo page.py como una pagina de ejemplo.
Puedes correrla con:
    stcmd run page.py -L
La opción -L es para no tener que hacer ingresar usuario y contraseña. 
''')

@app.command(no_args_is_help=True)
def setup(path: Path = typer.Argument(...,help="La ruta de la carpeta que ser desea configurar",show_default=False),
          force: Optional[bool] = typer.Option(False,'--force','-f',help='Sobrescribe el archivo de credenciales si ya existe. Usar con precaución')):
    '''Configura una carpeta para una nueva pagina de Streamlit. Crea un archivo de credenciales por defecto para ingresar a la pagina.
       Si ya existe un archivo de credenciales NO lo sobrescribe.'''

    stFolder = path / '.streamlit'
    stFolder.mkdir(parents=True,exist_ok=True)

    page = path / 'page.py'
    if not page.is_file():
        writeDefaultPage(page)
    else:
        print('Ya existe un archivo page.py')

    secrets = stFolder / 'secrets.toml'
    if not secrets.is_file():
        writeDefaultSecrets(secrets)
    else:  
        if force:
            writeDefaultSecrets(secrets)
        else:
            print("Ya existe un archivo de configuración de usuarios en .streamlit/secrets.toml")

    return None   



@app.command(no_args_is_help=True)
def run(path: str = typer.Argument(...,help='Ruta del archivo .py de la página que se quiere correr.',show_default=False),
        port: Optional[int] = typer.Option(None,help="El puerto donde donde se quiere dejar corriendo la página.",show_default=False),
        nologin: bool = typer.Option(False,'--no-login','-L',help='Se salta el login',show_default=False)):
    '''Corre una pagina de Streamlit con el Login de CMD. 

    Para correr una pagina en desarrollo se recomienda usar la opcion --no-login o -L para evitar ingresar a cada rato.
    También se puede especificar el puerto con la opción --port.'''

    loginPath = ir.files('stcmd.login') / 'main.py'
    if nologin:
        loginPath = ''
    cli_command = f'python -m streamlit run {loginPath} {path}'

    if port:
        cli_command += f' --server.port {port}'

    os.system(cli_command)

