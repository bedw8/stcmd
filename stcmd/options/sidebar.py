import streamlit as st

def SidebarOptions(label: str, optList: List[str], addUserOpts: Optional[Dict[str, List[str]]] = None, delUserOpts: Optional[Dict[str, List[str]]] = None):
    """Agrega opciones en la barra lateral

    Parameter
    ---------
    label: str
        Texto sobre el menú desplegable   

    optList: List[str]
        Lista con las opciones para el menú desplegable

    addUserOpts: Optional[Dict[str, List[str]]], default: None
        Diccionario con lista de opciones que se añaden para cada usuario. Los usuario son las llaves del diccionario.

    delUserOpts: Optional[Dict[str, List[str]]], default: None
        Diccionario con lista de opciones que se eliminan para cada usuario. Los usuario son las llaves del diccionario.

    Returns
    -------
    streamlit.sidebar.selectbox 
        Menu desplegable en la barra lateral
    """
    user = st.session_state['username']
    if addUserOpts and user in addUserOpts:
        optList += addUserOpts[user]

    if delUserOpts and user in delUserOpts:
        optList = [opt for opt in optList if opt not in delUserOpts[user]]
          
    return  st.sidebar.selectbox(label,optList)

def SidebarSecondaryOptions(label: str, firstOption: str, optList: Dict[str,List[str]], title: Optional[Union[str,Dict[str,str]]] = None, addUserOpts: Optional[Dict[str, List[str]]] = None, delUserOpts: Optional[Dict[str, List[str]]] = None):
    if firstOption not in optList:
        pass
    else:
        if title:
            if isinstance(title,str):
                pass
            else:
                title = title[firstOption]
            st.sidebar.title(title)

        if firstOption not in optList:
            return None
        else:
            optList = optList[firstOption]
            if addUserOpts and firstOption in addUserOpts:
                addUserOpts = addUserOpts[firstOption]
            if delUserOpts and firstOption in delUserOpts:
                delUserOpts = delUserOpts[firstOption]

            return SidebarOptions(label,optList,addUserOpts,delUserOpts)

