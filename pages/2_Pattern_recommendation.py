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


st.set_page_config(page_title="Pattern recommendation")

# st.markdown("# Pattern recommendation 🎉")
# st.sidebar.markdown("# Pattern recommendation 🎉")

maxt = 0


def search(expr, dic, inicial): 

    # prueba = {}
    # for pattern in expr:

        # function(dic,pattern, inicial, prueba)
    # return prueba

    return function(dic,expr, inicial)
    
def function(graph, expr, inicial):
    # if(expr == 'percentageReworkActivityPerEvents'):
    #     return percentageReworkPerActivityEventsDFG(graph)
    # elif(expr== 'percentageReworkPerActivity'):
    #     return percentageReworkPerActivityDFG(graph)

    if(expr == 'Identify DFGs with the maximum number of unique activities'):
        return maxuniqueActivitiesDFG(expr, graph) 
    elif(expr == 'Identify DFGs with the minimum number of unique activities'):
        return minuniqueActivitiesDFG(expr, graph) 
    elif(expr == 'Identify infrequent activities'):
        return infreqact(expr, graph)
    elif(expr == 'Identify the most frequent activities'):
        return mostfreqact(expr, graph)
    elif(expr == 'Identify transitions as bottlenecks'):
        return transbot(expr, graph)


    elif(expr == 'Identify the most frequent fragment'):
        return mostfreqfrag(graph, inicial)

    elif(expr == 'Identify transitions with high duration'):
        return transduration(graph, paramF)

    elif(expr == 'Identify activities with high duration'):
        return actduration(graph, paramF)

    

    elif(expr == 'Identify activities as bottlenecks'):
        return actbot(graph, inicial, prueba)

    elif(expr == 'Identify resources with high workload'):
        return mostfreqact(expr, graph)

    elif(expr == 'Identify resources as bottlenecks'):
        return transbot(expr, graph)


# Hechos:

def minuniqueActivitiesDFG(expr, dic):

    prueba={}
    # max_nodos = max(len(datos['graph'].nodes) for datos in dic.values())
    min_nodos = min(len(datos['graph'].nodes) for datos in dic.values())

    st.markdown(f" **{expr}** **(Min. nodes: {min_nodos})**")

    for key, datos in dic.items():
        graph = datos['graph']
        # if len(graph.nodes) >= max_nodos:
        #     # key = 'Max. number of nodes (' + str(max_nodos) + ' nodes) - ' + key 
        #     prueba[key] = datos
        if len(graph.nodes) <= min_nodos:
            # key = 'Min. number of nodes (' + str(min_nodos) + ' nodes) - ' + key 
            prueba[key] = datos

    return prueba

def maxuniqueActivitiesDFG(expr, dic):

    prueba={}
    max_nodos = max(len(datos['graph'].nodes) for datos in dic.values())
    # min_nodos = min(len(datos['graph'].nodes) for datos in dic.values())

    st.markdown(f" **{expr}** **(Max. nodes: {max_nodos})**")

    for key, datos in dic.items():
        graph = datos['graph']
        if len(graph.nodes) >= max_nodos:
            # key = 'Max. number of nodes (' + str(max_nodos) + ' nodes) - ' + key 
            prueba[key] = datos
        # elif len(graph.nodes) <= min_nodos:
        #     # key = 'Min. number of nodes (' + str(min_nodos) + ' nodes) - ' + key 
        #     prueba[key] = datos

    return prueba

def infreqact(expr, dic):
    # st.write('hola')
    prueba={}
    min_values = []
    
    # Obtener los 3 valores más pequeños de todos los grafos
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        min_values.extend(heapq.nsmallest(1, (item[1]['max_repetitions'] for item in data)))
    
    # Ordenar los valores mínimos y tomar el menor de ellos
    min_values.sort()
    minimo = min_values[0]
    # st.write(minimo)
    st.markdown(f" **{expr}** **(Min. frequency: {minimo})**")
    # Encontrar las actividades menos frecuentes
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        
        # Filtrar los nodos que tienen una frecuencia menor o igual al mínimo
        res = [node for node in data if node[1]['max_repetitions'] <= minimo]
        
        if len(res) > 0:
            
            # key = 'Infreq. activities (min. freq. ' + str(minimo) + ') - ' + key 
            prueba[key] = datos 
    # st.write(prueba)
    return prueba
 
