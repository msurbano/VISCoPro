import streamlit as st
import numpy as np
import pandas as pd
import pm4py
import copy
import deprecation
import os
# import cairosvg
from PIL import Image
# import svgwrite
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.transformation.log_to_features import algorithm as log_to_features
from pm4py.algo.filtering.dfg import dfg_filtering
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.statistics.rework.cases.log import get as cases_rework_get
from pm4py.statistics.start_activities.log.get import get_start_activities
from pm4py.statistics.end_activities.log.get import get_end_activities
import networkx as nx
from pm4py.statistics.rework.cases.log import get as rework_cases
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.statistics.rework.cases.log import get as rework_cases
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.attributes import attributes_filter
# from pm4py.objects.dfg import dfg_factory
import json
import re
# import datetime
from datetime import date, time, datetime
from pm4py.visualization.dfg.variants.frequency import apply
from pm4py.visualization.dfg.variants import performance
import warnings
warnings.filterwarnings("ignore")
import time
from datetime import datetime
from PIL import Image
from io import StringIO
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from streamlit import session_state as ss


st.set_page_config(page_title="Main page")

pd.set_option("styler.render.max_elements", 2000000)

st.title("VISCoPro")
st.markdown("""---""")

# pm4py_version = pm4py.__version__
# st.write(f"La versión de pm4py instalada es: {pm4py_version}")

# Convertir timestamp a tipo date
def convertir_a_fecha_hora(fecha_hora_str):
    formato = "%m/%d/%Y %H:%M:%S"
    return datetime.strptime(fecha_hora_str, formato)

def cargar_datos():
    uploaded_file = st.sidebar.file_uploader("Choose a file (.csv)")

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

        string_data = stringio.read()

        return pd.read_csv(uploaded_file)

# Check input data
# @st.cache_resource
def check_log(data):
    if (type(data) != pm4py.objects.log.obj.EventLog):
        data = log_converter.apply(data)
    return data

if "filter_types" not in st.session_state:
        st.session_state["filter_types"] = {}

if "filter_type_group" not in st.session_state:
        st.session_state["filter_type_group"] = {}

if "attribute" not in st.session_state:
        st.session_state["attribute"] = {}

if "values" not in st.session_state:
        st.session_state["values"] = {}

if "act1" not in st.session_state:
        st.session_state["act1"] = {}

if "act2" not in st.session_state:
        st.session_state["act2"] = {}

if "actk" not in st.session_state:
        st.session_state["actk"] = {}

if "rango" not in st.session_state:
    st.session_state["rango"] = {}

if "number_values" not in st.session_state:
    st.session_state["number_values"] = {}

if "range_values" not in st.session_state:
    st.session_state["range_values"] = {}

if "modes" not in st.session_state:
    st.session_state["modes"] = {}

if "nrange" not in st.session_state:
    st.session_state["nrange"] = {}

if "rango2" not in st.session_state:
    st.session_state["rango2"] = {}

if "input_values" not in st.session_state:
    st.session_state["input_values"] = {}

if "group" not in st.session_state:
    st.session_state["group"] = {}

if "nfollow" not in st.session_state:
    st.session_state["nfollow"] = 1

if "lista_act" not in st.session_state:
    st.session_state["lista_act"] = {}


