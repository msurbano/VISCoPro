import streamlit as st
import pandas as pd
from io import StringIO
import pm4py
import tempfile
import os

if 'original' not in st.session_state:
    st.session_state.original = pd.DataFrame()

st.write('### Upload event log')

uploaded_file = st.file_uploader('Choose file')

if uploaded_file:
    if uploaded_file.name.endswith('.xes'):
        try:
            # Crear un archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xes') as temp_file:
                temp_file.write(uploaded_file.read())  # Escribir el contenido del archivo subido
                temp_file_path = temp_file.name  # Obtener la ruta del archivo temporal
            
            # Leer el archivo XES desde la ruta temporal
            log = pm4py.read_xes(temp_file_path)
            df = pm4py.convert_to_dataframe(log)
        except Exception as e:
            st.error(f"Error processing XES file: {str(e)}")
    elif uploaded_file.name.endswith('.csv'):
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error processing CSV file: {str(e)}")
    elif uploaded_file.name.endswith(('.xls', '.xlsx')):
        try:
            # Leer archivo Excel con pandas
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error processing Excel file: {str(e)}")
    else:
        st.error("Unsupported file format. Please upload a CSV or XES file")




    # df = pd.DataFrame()
    # df = pd.read_csv('./datasets/Event log example.csv')



    if df is not None:
        if pd.api.types.is_datetime64_any_dtype(df['time:timestamp']):
            st.write("1) La columna timestamp es de tipo datetime")
        else:
            # st.write('no es fecha')
            df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
            # st.write('1) timestamp convertido a tipo datetime')


        if not pd.api.types.is_string_dtype(df['case:concept:name']):
            df['case:concept:name'] = df['case:concept:name'].astype(str)

    st.write('Here you can explore the original event log:')

    st.dataframe(df)
    
    st.markdown('##### 1. Next go to the _Data context_ page to define the context of the data. ')
    st.markdown('##### 2. Once the data context is defined, you can access _Pattern recommendation_ or _Pattern seacrh_ to obtain recommendations.')

    

    
    st.session_state.original = df  # backup the filtered df

    # st.write('filtered df')
    # st.dataframe(st.session_state.filtered_df)