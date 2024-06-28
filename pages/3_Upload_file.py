import streamlit as st
import pandas as pd
from io import StringIO
import pm4py

from typing import Tuple, Union, List, Dict, Any, Optional, Set

import pandas as pd
from pandas import DataFrame

from pm4py.algo.discovery.powl.inductive.utils.filtering import FILTERING_THRESHOLD
from pm4py.algo.discovery.powl.inductive.variants.dynamic_clustering_frequency.dynamic_clustering_frequency_partial_order_cut import \
    ORDER_FREQUENCY_RATIO
from pm4py.algo.discovery.powl.inductive.variants.powl_discovery_varaints import POWLDiscoveryVariant
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.dfg.obj import DFG
from pm4py.objects.powl.obj import POWL
from pm4py.objects.heuristics_net.obj import HeuristicsNet
from pm4py.objects.transition_system.obj import TransitionSystem
from pm4py.objects.trie.obj import Trie
from pm4py.objects.log.obj import EventLog
from pm4py.objects.log.obj import EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.util.pandas_utils import check_is_pandas_dataframe, check_pandas_dataframe_columns
from pm4py.utils import get_properties, __event_log_deprecation_warning
from pm4py.util import constants, pandas_utils
import deprecation
import importlib.util

if 'original' not in st.session_state:
    st.session_state.original = pd.DataFrame()

st.write('### Upload event log')

uploaded_file = st.file_uploader('Choose file')

if uploaded_file:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    #st.write(bytes_data)

    # To convert to a string based IO:
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

    if df is not None:
        if pd.api.types.is_datetime64_any_dtype(df['time:timestamp']):
            st.write("1) La columna timestamp es de tipo datetime")
        else:
            # st.write('no es fecha')
            df['time:timestamp'] = pd.to_datetime(df['time:timestamp'])
            # st.write('1) timestamp convertido a tipo datetime')


        if not pd.api.types.is_string_dtype(df['case:concept:name']):
            df['case:concept:name'] = df['case:concept:name'].astype(str)

    


    st.markdown('##### 1. Next go to the _LoVizQL_ main page to define the context of the data. ')
    st.markdown('##### 2. Once the data context is defined, you can access _Pattern recommendation_ or _Pattern seacrh_ to obtain recommendations.')

    st.write('Original event log')
    st.dataframe(df)

    # st.write(df.columns.tolist())
    try:
        dfg, start_activities, end_activities = pm4py.discovery.discover_dfg(df, case_id_key='case:concept:name', activity_key='concept:name', timestamp_key='time:timestamp')
        # Resto del código
    except Exception as e:
        st.write("Error:", e)
        raise  # Esto imprimirá el traceback completo
    
    st.session_state.original = df  # backup the filtered df

    # st.write('filtered df')
    # st.dataframe(st.session_state.filtered_df)