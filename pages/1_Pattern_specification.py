import streamlit as st
import numpy as np
import pandas as pd
import pm4py
import copy
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
import heapq
from pm4py.statistics.rework.cases.log import get as rework_cases
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.statistics.rework.cases.log import get as rework_cases
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.attributes import attributes_filter
import json
import re
import datetime
from pm4py.visualization.dfg.variants.frequency import apply
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
from PIL import Image
from io import StringIO
from pm4py.visualization.dfg.variants.frequency import apply
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from collections import Counter
from itertools import combinations

st.set_page_config(page_title="Pattern specification")

maxt = 0

# st.markdown("# Pattern specification ❄️")
# st.sidebar.markdown("# Pattern specification ❄️")

# st.write("DataFrame manipulado en la página 1:")


def search(expr, param, dic, inicial, measure): 
    return function(dic,expr,param, inicial, measure)
    
def function(graph, expr, paramF, inicial, measure):
    if(expr == 'percentageReworkActivityPerEvents'):
        return percentageReworkPerActivityEventsDFG(graph)
    elif(expr== 'percentageReworkPerActivity'):
        return percentageReworkPerActivityDFG(graph)

    elif(expr == 'Identify DFGs by the number of unique nodes'):
        return uniqueActivitiesDFG(graph, paramF)

    elif (expr == 'Identify DFGs by the number of unique resources'):
        return uniqueActivitiesDFG(graph, paramF)
    
    elif(expr == 'Identify infrequent activities'):
        return infreqact(graph, paramF, measure)
    
    elif(expr == 'Identify the most frequent activities'):
        return mostfreqact(graph, paramF, measure)

    elif(expr == 'Identify the most frequent fragment'):
        return mostfreqfrag(graph, param)

    elif(expr == 'Identify transitions with high duration'):
        return transduration(graph, paramF, measure)

    elif(expr == 'Identify activities with high duration'):
        # if(comprobar si es posible calcularlo):
            # return actduration(graph, paramF, measure)
        # else:
        st.markdown(" **Note: The duration associated with the transitions is used for this calculation.** ")
        return transduration(graph, paramF, measure)

    elif(expr == 'Identify transitions as bottlenecks'):
        return transbot(graph, paramF, inicial, measure)

    elif(expr == 'Identify activities as bottlenecks'):
        # if(comprobar si es posible calcularlo):
            # rreturn actbot(graph, paramF, inicial, measure)
        # else:
        st.markdown(" **Note: The duration associated with the transitions is used for this calculation.** ")
        return transbot(graph, paramF, inicial, measure)

    elif(expr == 'Identify resources with high workload'):
        return mostfreqresour(graph, paramF, measure)

    elif(expr == 'Identify resources as bottlenecks'):
        return resourbot(graph, paramF, inicial, measure)

    



def uniqueActivitiesDFG(dic, param):
    # st.write('n nodos de cada grafo', len(graph.nodes))
    prueba = {}

    min_nodos = min(len(datos['graph'].nodes) for datos in dic.values())
    max_nodos = max(len(datos['graph'].nodes) for datos in dic.values())

    for key, datos in dic.items():
        graph = datos['graph']

        if param == 'Minimum number of nodes':
            if len(graph.nodes) <= min_nodos:
                prueba[key] = datos
                st.markdown(f" **(Min. nodes: {min_nodos})**")

        elif param == 'Maximum number of nodes':
            if len(graph.nodes) >= max_nodos:
                st.markdown(f" **(Max. nodes: {max_nodos})**")
                prueba[key] = datos
        else:
            if(len(graph.nodes) >= param):
                prueba[key] = datos

    return prueba

def infreqact(dic, param, measure):
    # Obtener todos los datos de todos los grafos
    all_data = []
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        all_data.extend([valor[measure] for nombre, valor in data])

    # Calcular el promedio general de la medida
    promedio_abs_freq = sum(all_data) / len(all_data)

    # Filtrar los datos según el parámetro y el promedio general
    prueba = {}
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        
        if param == 'Mean frequency':
            res = [(nombre, valor) for nombre, valor in data if valor[measure] < promedio_abs_freq]
        elif param == 'Less than 10 (frequency)':
            res = [(nombre, valor) for nombre, valor in data if valor[measure] <= 10]  
        else:
            res = [(nombre, valor) for nombre, valor in data if valor[measure] <= param]
        
        if len(res) > 0:
            prueba[key] = datos 

    return prueba