# Manipulation  
def manipulation(df, original, i):
    # Filtro de tipo
    ft_group_default = st.session_state["filter_type_group"].get(f'ft_group_{i}', 'Attribute')
    ft_group = st.sidebar.selectbox(
        'Filter type',
        ('Attribute', 'Performance', 'Follower', 'Timeframe', 'Rework', 'Endpoints'),
        index=['Attribute', 'Performance', 'Follower', 'Timeframe', 'Rework', 'Endpoints'].index(ft_group_default),
        key=f'ft_group_{i}'
    )
    st.session_state["filter_type_group"][f'ft_group_{i}'] = ft_group

    filters1 = ("Mandatory", "Forbidden", "Keep Selected")
    filters2 = ("Case performance", 'Path performance')
    filters3 = ("Directly Followed", "Eventually Followed", "Keep Selected Fragments")

    if ft_group == 'Attribute':
        filter_modes = filters1
    elif ft_group == 'Performance':
        filter_modes = filters2
    elif ft_group == 'Follower':
        filter_modes = filters3
    else:
        filter_modes = [ft_group]

    default_value = st.session_state["filter_types"].get(f'ft_{i}', filter_modes[0])
    if default_value not in filter_modes:
        default_value = filter_modes[0]
    ft = st.sidebar.selectbox('Filter mode', filter_modes, index=filter_modes.index(default_value), key=f'ft_{i}')
    st.session_state["filter_types"][f'ft_{i}'] = ft

    def small_text(text):
        return f"<p style='font-size:11px; color:grey; font-style:italic;'>{text}</p>"

    if ft in ("Mandatory", "Forbidden", "Keep Selected"):
        explanations = {
            'Mandatory': "This filter removes all cases that do not have at least one event with one of the selected values.",
            'Forbidden': "This filter removes all cases that have at least one event with one of the selected values.",
            'Keep Selected': "This filter removes all events that do not have one of the selected values."
        }
        st.sidebar.markdown(small_text(explanations[ft]), unsafe_allow_html=True)

        at = st.sidebar.selectbox(
            'Attribute', original.columns,
            index=original.columns.get_loc(st.session_state["attribute"].get(f'at_{i}', original.columns[0])),
            key=f'at_{i}'
        )
        st.session_state["attribute"][f'at_{i}'] = at

        valores = ['* All values'] + list(original[at].unique())
        # st.write(valores)
        default_values = st.session_state["values"].get(f'value_{i}', [])
        valid_default_values = [value for value in default_values if value in valores]

        value = st.sidebar.multiselect('Value', list(valores), key=f'value_{i}', default=valid_default_values)
        st.session_state["values"][f'value_{i}'] = value

        g = st.sidebar.checkbox('Group by', key=f'g_{i}', value=st.session_state['group'].get(f'g_{i}', False))
        st.session_state['group'][f'g_{i}'] = g

        manip = [ft, (at, g), value]

    elif ft == "Path performance":
        act1 = st.sidebar.selectbox(
            'From', original['concept:name'].unique(),
            index=original['concept:name'].unique().tolist().index(st.session_state["act1"].get(f'act1_{i}', original['concept:name'].unique()[0])),
            key=f'act1_{i}'
        )
        st.session_state["act1"][f'act1_{i}'] = act1

        act2 = st.sidebar.selectbox(
            'To', original['concept:name'].unique(),
            index=original['concept:name'].unique().tolist().index(st.session_state["act2"].get(f'act2_{i}', original['concept:name'].unique()[0])),
            key=f'act2_{i}'
        )
        st.session_state["act2"][f'act2_{i}'] = act2

        rango = st.sidebar.slider("Minutes between them:", 1, 500, key=f'rang_{i}', value=st.session_state["rango"].get(f'rang_{i}', (25, 75)))
        st.session_state["rango"][f'rang_{i}'] = rango

        manip = [ft, (act1, act2), rango]

    elif ft == "Endpoints":
        st.sidebar.markdown(small_text("This filter removes all cases in which the first and/or last events do not have one of the selected values."), unsafe_allow_html=True)

        options = ['* All values'] + list(pm4py.get_start_activities(df))
        default_values = st.session_state["act1"].get(f'act1_{i}', [])
        valid_defaults = [val for val in default_values if val in options]

        act1 = st.sidebar.multiselect('From', options, key=f'act1_{i}', default=valid_defaults)
        st.session_state["act1"][f'act1_{i}'] = act1

        options2 = ['* All values'] + list(pm4py.get_end_activities(df))
        default_values2 = st.session_state["act2"].get(f'act2_{i}', [])
        valid_defaults2 = [val for val in default_values2 if val in options2]

        act2 = st.sidebar.multiselect('To', options2, key=f'act2_{i}', default=valid_defaults2)
        st.session_state["act2"][f'act2_{i}'] = act2

        manip = [ft, act1, act2]

    elif ft == 'Rework':
        act1 = st.sidebar.selectbox(
            'Activity', df['concept:name'].unique(),
            index=df['concept:name'].unique().tolist().index(st.session_state["act1"].get(f'act1_{i}', df['concept:name'].unique()[0])),
            key=f'act1_{i}'
        )
        st.session_state["act1"][f'act1_{i}'] = act1

        value = st.sidebar.number_input('Minimum frequency', step=1, key=f'value_{i}', value=st.session_state["number_values"].get(f'value_{i}', 0))
        st.session_state["number_values"][f'value_{i}'] = value

        manip = [ft, act1, value]

    elif ft == 'Case performance':
        mode_options = ["Unique interval", "More than one interval"]
        mode = st.sidebar.selectbox("Mode", mode_options, index=mode_options.index(st.session_state["modes"].get(f'mode_{i}', mode_options[0])), key=f'mode_{i}')
        st.session_state["modes"][f'mode_{i}'] = mode

        if mode == "Unique interval":
            rango = st.sidebar.slider("Minutes between them:", 1, 500, key=f'rang_{i}', value=st.session_state["range_values"].get(f'rang_{i}', (25, 75)))
            st.session_state["range_values"][f'rang_{i}'] = rango
        else:
            n = st.sidebar.number_input('Number of intervals', step=1, min_value=2, key=f'nrange_{i}', value=st.session_state["nrange"].get(f'nrange_{i}', 2))
            st.session_state["nrange"][f'nrange_{i}'] = n
            rango = []
            for j in range(n):
                r1 = st.sidebar.slider(f"Minutes between the interval {j+1}:", 1, 500, key=f'rang2_{j}', value=st.session_state["rango2"].get(f'rang2_{j}', (25, 75)))
                rango.append(r1)
                st.session_state["rango2"][f'rang2_{j}'] = r1

        manip = [ft, mode, rango]

    elif ft_group == 'Timeframe':
        mode_time = ['events', 'contained', 'intersecting']
        mode = st.sidebar.selectbox('Mode', mode_time, key=f'mode_{i}', index=mode_time.index(st.session_state["modes"].get(f'mode_{i}', mode_time[0])))
        st.session_state["modes"][f'mode_{i}'] = mode

        r, l = st.sidebar.columns(2)

        default_date1 = st.session_state["input_values"].get(f'date1_{i}', original['time:timestamp'][0].date())
        default_hour1 = st.session_state["input_values"].get(f'hour1_{i}', datetime.now().time())

        default_date2 = st.session_state["input_values"].get(f'date2_{i}', original['time:timestamp'][0].date())
        default_hour2 = st.session_state["input_values"].get(f'hour2_{i}', datetime.now().time())

        rango1 = r.date_input("From", key=f'date1_{i}', value=default_date1)
        h1 = l.time_input('Time From', key=f'hour1_{i}', value=default_hour1)
        start_datetime = datetime.combine(rango1, h1)

        rango2 = r.date_input("To", key=f'date2_{i}', value=default_date2)
        h2 = l.time_input('Time To', key=f'hour2_{i}', value=default_hour2)
        end_datetime = datetime.combine(rango2, h2)

        st.session_state["input_values"][f'date1_{i}'] = rango1
        st.session_state["input_values"][f'hour1_{i}'] = h1
        st.session_state["input_values"][f'date2_{i}'] = rango2
        st.session_state["input_values"][f'hour2_{i}'] = h2

        manip = [ft_group, mode, (start_datetime, end_datetime)]
    
    else:
        nfollow = st.sidebar.number_input('Number of fragments', step=1, min_value=1, value=ss['nfollow'])
        ss['nfollow'] = nfollow
        k = 1
        lista_act = []

        act1 = st.sidebar.selectbox(
                        'From', (original['concept:name'].unique()), 
                        index=original['concept:name'].unique().tolist().index(st.session_state["act1"].get('act1_%s' % i, original['concept:name'].unique()[0])), 
                        key='act1_%s' % i)
        st.session_state["act1"]['act1_%s' % i] = act1

        while (nfollow > 1 and k < nfollow):

            # st.write('prueba')
            actk = st.sidebar.selectbox(
                    'To - From', (original['concept:name'].unique()), 
                    index=original['concept:name'].unique().tolist().index(st.session_state["actk"].get('actk_%s' % k, original['concept:name'].unique()[0])), 
                    key='actk_%s' % k)
            st.session_state["actk"]['actk_%s' % k] = actk

            lista_act.append(actk)
            k = k+1

        ss['lista_act'] = lista_act

        act2 = st.sidebar.selectbox(
                    'To', (original['concept:name'].unique()), 
                    index=original['concept:name'].unique().tolist().index(st.session_state["act2"].get('act2_%s' % i, original['concept:name'].unique()[0])), 
                    key='act2_%s' % i)
        st.session_state["act2"]['act2_%s' % i] = act2

        
        # st.write(lista_act)
        manip = [ft,(act1,act2),lista_act]

    st.sidebar.markdown("""---""")

    filtered_dataframe={}
    
    dfs={}

    if not isinstance(df, dict):
        dfs['']=df
    else:
        dfs=df 

    # st.write('Atributos manipulacion: ', manip)

    ftype = manip[0]
    v1 = manip[1]
    v2 = manip[2]

    for key, df in dfs.items():

        if (ftype == 'Directly Followed'):
            activityFROM = v1[0] 
            activityTO = v1[1]
            if(v2==[]):
                filt = pm4py.filter_directly_follows_relation(df, 
                    [(activityFROM,activityTO)], activity_key='concept:name', 
                            case_id_key='case:concept:name', timestamp_key='time:timestamp')
                if(len(filt)!=0):
                    if(key==''):
                        filtered_dataframe[str(activityFROM) + " - " + str(activityTO)] = filt
                    else:
                        filtered_dataframe[key + " ; " + str(activityFROM) + " - " + str(activityTO)] = filt
            else:
                v2.insert(0, activityFROM)
                v2.append(activityTO)
                for frag in range(len(v2) - 1):
                    activityFROM = v2[frag]
                    activityTO = v2[frag + 1]
                    filt = pm4py.filter_directly_follows_relation(df, 
                        [(activityFROM, activityTO)], activity_key='concept:name', 
                            case_id_key='case:concept:name', timestamp_key='time:timestamp')

                    if(len(filt)!=0):
                        if(key==''):
                            filtered_dataframe[str(activityFROM) + " - " + str(activityTO)] = filt
                        else:
                            filtered_dataframe[key + " ; " + str(activityFROM) + " - " + str(activityTO)] = filt
                    
        elif(ftype == 'Eventually Followed'):

            activityFROM = v1[0] 
            activityTO = v1[1]
            if(v2==[]):
                filt = pm4py.filter_eventually_follows_relation(df, 
                    [(activityFROM,activityTO)], activity_key='concept:name', 
                            case_id_key='case:concept:name', timestamp_key='time:timestamp')
                if(len(filt)!=0):
                    if(key==''):
                        filtered_dataframe[str(activityFROM) + " - " + str(activityTO)] = filt
                    else:
                        filtered_dataframe[key + " ; " + str(activityFROM) + " - " + str(activityTO)] = filt
            else:
                v2.insert(0, activityFROM)
                v2.append(activityTO)
                for frag in range(len(v2) - 1):
                    activityFROM = v2[frag]
                    activityTO = v2[frag + 1]
                    filt = pm4py.filter_eventually_follows_relation(df, 
                        [(activityFROM, activityTO)], activity_key='concept:name', 
                            case_id_key='case:concept:name', timestamp_key='time:timestamp')

                    if(len(filt)!=0):
                        if(key==''):
                            filtered_dataframe[str(activityFROM) + " - " + str(activityTO)] = filt
                        else:
                            filtered_dataframe[key + " ; " + str(activityFROM) + " - " + str(activityTO)] = filt
                   

                    
        elif ftype == "Keep Selected Fragments":
            # st.write('prueba')
            activityFROM = v1[0] 
            activityTO = v1[1]
            if(v2==[]):
                filt = pm4py.filter_between(df, 
                    activityFROM,activityTO, activity_key='concept:name', 
                            case_id_key='case:concept:name', timestamp_key='time:timestamp')
                # st.write(filt)
                if(len(filt)!=0):
                    if(key==''):
                        filtered_dataframe[str(activityFROM) + " - " + str(activityTO)] = filt
                    else:
                        filtered_dataframe[key + " ; " + str(activityFROM) + " - " + str(activityTO)] = filt
                
            else:
                v2.insert(0, activityFROM)
                v2.append(activityTO)
                for frag in range(len(v2) - 1):
                    activityFROM = v2[frag]
                    activityTO = v2[frag + 1]
                    filt = pm4py.filter_between(df, 
                        activityFROM, activityTO, activity_key='concept:name', 
                            case_id_key='case:concept:name', timestamp_key='time:timestamp')

                    if(len(filt)!=0):
                        if(key==''):
                            filtered_dataframe[str(activityFROM) + " - " + str(activityTO)] = filt
                        else:
                            filtered_dataframe[key + " ; " + str(activityFROM) + " - " + str(activityTO)] = filt
                    
            
      

        elif ftype == 'Mandatory':
            g = v1[1]
            atr = v1[0] 
            if v2 == ['* All values']: 
                valores = df[atr].unique()
                for v in valores:
                    grupo = pm4py.filter_trace_attribute_values(df, atr, [v])
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str([v])] = grupo
                        else:
                            filtered_dataframe[key + " - " + str([v])] = grupo
                        
            else:    
                # st.write(v1)
                if(g==True):
                    # st.write('prueba')
                    for v in v2:
                        grupo = pm4py.filter_trace_attribute_values(df, atr, [v])
                        if(len(grupo)!=0):
                            if(key==""):
                                filtered_dataframe[str([v])] = grupo
                            else:
                                filtered_dataframe[key + " - " + str([v])] = grupo
                            # filtered_dataframe[v] = grupo
                # st.write(v1, v2)
                else:
                    grupo = pm4py.filter_trace_attribute_values(df, atr, v2)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str(v2)] = grupo
                        else:
                            filtered_dataframe[key + " - " + str(v2)] = grupo
                        
        elif ftype == 'Keep Selected':
            g = v1[1]
            atr = v1[0] 
            
            if v2 == ['* All values']:  
                valores = df[atr].unique()
                for v in valores:
                    grupo = df[df[atr]==v]
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str([v])] = grupo
                        else:
                            filtered_dataframe[key + " - " + str([v])] = grupo
                        # filtered_dataframe[v] = grupo
            else:   
                if(g==True):
                    valores = df[atr].unique()
                    for v in v2:
                        grupo = df[df[atr]==v]
                        if(len(grupo)!=0):
                            # filtered_dataframe[v] = grupo
                            if(key==""):
                                filtered_dataframe[str([v])] = grupo
                            else:
                                filtered_dataframe[key + " - " + str([v])] = grupo
                else:                    
                    grupo = pm4py.filter_event_attribute_values(df, atr, v2,  level='event')
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str(v2)] = grupo
                        else:
                            filtered_dataframe[key + " - " + str(v2)] = grupo

        elif ftype == 'Forbidden':   
            g = v1[1] 
            atr = v1[0] 
            
            if v2 == ['* All values']: 
                valores = df[atr].unique()
                for v in valores:
                    grupo = pm4py.filter_trace_attribute_values(df, atr, [v], retain=False)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str([v])] = grupo
                        else:
                            filtered_dataframe[key + " - " + str([v])] = grupo
                        # filtered_dataframe[v] = grupo
            else:       
                if(g==True):
                    for v in v2:
                        grupo = pm4py.filter_trace_attribute_values(df, atr, [v], retain=False)
                        if(len(grupo)!=0):
                            if(key==""):
                                filtered_dataframe[str([v])] = grupo
                            else:
                                filtered_dataframe[key + " - " + str([v])] = grupo
                            # filtered_dataframe[v] = grupo
                else:
                    grupo = pm4py.filter_trace_attribute_values(df, atr, v2, retain=False)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str(v2)] = grupo
                        else:
                            filtered_dataframe[key + " - " + str(v2)] = grupo

        elif ftype == 'Rework':
            # log = check_log(df)
            grupo = pm4py.filter_activities_rework(df, v1, v2)
            # grupo = pm4py.convert_to_dataframe(filtered_log)
            if(len(grupo)!=0):
                if(key==""):
                    filtered_dataframe[v1 + ': ' + str(v2)] = grupo
                else:
                    filtered_dataframe[key + " - " + v1 + ': ' + str([v2])] = grupo
                
        elif ftype == 'Endpoints':
            # log = check_log(df)
            log_start = pm4py.get_start_activities(df)
            log_end = pm4py.get_end_activities(df)

            if (v1 == ['* All values'] and v2 == []):
                for a in log_start:
                    grupo = pm4py.filter_start_activities(df, [a])
                    # grupo = pm4py.convert_to_dataframe(filtered_log)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[a + ' - ' + 'endpoints'] = grupo
                        else:
                            filtered_dataframe[key + " - " + a + ' - ' + 'endpoints'] = grupo
                        

            elif (v1 == ['* All values'] and v2 == ['* All values']):
                for a in log_start:
                    for e in log_end:
                        filtered_log = pm4py.filter_start_activities(df, [a])
                        grupo = pm4py.filter_end_activities(filtered_log, [e])
                        # grupo = pm4py.convert_to_dataframe(filtered_log)
                        if(len(grupo)!=0):
                            if(key==""):
                                filtered_dataframe[a + ' - ' + e] = grupo
                            else:
                                filtered_dataframe[key + " - " + a + ' - ' + e] = grupo
                            
            
            elif (v1 == ['* All values'] and v2 != []):
                for a in log_start:
                    filtered_log = pm4py.filter_start_activities(df, [a])
                    grupo = pm4py.filter_end_activities(filtered_log, v2)
                    # grupo = pm4py.convert_to_dataframe(filtered_log)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[a + ' - ' + str(v2)] = grupo
                        else:
                            filtered_dataframe[key + ' - ' + a + ' - ' + str(v2)] = grupo

            elif (v1 != [] and v2 == ['* All values']):
                for e in log_end:
                    filtered_log = pm4py.filter_end_activities(df, [e])
                    grupo = pm4py.filter_start_activities(filtered_log, v1)
                    # grupo = pm4py.convert_to_dataframe(filtered_log1)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str(v1) + ' - ' + e] = grupo
                        else:
                            filtered_dataframe[key + ' - ' + str(v1) + ' - ' + e] = grupo

            elif (v1 == [] and v2 == ['* All values']):
                for e in log_end:
                    grupo = pm4py.filter_end_activities(df, [e])
                    # grupo = pm4py.convert_to_dataframe(filtered_log)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe['startpoints' + ' - ' + e] = grupo
                        else:
                            filtered_dataframe[key + ' - ' + 'startpoints' + ' - ' + e] = grupo
            
            elif (v1 != [] and v2 != []):
                filtered_log = pm4py.filter_start_activities(df, v1)
                grupo = pm4py.filter_end_activities(filtered_log, v2)
                # grupo = pm4py.convert_to_dataframe(filtered_log)
                if(len(grupo)!=0):
                    if(key==""):
                    # st.write(a)
                        filtered_dataframe[str(v1) + ' - ' + str(v2)] = grupo
                    else:
                        filtered_dataframe[key + ' - ' + str(v1) + ' - ' + str(v2)] = grupo

            
            elif (v1 == [] and v2 != []):
                grupo = pm4py.filter_end_activities(df, v2)
                # grupo = pm4py.convert_to_dataframe(filtered_log)
                if(len(grupo)!=0):
                    if(key==""):
                        filtered_dataframe['startpoints -' + str(v2)] = grupo
                    else:
                        filtered_dataframe[key + ' - ' + 'startpoints -' + str(v2)] = grupo

            elif (v1 != [] and v2 == []):
                grupo = pm4py.filter_start_activities(df, v1)
                # grupo = pm4py.convert_to_dataframe(filtered_log)
                if(len(grupo)!=0):
                    if(key==""):
                        filtered_dataframe['selected startpoints -  endpoints'] = grupo
                    else:
                        filtered_dataframe[key + ' - ' + 'selected startpoints -  endpoints'] = grupo

            else:
                if(key==""):
                    filtered_dataframe[str(v1) + ' - endpoints'] = df
                else:
                    filtered_dataframe[key + ' - ' + str(v1) + ' - endpoints'] = df

        elif ftype == 'Path performance':
            # log = check_log(df)
            grupo = pm4py.filter_paths_performance(df, v1, v2[0]*60, v2[1]*60)
            # grupo = pm4py.convert_to_dataframe(filtered_log)
            if(len(grupo)!=0):
                if(key==""):
                    filtered_dataframe[str(v1)] = grupo
                else:
                    filtered_dataframe[key + ' - ' + str(v1)] = grupo
        
        elif ftype == 'Timeframe':
            # log = check_log(df)
            # st.write(v2[0])
            # st.write(v2[1])
            # df['time:timestamp'] = df['time:timestamp'].astype('datetime64[ns]')
            # v3 = (pd.to_datetime(v2[0]).to_datetime64(), pd.to_datetime(v2[1]).to_datetime64())

            grupo = pm4py.filter_time_range(df, v2[0] , v2[1], mode=v1)

            # Parace que para events funciona bien pero para contained y intersecting no filtra bien 
            # grupo = pm4py.convert_to_dataframe(filtered_log)
            # st.write(grupo)
            if(len(grupo)!=0):
                if(key==""):
                    filtered_dataframe[str(v2[0]) + ' - ' + str(v2[1])] = grupo
                else:
                    filtered_dataframe[key + ' - ' + str(v2[0]) + ' - ' + str(v2[1])] = grupo

        elif ftype == 'Case performance':
            
            # log = check_log(df)
            if(v1=="Unique interval"):
                grupo = pm4py.filter_case_performance(df, v2[0]*60, v2[1]*60)
                # grupo = pm4py.convert_to_dataframe(filtered_log)
                if(len(grupo)!=0):
                    if(key==""):
                        filtered_dataframe[v2] = grupo
                    else:
                        filtered_dataframe[key + ' - ' + str(v2)] = grupo
            else:
                j=0
                for j in rango:
                    # st.write(j, rango)
                    grupo = pm4py.filter_case_performance(df, j[0]*60, j[1]*60)
                    # grupo = pm4py.convert_to_dataframe(filtered_log)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[j] = grupo
                        else:
                            filtered_dataframe[key + ' - ' + j] = grupo
                    #     st.write('si hay resultados')
                    # else:
                    #     st.write('No hay resultados')

    return filtered_dataframe 


    


