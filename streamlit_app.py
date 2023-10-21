import streamlit as st
import pandas as pd 
from google.cloud import firestore
from google.oauth2 import service_account

import json
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="names-project-demo")

#Crear una referencia hacia la colección names de Firestore.
dbNames = db.collection("names")

#Visualizar el dataframe con st.dataframe
st.header("Nuevo registro")

#Crear controles de entrada para cada uno de los campos.
index = st.text_input("Index")
name = st.text_input("Name")
sex = st.selectbox('Select sex',('F','M','Other'))

#Crear un control de botón.
submit = st.button("Crear nuevo registro")

#Once the name has submitted, upload it to the database
if index and name and sex and submit:
  doc_ref = db.collection("names").document(name)

  #Si fue presionado y además se llenaron los campos de entrada, crear una
  #referencia al documento nuevo y usando el método set() insertar el
  #nuevo registro.
  doc_ref.set({
    "index": index,
    "name": name,
    "sex": sex
  })
  st.sidebar.write("Registro insertado correctamente")

#Lectura de documento de firestone
#Crear una referencia hacia la colección names de Firebase y convertirla en una lista
names_ref = list(db.collection(u'names').stream())

#Convertir la lista en un diccionario de Python.
names_dict = list(map(lambda x: x.to_dict(), names_ref))

#Crear un dataframe de pandas a partir del diccionario.
names_dataframe = pd.DataFrame(names_dict)

#Visualizar el dataframe con st.dataframe
st.dataframe(names_dataframe)

#Crear una función que reciba como parámetro el nombre a buscar, filtre y
#regrese un único documento
def loadByName(name):
   names_ref = dbNames.where(u'name', u'==', name)
   currentName = None
   for myname in names_ref.stream():
      currentName = myname
   return currentName

#Crear el control de texto para capturar el nombre a buscar
st.sidebar.subheader("Buscar nombre")
nameSearch = st.sidebar.text_input("nombre")

#Crear el control de botón para implementar la búsqueda
btnFiltrar = st.sidebar.button("buscar")

#Si el botón es presionado llamar a la función de búsqueda
if btnFiltrar:
   doc = loadByName(nameSearch)
   #Si el documento es encontrado visualizarlo
   if doc is None:
      st.sidebar.write("Nombre no existe")
   else:
      st.sidebar.write(doc.to_dict())

#Crear un botón para la operación de eliminar
st.sidebar.markdown("""---""")
btnEliminar = st.sidebar.button("eliminar")

#Si el botón es presionado, llamar a la función de búsqueda para validar la
#existencia de ese documento
if btnEliminar:
   deleteName = loadByName(nameSearch)
   #Si existe entonces, crear una referencia al documento y eliminar usando
   #el método delete()
   if deleteName is None:
      st.sidebar.write(f"{nameSearch} no existe")
   else:
      dbNames.document(deleteName.id).delete()
      st.sidebar.write(f"{nameSearch} eliminado")


#Crear un texto para capturar el nuevo nombre
st.sidebar.markdown("""---""")
newName = st.sidebar.text_input("Actualizar nombre")

#Crear un botón para la operación de actualizar
btnActualizar = st.sidebar.button("actualizar")

#Si el botón de actualizar es presionado, llamar a la función de búsqueda
#para validar la existencia de ese documento
if btnActualizar:
   updateName = loadByName(nameSearch)

   #Si existe entonces, crear una referencia al documento y actualizar el
   #campo nombre usando el método update()
   if updateName is None:
      st.sidebar.write(f"{nameSearch} no existe")
   else:
      myUpdateName = dbNames.document(updateName.id)
      myUpdateName.update(
        {
           "name" : newName
        }
      )