def mostfreqact(dic, param, measure):
    # Obtener todos los datos de todos los grafos
    all_data = []
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        all_data.extend([valor[measure] for nombre, valor in data])

    # Calcular el promedio general de la medida
    promedio_abs_freq = sum(all_data) / len(all_data)

    # Filtrar los datos según el parámetro y el promedio general
    prueba = {}
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        
        if param == 'Mean frequency':
            res = [(nombre, valor) for nombre, valor in data if valor[measure] > promedio_abs_freq]
        elif param == 'More than 10 (frequency)':
            res = [(nombre, valor) for nombre, valor in data if valor[measure] >= 10]  
        else:
            res = [(nombre, valor) for nombre, valor in data if valor[measure] >= param]
        
        if len(res) > 0:
            prueba[key] = datos 

    return prueba

# def mostfreqfrag(dic, inicial):
    
    
#     for key, datos in dic.items():
#         st.write(datos)
#         dataframe = datos['df']
        
    

def transduration(dic, param, measure):
    # Obtener todos los datos de todas las transiciones
    all_data = []
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.edges.data()
        all_data.extend([edge[2][measure] for edge in data])

    # Calcular el promedio general de la duración de las transiciones
    promedio = sum(all_data) / len(all_data)
    # st.write(promedio)

    # Filtrar las transiciones según el parámetro y el promedio general
    prueba = {}
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.edges.data()
        
        if (param == 'Mean cycle time of transitions' or param == 'Mean cycle time of activities') :
            res = [edge for edge in data if edge[2][measure] > promedio] 
        else:
            res = [edge for edge in data if edge[2][measure] > param * 60]
    
        if len(res) > 0:
            prueba[key] = datos 

    return prueba

def actduration(dic, param):

    all_data = []
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        all_data.extend([edge[2][measure] for edge in data])

    # Calcular el promedio general de la duración de las transiciones
    promedio = sum(all_data) / len(all_data)
    # st.write(promedio)

    # Filtrar las transiciones según el parámetro y el promedio general
    prueba = {}
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        
        if param == 'Mean cycle time of transitions':
            res = [edge for edge in data if edge[2][measure] > promedio] 
        else:
            res = [edge for edge in data if edge[2][measure] > param * 60]
    
        if len(res) > 0:
            prueba[key] = datos 

    return prueba

def transbot(dic, param, inicial, measure):

    # dfg, sa, ea = pm4py.discover_dfg(inicial, activity_key=nodes)
    prueba = {}
    maximo = 0
    maximos=[]
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.edges.data()
        max2 = heapq.nlargest(3, (item[2][measure] for item in data))
        maximos.extend(max2)
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.edges.data()
        lista_max = sorted(maximos, reverse=True)
        if(param=='Transition with the maximum duration' or param=='Activity with the maximum duration'):
            valores_mas_altos = lista_max[0]
            res = [edge for edge in data if edge[2][measure] >= valores_mas_altos] 
        else: 
            valores_mas_altos = lista_max[:param] 
            res = [edge for edge in data if edge[2][measure] >= min(valores_mas_altos)]
        if(len(res)>0):
            prueba[key] = datos 
    
    return prueba

def actbot(dic, param, inicial, measure):
    dfg, sa, ea = pm4py.discover_dfg(inicial, activity_key=nodes)
    prueba = {}
    maximo = 0
    maximos=[]
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        max2 = heapq.nlargest(3, (item[2][measure] for item in data))
        maximos.extend(max2)
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        lista_max = sorted(maximos, reverse=True)
        if(param=='Transition with the maximum duration'):
            valores_mas_altos = lista_max[0]
            res = [edge for edge in data if edge[2][measure] >= valores_mas_altos] 
        else: 
            valores_mas_altos = lista_max[:param] 
            res = [edge for edge in data if edge[2][measure] >= min(valores_mas_altos)]
        if(len(res)>0):
            prueba[key] = datos 
    
    return prueba

def mostfreqresour(dic, param, measure):
    # Obtener todos los datos de todos los grafos
    all_data = []
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        all_data.extend([valor[measure] for nombre, valor in data])

    # Calcular el promedio general de la medida
    promedio_abs_freq = sum(all_data) / len(all_data)

    # Filtrar los datos según el parámetro y el promedio general
    prueba = {}
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        
        if(param == 'Mean frequency'):
            res = [(nombre, valor) for nombre, valor in data if valor[measure] > promedio_abs_freq]
        else:
            res = [(nombre, valor) for nombre, valor in data if valor[measure] >= param]
        
        if len(res) > 0:
            prueba[key] = datos 

    return prueba