def df_to_dfg(dfs,nodes,metric):
    # st.write('paso 1')
    dic={}

    for key, df in dfs.items():
        if metric in ['Absolute Frequency', 'Case Frequency', 'Max Repetitions', 'Total Repetitions', 'Frequency']:
            # st.write(df, nodes)
            dfg, sa, ea = pm4py.discover_dfg(df, activity_key=nodes)

            # dfg, sa, ea = pm4py.discover_dfg(df, activity_key='City')
            # st.write('3) DFG descubierto')
            
            grafo = defineGraphFrequency(df, dfg, nodes, metric)
            # st.write('4) Metricas calculadas')
            # st.write(dfg, grafo.nodes.data)            

            # st.write(grafo.edges.data())
            dic[key] = {'dfg': dfg, 'sa': sa, 'ea': ea, 'df': df, 'graph':grafo}
        else:
            dfg, sa, ea = pm4py.discovery.discover_performance_dfg(df, activity_key=nodes)
            # st.write('3) DFG descubierto')
            
            grafo = defineGraphPerformance(df, dfg, nodes, metric)
            # st.write('4) Metricas calculadas')

            
            dic[key] = {'dfg': dfg, 'sa': sa, 'ea': ea, 'df': df,'graph':grafo} 
    # st.write('paso 1 check')

    # st.write(list(dic.items())[0])
    return dic