def mostfreqact(expr, dic):
    prueba={}
    maximo = 0
    maximos=[]
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        max2 = heapq.nlargest(1, (item[1]['max_repetitions'] for item in data))
        maximos.extend(max2)

    lista_max = sorted(maximos, reverse=True)
        
    valores_mas_altos = lista_max[0]
    
    st.markdown(f" **{expr}** **(Max. frequency: {valores_mas_altos})**")
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        
        res = [node for node in data if node[1]['max_repetitions'] >= valores_mas_altos] 
        
        if(len(res)>0):
            # key = 'Most freq. activities (max. freq. ' + str(valores_mas_altos) + ') - ' + key 
            prueba[key] = datos 

    return prueba

def transbot(expr, dic):
    prueba={}
    maximo = float('-inf')  # Inicializa el máximo con un valor muy pequeño
    grafos_maximos = []

    for key, datos in dic.items():
        graph = datos['graph']
       
        data = graph.edges.data()
        max2 = max(item[2]['mean CT'] for item in data)
        if max2 > maximo:
            
            maximo = max2
            grafos_maximos = [(key, datos)]   # Inicializa la lista con un solo elemento
        elif max2 == maximo:
            
            grafos_maximos.append((key, datos)) # Agrega el grafo actual a la lista
    m = maximo / 60
    

    st.markdown(f" **{expr}** **(Max. CT: {int(m)} minutes ~ {int(m/1440)} days)**")

    for i, (key, grafo) in enumerate(grafos_maximos, start=1):
        # nueva_clave = f"{key}_{i}"  # Construye una nueva clave única añadiendo un sufijo numérico
        prueba[key] = grafo

    return prueba





def mostfreqfrag(dic, inicial):
    
    # log = check_log(inicial)

    # filtered_log = pm4py.filter_variants_top_k(log, 1)


    # prueba = {}
    # frecuencias_subsecuencias = Counter()
    for key, datos in dic.items():
    #     st.write(datos)
        dataframe = datos['df']
        variants = pm4py.get_variants_as_tuples(dataframe, activity_key='concept:name', case_id_key='case:concept:name', timestamp_key='time:timestamp')

        st.write(variants)
    #     # st.write(dataframe['concept:name'].apply(list))
    #     filtered_log = pm4py.filter_variants_top_k(check_log(dataframe), 1)
    #     if(len(filtered_log)>0):
    #         prueba[key]=datos

    # return prueba

def actduration(dic, param):

    prueba = {}
    for key, datos in dic.items():
        
        graph = datos['graph']

        data = graph.nodes.data()
        # st.write(data)
        suma = sum(item[2]['mean CT'] for item in data)

        if(param=='Mean cycle time of transitions'):
            promedio =  suma / len(data)
            res = [node for node in data if node[2]['mean CT'] > promedio] 
        else:
            res = [node for node in data if node[2]['mean CT'] > param*60]
    
        if(len(res)>0):
            prueba[key] = datos 

    return prueba

def actbot(dic, param, inicial):
    dfg, sa, ea = pm4py.discover_dfg(inicial, activity_key=nodes)
    prueba = {}
    maximo = 0
    maximos=[]
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        max2 = heapq.nlargest(3, (item[2]['mean CT'] for item in data))
        maximos.extend(max2)
    for key, datos in dic.items():
        graph = datos['graph']
        data = graph.nodes.data()
        lista_max = sorted(maximos, reverse=True)
        if(param=='Maximum CT of activities'):
            valores_mas_altos = lista_max[0]
            res = [node for node in data if node[2]['mean CT'] >= valores_mas_altos] 
        else: 
            valores_mas_altos = lista_max[:param] 
            res = [node for node in data if node[2]['mean CT'] >= min(valores_mas_altos)]
        if(len(res)>0):
            prueba[key] = datos 
    
    return prueba




def numberOfEdges(graph):
    return len(graph.edges)

def meanNodes(graph):
    mean=sum([list(val.values())[0] for dict_val,val in dict(G.nodes.data()).items()])
    return mean

def meanNodes(graph):
    valores = []
    for tupla in list(graph.edges.data()):
        for valor in tupla[2].values():
            if isinstance(valor, (int, float)):
                valores.append(valor)
    mean = sum(valores) / len(valores)
    return mean

def meanEdges(graph):
    valores = []
    for tupla in list(graph.nodes.data()):
        for valor in tupla[2].values():
            if isinstance(valor, (int, float)):
                valores.append(valor)
    mean = sum(valores) / len(valores)
    return mean

def maxNode(graph):
    valores = []
    for tupla in list(graph.nodes.data()):
        for valor in tupla[2].values():
            if isinstance(valor, (int, float)):
                valores.append(valor)
    return max(valores)

def minNode(graph):
    valores = []
    for tupla in list(graph.nodes.data()):
        for valor in tupla[2].values():
            if isinstance(valor, (int, float)):
                valores.append(valor)
    return min(valores)