def resourbot(dic, param, inicial, measure):
    dfg, sa, ea = pm4py.discover_dfg(inicial, activity_key=nodes)
    prueba = {}
    maximo = 0
    maximos=[]
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.edges.data()
        max2 = heapq.nlargest(3, (item[2][measure] for item in data))
        maximos.extend(max2)
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.edges.data()
        lista_max = sorted(maximos, reverse=True)
        if(param=='Maximum CT of resources'):
            valores_mas_altos = lista_max[0]
            res = [edge for edge in data if edge[2][measure] >= valores_mas_altos] 
        else: 
            valores_mas_altos = lista_max[:param] 
            res = [edge for edge in data if edge[2][measure] >= min(valores_mas_altos)]
        if(len(res)>0):
            prueba[key] = datos 
    
    return prueba

         

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

def returnEdgesInfo(df,concept_name,case_concept_name,timestamp):
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
    max_rep=returnMaxRepititionsEdges(df_edges)
    case_freq=returnCaseFreqEdges(df_edges)
    total_rep = returnTotalRepetitions(df_edges)

    return max_rep,case_freq, total_rep

def returnTotalRepetitions(df):
    totalRep=df.groupby("Transitions").apply(lambda x: (x['case_ids'].value_counts() > 1).sum())
    return totalRep

def returnCaseFreqEdges(df):
    case_freq=df.groupby('Transitions')['case_ids'].nunique()
    return case_freq

def returnMaxRepititionsEdges(df):
    maxRep=df.groupby(["case_ids","Transitions"]).apply(lambda x: len(x)).reset_index().groupby("Transitions").apply(lambda x: max(x[0]))
    return maxRep

def check_log(data):
    if (type(data) != pm4py.objects.log.obj.EventLog):
        data = log_converter.apply(data)
    return data


dic = {}
datos = {}

if 'dataframe' not in st.session_state:
    st.session_state.dataframe = pd.DataFrame()