def defineGraphFrequency(df, dfg, nodes, metric): 
    # st.write('paso 2')
    lista_nodos = list(df[nodes].unique())
    G = nx.DiGraph()
    dic_paths = {}
    dic_max = {}
    dic_nodes = {}

    

    if(metric == 'Absolute Frequency'):
        abs_freq_nodes = df[nodes].value_counts().to_dict()
    elif(metric == 'Case Frequency'):
        case_freq_nodes = df.groupby(nodes).apply(lambda x: len(x['case:concept:name'].unique())).to_dict() 
    elif(metric == 'Max Repetitions'):
        max_repetitions_nodes = df.groupby(nodes).apply(lambda x: x['case:concept:name'].value_counts().max()).to_dict()
    elif(metric=='Total Repetitions'):
        sum_repetitions_nodes = df.groupby(nodes).apply(lambda x: (x['case:concept:name'].value_counts() > 1).sum())

    
    # max_rep, case_freq, total_repetitions = returnEdgesInfo(df,nodes,'case:concept:name','time:timestamp')
    if(metric in ['Case Frequency', 'Max Repetitions', 'Total Repetitions']):
        res = returnEdgesInfo(df,nodes,'case:concept:name','time:timestamp', metric)
        # st.write('4.1) returnEdgesInfo hecho')

    for key in dfg.keys():  
        # st.write(key)          
        dic_paths[key]={}
        # for metric in metrics:
        if(metric == 'Absolute Frequency'):
            dic_paths[key]['abs_freq'] = dfg[key]
        elif(metric == 'Case Frequency'):
            dic_paths[key]['case_freq'] = res[key]
        elif(metric == 'Max Repetitions'):
            dic_paths[key]['max_repetitions'] = res[key]
        elif(metric=='Total Repetitions'):
            dic_paths[key]['total_repetitions'] = res[key]
    
    # abs_freq_nodes = df[nodes].value_counts().to_dict()
    # case_freq_nodes = df.groupby(nodes).apply(lambda x: len(x['case:concept:name'].unique())).to_dict() 
    # max_repetitions_nodes = df.groupby(nodes).apply(lambda x: x['case:concept:name'].value_counts().max()).to_dict()
    # sum_repetitions_nodes = df.groupby(nodes).apply(lambda x: (x['case:concept:name'].value_counts() > 1).sum())

    for key in lista_nodos:
        # st.write(case_freq_nodes[key])
        dic_nodes[key]={}
        # for metric in metrics:
        if(metric == 'Absolute Frequency'):
            dic_nodes[key]['abs_freq'] = abs_freq_nodes[key]
        elif(metric == 'Case Frequency'):
            dic_nodes[key]['case_freq'] = case_freq_nodes[key]
        elif(metric == 'Max Repetitions'):
            dic_nodes[key]['max_repetitions'] = max_repetitions_nodes[key]
        elif(metric == 'Total Repetitions'):
            dic_nodes[key]['total_repetitions'] = sum_repetitions_nodes[key]
    
    for nodo, propiedades in dic_nodes.items():
        G.add_node(nodo, **propiedades)
    
    for edge, propiedades in dic_paths.items():
        actividad_origen, actividad_destino = edge
        G.add_edge(actividad_origen,actividad_destino, **propiedades)  
        
    return G
    
