import streamlit as st
import numpy as np
import pandas as pd
import pm4py
import copy
import deprecation
import os
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
import warnings
warnings.filterwarnings("ignore")
import time
from datetime import datetime
from PIL import Image
from io import StringIO
from pm4py.visualization.dfg.variants.frequency import apply
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from streamlit import session_state as ss


st.set_page_config(page_title="Main page")

pd.set_option("styler.render.max_elements", 2000000)


# st.markdown("# Main page 🎈")
# st.sidebar.markdown("# Main page 🎈")


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

if "grupo" not in st.session_state:
    st.session_state["grupo"] = {}

if "values" not in st.session_state:
        st.session_state["values"] = {}

if "act1" not in st.session_state:
        st.session_state["act1"] = {}

if "act2" not in st.session_state:
        st.session_state["act2"] = {}

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


# Manipulation  
def manipulation(df, original, i): 
    # log = check_log(df)

    ft_group = st.sidebar.selectbox('Filter type', ('Attribute', 'Performance', 'Follower', 'Timeframe', 'Rework', 'Endpoints'),
         key='ft_group_%s' % i)

    st.session_state["filter_type_group"]['ft_group_%s' % i] = ft_group

    filters1 = ("Mandatory", "Forbidden", "Keep Selected")

    filters2 = ('Path performance', "Case performance")

    filters3 = ("Directly Followed", "Eventually Followed", "Keep Selected Fragments")

    # filters = ("Mandatory", "Forbidden", "Keep Selected", 
    #        "Directly Followed", "Eventually Followed", "Keep Selected Fragments", 
    #        'Timeframe','Path performance', "Case performance", 'Endpoints', 'Rework')

    if(ft_group == 'Attribute'):
        ft = st.sidebar.selectbox('Filter mode', 
            filters1,  index=filters1.index(st.session_state["filter_types"].get('ft_%s' % i, filters1[0])), key='ft_%s' % i)
    
        # default_value = st.session_state["filter_types"].get('ft_%s' % i, filters1[0])
        # # Asegurarse de que el valor predeterminado esté en filters1
        # if default_value not in filters1:
        #     default_value = filters1[0]

        # ft = st.sidebar.selectbox('Filter mode', filters1, index=filters1.index(default_value), key='ft_%s' % i)
        # st.session_state["filter_types"]['ft_%s' % i] = ft

    elif(ft_group == 'Performance'):
        ft = st.sidebar.selectbox('Filter mode', 
            filters2,  index=filters2.index(st.session_state["filter_types"].get('ft_%s' % i, filters2[0])), key='ft_%s' % i)
    
    elif(ft_group == 'Follower'):
        ft = st.sidebar.selectbox('Filter mode', 
            filters3,  index=filters3.index(st.session_state["filter_types"].get('ft_%s' % i, filters3[0])), key='ft_%s' % i)

    else:
        ft = ft_group
    
    
    # ft = st.sidebar.selectbox('Filter type', 
    #         filters,  index=filters.index(st.session_state["filter_types"].get('ft_%s' % i, filters[0])), key='ft_%s' % i)

    st.session_state["filter_types"]['ft_%s' % i] = ft


    # Texto pequeño
    def small_text(text):
        return f"<p style='font-size:11px; color:{'grey'}; font-style:{'italic'}; '>{text}</p>"
    
    
    if(ft in ("Mandatory", "Forbidden", "Keep Selected")):
        if(ft == 'Mandatory'):
            st.sidebar.markdown(small_text("This filter removes all cases that do not have at least one event with one of the selected values."), unsafe_allow_html=True)
        elif(ft == 'Forbidden'):
            st.sidebar.markdown(small_text("This filter removes all cases that have at least one event with one of the selected values."), unsafe_allow_html=True)
        else:
            st.sidebar.markdown(small_text("This filter removes all events that do not have one of the selected values."), unsafe_allow_html=True)


        at = st.sidebar.selectbox('Attribute',
                    (original.columns), 
                    index=original.columns.get_loc(st.session_state["attribute"].get('at_%s' % i, original.columns[0])), 
                    key='at_%s' % i)

        g = st.sidebar.checkbox('Group by', key='g_%s' % i)
        st.session_state["grupo"]['g_%s' % i] = g

        st.session_state["attribute"]['at_%s' % i] = at
                
        valores = original[at].unique()
              
        # value = st.sidebar.multiselect('Value', (['*'] + list(valores) ), key='value_%s' % i)
        value = st.sidebar.multiselect('Value', (['*'] + list(valores)), key='value_%s' % i, default=st.session_state["values"].get('value_%s' % i, []))
        st.session_state["values"]['value_%s' % i] = value

        manip = [ft,(at,g),value]

        

    elif(ft == "Path performance"):
        act1 = st.sidebar.selectbox(
                    'From', (original['concept:name'].unique()), 
                    index=original['concept:name'].unique().tolist().index(st.session_state["act1"].get('act1_%s' % i, original['concept:name'].unique()[0])), 
                    key='act1_%s' % i)
        st.session_state["act1"]['act1_%s' % i] = act1

        act2 = st.sidebar.selectbox(
                    'To', (original['concept:name'].unique()), 
                    index=original['concept:name'].unique().tolist().index(st.session_state["act2"].get('act2_%s' % i, original['concept:name'].unique()[0])), 
                key='act2_%s' % i)
        st.session_state["act2"]['act2_%s' % i] = act2

        rango = st.sidebar.slider("Minutes between them:", 1, 500, key='rang_%s' % i, 
        value=st.session_state["rango"].get('rang_%s' % i, (25, 75)))
        st.session_state["rango"]['rang_%s' % i] = rango

        manip = [ft,(act1,act2),rango]

    elif(ft == "Endpoints"):
        st.sidebar.markdown(small_text("This filter removes all cases in which the first and/or last events do not have one of the selected values."), unsafe_allow_html=True)
        
        options = ['*'] + list(pm4py.get_start_activities(df))
        st.write(options)

        default_values = st.session_state["act1"].get('act1_%s' % i, [])
        valid_defaults = [val for val in default_values if val in options]

        act1 = st.sidebar.multiselect('From', (options), key='act1_%s' % i, default=valid_defaults)
        st.session_state["act1"]['act1_%s' % i] = act1

        options2 = ['*'] + list(pm4py.get_end_activities(df))
        st.write(options2)

        default_values2 = st.session_state["act2"].get('act2_%s' % i, [])
        valid_defaults2 = [val for val in default_values2 if val in options2]

        act2 = st.sidebar.multiselect('To', (options2), key='act2_%s' % i,
                default=valid_defaults2)
        st.session_state["act2"]['act2_%s' % i] = act2
        manip = [ft,act1,act2]

    elif(ft == 'Rework'):
        act1 = st.sidebar.selectbox('Activity', (df['concept:name'].unique() ), 
                index=df['concept:name'].unique().tolist().index(st.session_state["act1"].get('act1_%s' % i, df['concept:name'].unique()[0])), 
                key='act1_%s' % i)
        st.session_state["act1"]['act1_%s' % i] = act1

        value = st.sidebar.number_input('Minimum frequency', step=1, key='value_%s' % i,
            value=st.session_state["number_values"].get('value_%s' % i, 0))
        st.session_state["number_values"]['value_%s' % i] = value
        manip = [ft,act1,value]

    elif(ft == 'Case performance'):
        j = 2
        # ft = st.sidebar.selectbox('Filter type', 
            # filters, index=filters.index(st.session_state["filter_types"].get('ft_%s' % i, filters[0])), key='ft_%s' % i)
        mode_options = ["Unique interval", "More than one interval"]
        mode = st.sidebar.selectbox("Mode", 
            mode_options, index=mode_options.index(st.session_state["modes"].get(f'mode_{i}', mode_options[0])), key=f'mode_{i}')
        st.session_state["modes"][f'mode_{i}'] = mode
        if(mode == "Unique interval"):
            rango = st.sidebar.slider("Minutes between them:", 1, 500, key='rang_%s' % i, value=st.session_state["range_values"].get(f'rang_{i}', (25, 75)))
            st.session_state["range_values"][f'rang_{i}'] = rango
        else:
            n = st.sidebar.number_input('Number of intervals', step=1, min_value=2, key='nrange_%s' % i, value=st.session_state["nrange"].get(f'nrange_{i}', 2))
            st.session_state["nrange"][f'nrange_{i}'] = n
            rango = []
            for j in range(n):
                r1 = st.sidebar.slider("Minutes between the interval " + str(j+1) + ":", 1, 500, key='rang2_%s' % j, 
                        value=st.session_state["rango2"].get(f'rang2_{j}', (25, 75)))
                rango.append(r1)
                st.session_state["rango2"][f'rang2_{j}'] = r1
        
        manip = [ft,mode, rango]
    
    elif(ft == 'Timeframe'):
        mode_time = ['contained', 'intersecting', 'events']
        mode = st.sidebar.selectbox('Mode', (mode_time), key='mode_%s' % i,
            index=mode_time.index(st.session_state["modes"].get(f'mode_{i}', mode_time[0])))
        r, l = st.sidebar.columns(2)

        rango1 = r.date_input("From", key='date1_%s' % i, 
                value=st.session_state["input_values"].get('date1_%s' % i, original['time:timestamp'][0]))
        h1 = l.time_input('', key='hour1_%s' % i,
                value=st.session_state["input_values"].get('hour1_%s' % i, datetime.now().time()))
        start_datetime = datetime.combine(rango1, h1)


        rango2 = r.date_input("To", key='date2_%s' % i,
                value=st.session_state["input_values"].get('date2_%s' % i, original['time:timestamp'][0]))
        h2 = l.time_input('', key='hour2_%s' % i,
                value=st.session_state["input_values"].get('hour2_%s' % i, datetime.now().time()))
        end_datetime = datetime.combine(rango2, h2)

        manip = [ft,mode,(start_datetime,end_datetime)]

    else:
        act1 = st.sidebar.selectbox(
                    'From', (original['concept:name'].unique()), 
                    index=original['concept:name'].unique().tolist().index(st.session_state["act1"].get('act1_%s' % i, original['concept:name'].unique()[0])), 
                    key='act1_%s' % i)
        st.session_state["act1"]['act1_%s' % i] = act1

        act2 = st.sidebar.selectbox(
                    'To', (original['concept:name'].unique()), 
                    index=original['concept:name'].unique().tolist().index(st.session_state["act2"].get('act2_%s' % i, original['concept:name'].unique()[0])), 
                key='act2_%s' % i)
        st.session_state["act2"]['act2_%s' % i] = act2

        manip = [ft,act1,act2]

   
    st.sidebar.markdown("""---""")

    filtered_dataframe={}
    
    dfs={}

    if not isinstance(df, dict):
        dfs['']=df
    else:
        dfs=df 

    ftype = manip[0]
    v1 = manip[1]
    v2 = manip[2]

    for key, df in dfs.items():

        if (ftype == 'Directly Followed'):
            activityFROM = v1 
            activityTO = v2
            filt = pm4py.filter_directly_follows_relation(df, 
                [(activityFROM,activityTO)], activity_key='concept:name', 
                        case_id_key='case:concept:name', timestamp_key='time:timestamp')
                # if(key != ''):
                #     z_value=key
            if(len(filt)!=0):
                if(key==''):
                    filtered_dataframe[str(v1) + " - " + str(v2)] = filt
                else:
                    filtered_dataframe[key + " ; " + str(v1) + " - " + str(v2)] = filt
                    
        elif(ftype == 'Eventually Followed'):
            activityFROM = v1 
            activityTO = v2
            filt = pm4py.filter_eventually_follows_relation(df, 
                                [(activityFROM,activityTO)], activity_key='concept:name', 
                                case_id_key='case:concept:name', timestamp_key='time:timestamp')
                # if(key != ''):
                #     z_value=key
            if(len(filt)!=0):
                if(key==""):
                    filtered_dataframe[str(v1) + " - " + str(v2)] = filt
                else:
                    filtered_dataframe[key + " ; " + str(v1) + " - " + str(v2)] = filt
                    

        elif ftype == "Keep Selected Fragment":
            #             z_value='{'+z_value+'}'
            #             z_value=json.loads(z_value)
            grupo = pm4py.filter_between(df, v1, v2, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')
            #             if(key != ''):
            #                 z_value=key
            if(len(grupo)!=0):
                if(key==""):
                    filtered_dataframe[str(v1) + " - " + str(v2)] = grupo
                else:
                    filtered_dataframe[key + " ; " + str(v1) + " - " + str(v2)] = grupo
                

        elif ftype == 'Mandatory':
            g = v1[1]
            v1 = v1[0] 
            if v2 == ['*']: 
                valores = df[v1].unique()
                for v in valores:
                    grupo = pm4py.filter_trace_attribute_values(df, v1, [v])
                    if(len(grupo)!=0):
                        filtered_dataframe[v] = grupo
            else:    
                # st.write(v1)
                if(g==True):
                    # st.write('prueba')
                    for v in v2:
                        grupo = pm4py.filter_trace_attribute_values(df, v1, [v])
                        if(len(grupo)!=0):
                            filtered_dataframe[v] = grupo
                # st.write(v1, v2)
                else:
                    grupo = pm4py.filter_trace_attribute_values(df, v1, v2)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str(v2)] = grupo
                        else:
                            filtered_dataframe[key + " ; " + str(v2)] = grupo
                        

        elif ftype == 'Keep Selected':
            g = v1[1]
            v1 = v1[0] 
            
            if v2 == ['*']:  
                valores = df[v1].unique()
                for v in valores:
                    grupo = df[df[v1]==v]
                    if(len(grupo)!=0):
                        filtered_dataframe[v] = grupo
            else:   
                if(g==True):
                    valores = df[v1].unique()
                    for v in v2:
                        grupo = df[df[v1]==v]
                        if(len(grupo)!=0):
                            filtered_dataframe[v] = grupo
                else:                    
                    grupo = pm4py.filter_event_attribute_values(df, v1, v2,  level='event')
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str(v2)] = grupo
                        else:
                            filtered_dataframe[key + " ; " + str(v2)] = grupo

        elif ftype == 'Forbidden':   
            g = v1[1] 
            v1 = v1[0] 
            
            if v2 == ['*']: 
                valores = df[v1].unique()
                for v in valores:
                    grupo = pm4py.filter_trace_attribute_values(df, v1, [v], retain=False)
                    if(len(grupo)!=0):
                        filtered_dataframe[v] = grupo
            else:       
                if(g==True):
                    # st.write('prueba')
                    for v in v2:
                        grupo = pm4py.filter_trace_attribute_values(df, v1, [v], retain=False)
                        if(len(grupo)!=0):
                            filtered_dataframe[v] = grupo
                # st.write(v1, v2)
                else:
                    grupo = pm4py.filter_trace_attribute_values(df, v1, v2, retain=False)
                    if(len(grupo)!=0):
                        if(key==""):
                            filtered_dataframe[str(v2)] = grupo
                        else:
                            filtered_dataframe[key + " ; " + str(v2)] = grupo

        elif ftype == 'Rework':
            # log = check_log(df)
            grupo = pm4py.filter_activities_rework(df, v1, v2)
            # grupo = pm4py.convert_to_dataframe(filtered_log)
            if(len(grupo)!=0):
                filtered_dataframe[v1 + ': ' + str(v2)] = grupo

        elif ftype == 'Endpoints':
            # log = check_log(df)
            log_start = pm4py.get_start_activities(df)
            log_end = pm4py.get_end_activities(df)

            if (v1 == ['*'] and v2 == []):
                for a in log_start:
                    grupo = pm4py.filter_start_activities(df, [a])
                    # grupo = pm4py.convert_to_dataframe(filtered_log)
                    if(len(grupo)!=0):
                        filtered_dataframe[a + ' - ' + 'endpoints'] = grupo

            elif (v1 == ['*'] and v2 == ['*']):
                for a in log_start:
                    for e in log_end:
                        filtered_log = pm4py.filter_start_activities(df, [a])
                        grupo = pm4py.filter_end_activities(filtered_log, [e])
                        # grupo = pm4py.convert_to_dataframe(filtered_log)
                        if(len(grupo)!=0):
                            filtered_dataframe[a + ' - ' + e] = grupo
            
            elif (v1 == ['*'] and v2 != []):
                for a in log_start:
                    filtered_log = pm4py.filter_start_activities(df, [a])
                    grupo = pm4py.filter_end_activities(filtered_log, v2)
                    # grupo = pm4py.convert_to_dataframe(filtered_log)
                    if(len(grupo)!=0):
                        filtered_dataframe[a + ' - ' + str(v2)] = grupo

            elif (v1 != [] and v2 == ['*']):
                for e in log_end:
                    filtered_log = pm4py.filter_end_activities(df, [e])
                    grupo = pm4py.filter_start_activities(filtered_log, v1)
                    # grupo = pm4py.convert_to_dataframe(filtered_log1)
                    if(len(grupo)!=0):
                        filtered_dataframe[str(v1) + ' - ' + e] = grupo

            elif (v1 == [] and v2 == ['*']):
                for e in log_end:
                    grupo = pm4py.filter_end_activities(df, [e])
                    # grupo = pm4py.convert_to_dataframe(filtered_log)
                    if(len(grupo)!=0):
                        filtered_dataframe['startpoints' + ' - ' + e] = grupo
            
            elif (v1 != [] and v2 != []):
                filtered_log = pm4py.filter_start_activities(df, v1)
                grupo = pm4py.filter_end_activities(filtered_log, v2)
                # grupo = pm4py.convert_to_dataframe(filtered_log)
                if(len(grupo)!=0):
                    # st.write(a)
                    filtered_dataframe[str(v1) + ' - ' + str(v2)] = grupo

            
            elif (v1 == [] and v2 != []):
                grupo = pm4py.filter_end_activities(df, v2)
                # grupo = pm4py.convert_to_dataframe(filtered_log)
                if(len(grupo)!=0):
                    filtered_dataframe['startpoints -' + str(v2)] = grupo

            elif (v1 != [] and v2 == []):
                grupo = pm4py.filter_start_activities(df, v1)
                # grupo = pm4py.convert_to_dataframe(filtered_log)
                if(len(grupo)!=0):
                    filtered_dataframe['selected startpoints -  endpoints'] = grupo

            else:
                filtered_dataframe[str(v1) + ' - endpoints'] = df

        elif ftype == 'Path performance':
            # log = check_log(df)
            grupo = pm4py.filter_paths_performance(df, v1, v2[0]*60, v2[1]*60)
            # grupo = pm4py.convert_to_dataframe(filtered_log)
            if(len(grupo)!=0):
                    filtered_dataframe[str(v1)] = grupo
        
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
                    filtered_dataframe[str(v2[0]) + ' - ' + str(v2[1])] = grupo

        elif ftype == 'Case performance':
            
            # log = check_log(df)
            if(v1=="Unique interval"):
                grupo = pm4py.filter_case_performance(df, v2[0]*60, v2[1]*60)
                # grupo = pm4py.convert_to_dataframe(filtered_log)
                if(len(grupo)!=0):
                    filtered_dataframe[v2] = grupo
            else:
                j=0
                for j in rango:
                    # st.write(j, rango)
                    grupo = pm4py.filter_case_performance(df, j[0]*60, j[1]*60)
                    # grupo = pm4py.convert_to_dataframe(filtered_log)
                    if(len(grupo)!=0):
                        filtered_dataframe[j] = grupo
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
        st.write('4.1) returnEdgesInfo hecho')

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
            pm4py.save_vis_performance_dfg(dfg['dfg'],dfg['sa'],dfg['ea'], './figures/dfg' + str(ident) + '.png', aggregation_measure=measure)
            
            st.write(str(key))
            st.image('./figures/dfg' + str(ident) + '.png')
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

            dfg_visualizer.save(gviz, './figures/dfg' + str(ident) + '.png')

            st.write(str(key))
            st.image( './figures/dfg' + str(ident) + '.png')
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

        columnas_a_eliminar = ['case:concept:name', 'time:timestamp']

        for col in columnas_a_eliminar:
            atributos.remove(col)

        
        col1, col2, col3, col4 = st.columns(4)

        
        
        if "nodes" not in ss:
            ss["nodes"] = None

        ss["nodes"] = col1.selectbox(
                'Nodes',
                (atributos), 
                index=atributos.index(st.session_state["nodes"]) if st.session_state["nodes"] in atributos else 0)
        
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
                    st.error(f"Error: {e}")
                    raise

                # filtered = manipulation(dataframe, original, cont)
                dataframe = filtered
                cont = cont+1

        # st.sidebar.write('2) Datos manipulados')

        if st.button('Show DFGs collection'):
            st.markdown("""---""")
            
            # t = time.process_time()
            dfgs = df_to_dfg(filtered,nodes,metric)
            # elapsed_time = time.process_time() - t
            # st.write('df_to_dfg: ' + str(elapsed_time/60) + ' minutos')
            
            st.session_state.dataframe = dfgs
            copia_dict = copy.deepcopy(dfgs)

            # t = time.process_time()
            threshold(copia_dict, metric, perc_act, perc_path, nodes)
            # elapsed_time = time.process_time() - t
            # st.write('threshold: ' + str(elapsed_time/60) + ' minutos')
        





    