if len(st.session_state.dataframe):
# if st.session_state.dataframe is not None:
    dic = st.session_state.dataframe
    # st.write(st.session_state.datos)

    if 'metric' not in st.session_state:
        metric = 'Mean CT'
    else:
    # if st.session_state.metric is not None:
        metric = st.session_state.metric

    if 'nodes' not in st.session_state:
        nodes = 'concept:name'
    else:
    # if st.session_state.nodes is not None:
        nodes = st.session_state.nodes

    # if st.session_state.inicial is not None:
    if 'inicial' not in st.session_state:
        st.session_state.inicial = pd.DataFrame()
    else:
        inicial = st.session_state.inicial

    left_column, right_column = st.columns(2)

    perc_act = st.sidebar.slider('Activity threshold')  

    perc_path = st.sidebar.slider('Path threshold')

    if (nodes == 'concept:name'):
        if metric in ['Mean CT', 'Median CT', 'StDev CT', 'Total CT']:  
            pattern = st.sidebar.selectbox(
                    'Pattern search',
                    ('Identify DFGs by the number of unique nodes', 
                    'Identify transitions with high duration',
                    'Identify activities with high duration',   # impememtado pero falta comprobar que existe tiempo asociado a actividades
                    'Identify transitions as bottlenecks',
                    'Identify activities as bottlenecks'))    # impememtado pero falta comprobar que existe tiempo asociado a actividades
                    # 'Identify activity loops as bottlenecks'))  # no implementado aun
        else:
            pattern = st.sidebar.selectbox(
                    'Pattern search',
                    # ('Identify the most frequent fragment',
                    ('Identify DFGs by the number of unique nodes',  
                    'Identify infrequent activities',
                    'Identify the most frequent activities'))

    elif(nodes == 'org:resource'):
        if metric in ['Mean CT', 'Median CT', 'StDev CT', 'Total CT']: 
            pattern = st.sidebar.selectbox(
                    'Pattern search',
                    ('Identify DFGs by the number of unique resources', 
                    'Identify resources as bottlenecks',
                    'Identify transitions as bottlenecks',
                    'Identify transitions with high duration'))
        else:
            pattern = st.sidebar.selectbox(
                    'Pattern search',
                    ('Identify DFGs by the number of unique resources', 
                    'Identify resources with high workload'))
    
    else:
        if metric in ['Mean CT', 'Median CT', 'StDev CT', 'Total CT']:  
            pattern = st.sidebar.selectbox(
                'Pattern search',
                ('Identify DFGs by the number of unique nodes', 
                'Identify transitions as bottlenecks',   
                'Identify transitions with high duration',
                'Identify activities with high duration',
                'Identify activities as bottlenecks',))   
        else:
            pattern = st.sidebar.selectbox(
                'Pattern search',
                ('Identify DFGs by the number of unique nodes',
                'Identify infrequent activities',
                'Identify the most frequent activities'))


    param = 0
    prueba = {}
    if(pattern == 'Identify DFGs by the number of unique nodes' or pattern == 'Identify DFGs by the number of unique resources'):
        param = st.sidebar.selectbox('Number of nodes', 
        ['Minimum number of nodes', "Maximum number of nodes", 'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('More than X nodes:', step=1, min_value=0)
        
    # elif (pattern == 'Identify activities with high duration'): #solo es posible si hay tiempo de inicio y fin de actividades
    #     param = st.sidebar.number_input('Minimum minutes to consider an activity with high duration', step=1) 

    elif (pattern == 'Identify infrequent activities'):
        param = st.sidebar.selectbox('Maximum frequency to consider an infrequent activity', 
        ['Mean frequency', "Less than 10 (frequency)", 'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('Maximum absolute frequency to consider an infrequent activity', step=1, min_value=0) 

    elif (pattern == 'Identify the most frequent activities'):
        param = st.sidebar.selectbox('Minimum threshold to consider the most frequent activities', 
        ['Mean frequency', "More than 10 (frequency)", 'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('Minimum absolute frequency to consider the most frequent activities', step=1, min_value=0) 

    elif (pattern == 'Identify the most frequent fragment'):
        param = st.sidebar.number_input('Number of activities of the fragment', step=1, min_value=3) 

    elif (pattern == 'Identify transitions with high duration'):
        param = st.sidebar.selectbox('Minimum minutes to consider a transition with high duration', 
        ['Mean cycle time of transitions',  'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('Minimum minutes to consider a transition with high duration', step=1, min_value=0)

    elif (pattern == 'Identify activities with high duration'):
        param = st.sidebar.selectbox('Minimum minutes to consider an activity with high duration', 
        ['Mean cycle time of activities',  'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('Minimum minutes to consider a activity with high duration', step=1, min_value=0)

    elif (pattern == 'Identify transitions as bottlenecks'):
        param = st.sidebar.selectbox('Number of transitions', 
        ['Transition with the maximum duration',  'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('Top-k transitions with the maximum duration', min_value=1,step=1)  

    elif(pattern == 'Identify resources with high workload'):
        param = st.sidebar.selectbox('Minimum threshold to consider resources with high workload', 
        ['Mean frequency', 'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('Minimum workload value (frequency)', step=1, min_value=1)

    elif (pattern == 'Identify activities as bottlenecks'):
        param = st.sidebar.selectbox('Number of activities', 
        ['Activity with the maximum duration',  'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('Top-k activities with the maximum duration', min_value=1,step=1) 

    elif (pattern == 'Identify activity loops as bottlenecks'):
        param = st.sidebar.number_input('Number of times an activity must occur to be considered bottleneck', step=1, min_value=0)
        # elif (pattern == 'Identify loops'):
        #     param = 
        # elif(pattern == 'Identify decision points'):
        #     param = 

    elif (pattern == 'Identify resources as bottlenecks'):
        param = st.sidebar.selectbox('Resources with the maximum duration', 
        ['Maximum CT of resources',  'Other'])
        if param == 'Other':
            param = st.sidebar.number_input('Top-k resources', min_value=1,step=1) 

    elif(pattern == 'Identify rework of activities'):
        param = st.sidebar.selectbox('Rework of activities', 
        ['Mean rework',  'Other value as maximum rework'])
        if param == 'Other value as maximum rework':
            param = st.sidebar.number_input('Maximum rework', min_value=1,step=1)      

    translater={"Absolute Frequency":"abs_freq","Case Frequency":"case_freq",
                    "Max Repetitions":"max_repetitions", "Total Repetitions":
                    "total_repetitions","Median CT":"median CT","Mean CT":"mean CT","StDev CT":"stdev","Total CT":"sum"}

    measure=translater[metric]


    if st.sidebar.button('Show DFGs collection'):
        selected = search(pattern, param, dic, inicial, measure)

        copia_dict = copy.deepcopy(selected)

        threshold(copia_dict, metric, perc_act, perc_path, nodes)