def defineGraphPerformance(df, dfg, nodes, metrics):  

    G = nx.DiGraph()

    lista_nodos = list(df[nodes].unique())

    dic_paths = {}
    dic_nodes = {}

    for key in dfg.keys():
        
        if(metric=='Mean CT'):
            dic_paths[key] = {'mean CT':dfg[key]['mean']}
        elif(metric=='Median CT'):
            dic_paths[key] = {'median CT':dfg[key]['median']}
        elif(metric=='StDev CT'):
            dic_paths[key] = {'stdev CT':dfg[key]['stdev']}
        elif(metric=='Total CT'):
            dic_paths[key] = {'total CT':dfg[key]['sum']}

    for nodo in lista_nodos:
        G.add_node(nodo)

    for edge, propiedades in dic_paths.items():        
        actividad_origen, actividad_destino = edge
        G.add_edge(actividad_origen,actividad_destino, **propiedades)  
    case_durations = pm4py.get_all_case_durations(df, activity_key='concept:name', 
                 case_id_key='case:concept:name', timestamp_key='time:timestamp')
    
    if(metric=='Mean CT'):       
        avg_duration=np.mean(case_durations)
        G.graph['meanCTWholeProcess'] = avg_duration
    elif(metric=='Median CT'):
        avg_duration=np.median(case_durations)
        G.graph['medianCTWholeProcess'] = avg_duration   

    return G

