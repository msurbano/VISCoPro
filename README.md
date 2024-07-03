# VISCoDFG:  A Tool for Visual Insights Search from Collections of Directly-Follows Graphs

Process mining is a discipline that enables the analysis of business processes from event logs. The Directly-Follows Graph (DFG) is one of the most used visualization types employed in this domain. However, the extraction of valuable information from DFGs requires significant manual effort from users due to the limitations of current process mining tools. To address this challenge, we propose VISCoDFG, a visual query tool designed to ease the manipulation of event logs and the management of DFG collections. The system allows users to query these DFGs to uncover significant insights efficiently. The tool proposed has been developed with Streamlit (https://streamlit.io/), which is a framework
that enables the conversion of data Python scripts into shareable web applications.

![User interface: Main page](https://github.com/msurbano/VISCoDFG/blob/main/User_interface_home_page.png)

### Use case: Find bottlenecks in the process 

- Data source: Business Process Intelligence Challenge 2020 International Declarations Event Log (https://icpmconference.org/2020/bpi-challenge/)
- We focused on the 5th question of this challenge: *Where are the bottlenecks in the process of a travel declaration?*

We open the application and we go to the *Upload file* page and click the *Browse files* button.

![image](https://github.com/msurbano/VISCoDFG/assets/92515344/21de6cf3-0ac5-42d5-b1a7-b4a98a077f80)

We can examine the event log when it is selected.

![image](https://github.com/msurbano/VISCoDFG/assets/92515344/dfb42a77-d8d1-4f3b-8151-9a5b44814c3f)

Next we go to the LoVizQL page where we can define the context of the data. To look for bottlenecks in the process, we can focus on identifying certain attribute values that influence the time performance of the process. 

![image](https://github.com/msurbano/VISCoDFG/assets/92515344/d817c631-e284-4b25-8049-451def2e5a6f)