def maxEdge(graph):
    valores = []
    for tupla in list(graph.edges.data()):
        for valor in tupla[2].values():
            if isinstance(valor, (int, float)):
                valores.append(valor)
    return max(valores)

def minEdge(graph):
    valores = []
    for tupla in list(graph.edges.data()):
        for valor in tupla[2].values():
            if isinstance(valor, (int, float)):
                valores.append(valor)
    return min(valores)

def CTPorcTransitions(porc, graph1):   
    porc = int(porc)
    edges = graph1.edges.data()
    mean = graph1.graph['meanCTWholeProcess']
    umbral = (porc/100)*mean
    filtered_edges = [(edge[0], edge[1], edge[2]['mean CT']) for edge in edges if edge[2]['mean CT'] >= mean]
    return len(filtered_edges)

def graphValue(graph):
    for v in g.graph.values():
        valor = v
    return valor

# (number of events with rework * 100 / total number of events)
def percentageReworkPerActivityEventsDFG(graph):
    total_repetitions = sum(node[1]['total_repetitions'] for node in graph.nodes.data())
    sum_abs_freq = sum(node[1]['abs_freq'] for node in graph.nodes.data())
    return  total_repetitions*100/sum_abs_freq

# (number of activities with rework * 100 / total number of activities)
def percentageReworkPerActivityDFG(graph):
    count_repetitions = sum(1 for item in graph.nodes.data() if item[1]['total_repetitions'] > 0)
    return  count_repetitions*100/uniqueActivities(graph)

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

            # st.write('./figures/dfg' + str(ident) + '.svg')
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


    # if st.session_state.dataframe is not None:
    #     dic = st.session_state.dataframe

    # if st.session_state.metric is not None:
    #     metric = st.session_state.metric

    # if st.session_state.nodes is not None:
    #     nodes = st.session_state.nodes

    # inicial = st.session_state.inicial

    left_column, right_column = st.columns(2)

    perc_act = st.sidebar.slider('Activity threshold')  

    perc_path = st.sidebar.slider('Path threshold')

    if (nodes == 'concept:name'):
        if metric in ['Mean CT', 'Median CT', 'StDev CT', 'Total CT']:  

            pattern = ['Identify transitions as bottlenecks',
                    'Identify DFGs with the maximum number of unique activities',
                    'Identify DFGs with the minimum number of unique activities']
                    #'Identify transitions with high duration',
                    # 'Identify activities with high duration',   # impememtado pero falta comprobar que existe tiempo asociado a actividades
                    # 'Identify activities as bottlenecks',    # impememtado pero falta comprobar que existe tiempo asociado a actividades
                    # 'Identify clusters of activities',   # no implementado aun
                    # 'Identify activity loops as bottlenecks'))  # no implementado aun
        else:

            pattern = ['Identify infrequent activities',
                    'Identify the most frequent activities',
                    'Identify DFGs with the maximum number of unique activities',
                    'Identify DFGs with the minimum number of unique activities']
                    # 'Identify the most frequent fragment',    # no implementado aun
                    # 'Identify clusters of activities'))   # no implementado aun

    elif(nodes == 'org:resource'):
        if metric in ['Mean CT', 'Median CT', 'StDev CT', 'Total CT']: 
            pattern = ['Identify resources as bottlenecks',
                    # 'Identify clusters of resources',      # no implementado
                    # 'Identify transitions as bottlenecks',
                    'Identify DFGs with the maximum number of unique activities',
                    'Identify DFGs with the minimum number of unique activities']
                    # 'Identify transitions with high duration'
        else:
            pattern = ['Identify resources with high workload',
                    'Identify DFGs with the maximum number of unique activities',
                    'Identify DFGs with the minimum number of unique activities']
                    # 'Identify clusters of resources']   # no implementado aun
    else:
        if metric in ['Mean CT', 'Median CT', 'StDev CT', 'Total CT']:  
            pattern = ['Identify DFGs with the maximum number of unique activities',
                'Identify DFGs with the minimum number of unique activities',
                'Identify transitions as bottlenecks']  
                
        else:
            pattern = ['Identify DFGs with the maximum number of unique activities',
                'Identify DFGs with the minimum number of unique activities']
                # 'Identify loops', # no implementado aun
                # 'Identify decision points'] # no implementado aun


    param = 0
    prueba = {}

    for pat in pattern:
        # st.write(pat)
        # st.write(f"# {pat}")
        
        
        # st.markdown(f" **{pat}** ")
        selected = search(pat, dic, inicial)
        # st.write(selected)
        copia_dict = copy.deepcopy(selected)

        threshold(copia_dict, metric, perc_act, perc_path, nodes)
        st.markdown("""---""")