def threshold(datos, metric, a, p, nodes):
    dic={}
    ident = 0
    for key, dfg in datos.items():
        df = dfg['df']
        dfg_ini = dfg['dfg']

        if metric in ['Mean CT', 'Median CT', 'StDev CT', 'Total CT']:  
            translater={"Median CT":"median","Mean CT":"mean","StDev CT":"stdev","Total CT":"sum"}

            ac = dict(df[nodes].value_counts())   
            dfg_discovered, sa, ea = pm4py.discover_dfg(df, activity_key=nodes)      

            if(p==100 and a==100):
                dfg_path = dfg_ini
            elif(p==100):
                dfg_path, sa, ea, ac = dfg_filtering.filter_dfg_on_activities_percentage(dfg_discovered, sa, ea, ac, a/100)
            elif(a==100):
                dfg_path, sa, ea, ac = dfg_filtering.filter_dfg_on_paths_percentage(dfg_discovered, sa, ea, ac, p/100)
            else:
                dfg_act, sa, ea, ac = dfg_filtering.filter_dfg_on_activities_percentage(dfg_discovered, sa, ea, ac, a/100)
                dfg_path, sa, ea, ac = dfg_filtering.filter_dfg_on_paths_percentage(dfg_act, sa, ea, ac, p/100)

            
            dfg['sa'] = {key: dfg['sa'][key] for key in list(sa.keys())}
            dfg['ea'] = {key: dfg['ea'][key] for key in list(ea.keys())}
            dfg['dfg'] = {key: dfg['dfg'][key] for key in list(dfg_path.keys())}


            measure=translater[metric]


            pm4py.save_vis_performance_dfg(dfg['dfg'],dfg['sa'],dfg['ea'], './figures/dfg' + str(ident) + '.svg', aggregation_measure=measure)
            
            st.write(str(key))

            # st.image('./figures/dfg' + str(ident) + '.svg')
            with open('./figures/dfg' + str(ident) + '.svg', 'r', encoding='utf-8') as file:
                svg_data = file.read()
                st.image(svg_data)
                # ------------------------------ modification
                st.download_button(
                    label="Descargar SVG",
                    data=svg_data,
                    file_name='dfg' + str(ident) + '.svg',
                    mime='image/svg+xml'
                )

            # Mostrar el SVG utilizando HTML
            # st.markdown(f'<div>{svg_data}</div>', unsafe_allow_html=True)
            # svg_html = f'<div style="width: 400px; max-width: 100%;">{svg_data}</div>'

            # st.markdown(svg_html, unsafe_allow_html=True)

            ident = ident + 1

        else:
            translater={"Absolute Frequency":"abs_freq","Case Frequency":"case_freq",
                "Max Repetitions":"max_repetitions", "Total Repetitions":
                "total_repetitions"}


            ac = dict(df[nodes].value_counts())

            if(p==100 and a==100):
                dfg_path = dfg_ini
            elif(p==100):
                dfg_path, sa, ea, ac = dfg_filtering.filter_dfg_on_activities_percentage(dfg['dfg'], dfg['sa'], dfg['ea'], ac, a/100)
            elif(a==100):
                dfg_path, sa, ea, ac = dfg_filtering.filter_dfg_on_paths_percentage(dfg['dfg'], dfg['sa'], dfg['ea'], ac, p/100)
            else:
                dfg_act, sa, ea, ac = dfg_filtering.filter_dfg_on_activities_percentage(dfg['dfg'], dfg['sa'], dfg['ea'], ac, a/100)
                dfg_path, sa, ea, ac = dfg_filtering.filter_dfg_on_paths_percentage(dfg_act, sa, ea, ac, p/100)

            G = dfg['graph']
            
            G_nodes_filtered=removeEdges(G,list(dfg_path.keys()))
            G_edges_filtered=removeNodes(G_nodes_filtered,list(ac.keys()))

            measure=translater[metric]
            
            metric_nodes=dict(G.nodes.data(measure))
            
            list_edges=list(G.edges.data())
            dfg_custom={(edge[0],edge[1]):edge[2][measure] for edge in list_edges}

            gviz=apply(dfg_custom,None,None,metric_nodes,None)
            st.write(str(key))
            st.write(gviz)         


            ident = ident + 1

            

