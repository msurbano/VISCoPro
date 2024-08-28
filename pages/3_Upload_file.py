import streamlit as st
import pandas as pd
from io import StringIO

if 'original' not in st.session_state:
    st.session_state.original = pd.DataFrame()

st.write('### Upload event log')

uploaded_file = st.file_uploader('Choose file')

if uploaded_file:
    bytes_data = uploaded_file.getvalue()

    stringio = StringIO(uploaded_file.getvalue().decode("ISO-8859-1"))
    #st.write(stringio)

    # To read file as string:
    string_data = stringio.read()

    try:
        try:
            df = pd.read_csv(uploaded_file)
        except:
            df = pd.read_excel(uploaded_file)
    except:
        st.error('Error loading file. Please be sure to either upload a CSV or an XLSX')


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

    st.write('Original event log')

    st.dataframe(df)
    
    st.markdown('##### 1. Next go to the _VISCoPro_ main page to define the context of the data. ')
    st.markdown('##### 2. Once the data context is defined, you can access _Pattern recommendation_ or _Pattern seacrh_ to obtain recommendations.')

    

    
    st.session_state.original = df  # backup the filtered df

    # st.write('filtered df')
    # st.dataframe(st.session_state.filtered_df)