def removeEdges(G,filteredEdges):
    for edge in list(G.edges):
        if edge not in filteredEdges:
            G.remove_edge(*edge)
            
    return G
            
def removeNodes(G,filteredNodes):
    for node in list(G.nodes):
        if node not in filteredNodes:
            G.remove_node(node)
            
    return G

def returnEdgesInfo(df,concept_name,case_concept_name,timestamp,metric):
    df_sorted=df.reset_index().sort_values(by=[case_concept_name,timestamp,"index"])
    first_events=df_sorted.iloc[0:len(df_sorted)-1] 
    second_events=df_sorted.iloc[1:len(df_sorted)]
    transitions=[]
    case_ids=[]

    for (index1,row1),(index2,row2) in zip(first_events.iterrows(),second_events.iterrows()):
        if row1[case_concept_name]==row2[case_concept_name]:
            transitions.append((row1[concept_name],row2[concept_name]))
            case_ids.append(row2[case_concept_name])
        else:
            continue      
    df_edges=pd.DataFrame.from_dict({"Transitions":transitions,"case_ids":case_ids})

    if(metric == 'Case Frequency'):
        res=returnCaseFreqEdges(df_edges)
    elif(metric == 'Max Repetitions'):
        res=returnMaxRepititionsEdges(df_edges)
    elif(metric == 'Total Repetitions'):
        res = returnTotalRepetitions(df_edges)
    else:
        res={}

    # max_rep=returnMaxRepititionsEdges(df_edges)
    # case_freq=returnCaseFreqEdges(df_edges)
    # total_rep = returnTotalRepetitions(df_edges)

    return res

def returnTotalRepetitions(df):
    totalRep=df.groupby("Transitions").apply(lambda x: (x['case_ids'].value_counts() > 1).sum())
    return totalRep

def returnCaseFreqEdges(df):
    case_freq=df.groupby('Transitions')['case_ids'].nunique()
    return case_freq

def returnMaxRepititionsEdges(df):
    maxRep=df.groupby(["case_ids","Transitions"]).apply(lambda x: len(x)).reset_index().groupby("Transitions").apply(lambda x: max(x[0]))
    return maxRep



#  ------------------------------------------------------------------------------------------------
# Elementos de la interfaz
#  ------------------------------------------------------------------------------------------------

# dataframe = pd.DataFrame()

# dataframe = pd.read_csv('./datasets/example.csv')
# dataframe = cargar_datos()

if 'original' not in st.session_state:

    # log_prueba = pm4py.read_xes("datasets/BPI_Challenge_2019.xes")
    # df_prueba = pm4py.convert_to_dataframe(log_prueba)
    # df_prueba.to_csv('BPIC2019.csv', index=False)
    # st.dataframe(df_prueba)


    st.session_state.original = pd.DataFrame()
    st.markdown(" ##### **Please, upload the event log in _Upload file_.** ")



if len(st.session_state.original):
    dataframe = st.session_state.original

    if 'inicial' not in st.session_state:
        st.session_state.inicial = dataframe

    left_column, right_column = st.columns(2)

    if dataframe is not None:

        if st.checkbox('Show Event log'):
            dataframe

        atributos = dataframe.columns.tolist()
        atributos2 = atributos.copy()

        if 'concept:name' in atributos2:
            atributos2.remove('concept:name')
            atributos2.insert(0, 'concept:name')


        columnas_a_eliminar = ['case:concept:name', 'time:timestamp']

        for col in columnas_a_eliminar:
            atributos2.remove(col)
            atributos.remove(col)

        
        col1, col2, col3, col4 = st.columns(4)

        
        
        if "nodes" not in ss:
            ss["nodes"] = None

        ss["nodes"] = col1.selectbox(
                'Nodes',
                (atributos2), 
                index=atributos2.index(st.session_state["nodes"]) if st.session_state["nodes"] in atributos2 else 0)
        
        nodes = ss["nodes"]


        if "metric" not in ss:
            ss["metric"] = None

        lista_metricas = ['Absolute Frequency', 'Case Frequency', 'Max Repetitions', 
                'Total Repetitions', 'Mean CT',  'Median CT', 'StDev CT', 'Total CT']
        ss["metric"] = col2.selectbox(
                'Metric',
                (lista_metricas), 
                index=lista_metricas.index(st.session_state["metric"]) if st.session_state["metric"] in lista_metricas else 0)
        
        metric = ss["metric"]

        if "perc_act" not in st.session_state:
            st.session_state["perc_act"] = 0

        perc_act = col3.slider('Activity threshold', min_value=0, max_value=100, value=st.session_state.get("perc_act", 0))
        st.session_state["perc_act"] = perc_act



        if "perc_path" not in st.session_state:
            st.session_state["perc_path"] = 0

        perc_path = col4.slider('Path threshold', min_value=0, max_value=100, value=st.session_state.get("perc_path", 0))
        st.session_state["perc_path"] = perc_path

        

        cont = 0

        

        if "n_filter" not in ss:
            ss["n_filter"] = 0

        ss["n_filter"] = st.sidebar.number_input('Number of manipulation actions', step=1, min_value=0, value=ss['n_filter'])
        n = ss["n_filter"] 
        filtered = pd.DataFrame()
        original = dataframe


        if(n==0):
            filtered={}
            filtered['Initial'] = dataframe

        else:
            while (cont < n):
                try:
    
                    filtered = manipulation(dataframe, original, cont)
                except Exception as e:
                    st.error(f"Error")
                    break

                # filtered = manipulation(dataframe, original, cont)
                dataframe = filtered
                cont = cont+1

        # st.sidebar.write('2) Datos manipulados')

        if st.button('Generate collection of DFGs'):

            st.markdown("""---""")
            # t = time.process_time()
            if (filtered == {}):
                st.error('No results (no event log subset matches the specified manipulation actions).')
            dfgs = df_to_dfg(filtered,nodes,metric)
                # elapsed_time = time.process_time() - t
                # st.write('df_to_dfg: ' + str(elapsed_time/60) + ' minutos')
                
            st.session_state.dataframe = dfgs
            copia_dict = copy.deepcopy(dfgs)

                # t = time.process_time()
            threshold(copia_dict, metric, perc_act, perc_path, nodes)
                # elapsed_time = time.process_time() - t
                # st.write('threshold: ' + str(elapsed_time/60) + ' minutos')   


            # try:
            #     st.markdown("""---""")
            
            #     # t = time.process_time()
            #     if (filtered == {}):
            #         st.error('No results (no event log subset matches the specified manipulation actions).')
            #     dfgs = df_to_dfg(filtered,nodes,metric)
            #     # elapsed_time = time.process_time() - t
            #     # st.write('df_to_dfg: ' + str(elapsed_time/60) + ' minutos')
                
            #     st.session_state.dataframe = dfgs
            #     copia_dict = copy.deepcopy(dfgs)

            #     # t = time.process_time()
            #     threshold(copia_dict, metric, perc_act, perc_path, nodes)
            #     # elapsed_time = time.process_time() - t
            #     # st.write('threshold: ' + str(elapsed_time/60) + ' minutos')

            # except Exception as e:
            #     # Mostrar un mensaje genérico al usuario en la interfaz de Streamlit
            #     st.error("Error")
            #     # Aquí puedes registrar el error detallado para depuración, si lo necesitas
            #     print(f"Error capturado: {str(e)}")


            
        





    
