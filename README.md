# Proposing a repoducible method of creating time resilience models in Python using NetworkX and London Underground data
This repo is used to showcase the methodology used in my thesis "Assessing time resilience of public transit networks using London Underground data". The motivation behind this study was to explore the importance of disruption time in public transport network resilience, and how to measure the changing impact over time. Here you can find a methodology to model a non-cascading time-dependent network model, estimating changing passenger loads in a public transport network. 


![test](Media/disruption%20events.png)
> Changing impact of disruption events on capacity utilization for different timeslots

## Thesis link and abstract
The thesis can be found [here](https://jakobs.dev/posts/timeresilience.pdf)

### abstract
The motivation behind this study is to explore the importance of disruption time in public transport network resilience, and how to measure the changing impact over time. We have proposed a methodology to create a non-cascading time-dependent network model, estimating changing passenger loads in a public transport network. Our models, created using empirical passenger data from the London Underground, show that the network is not only most vulnerable during peak-hours to increased passenger loads, but in addition, the impact disruptions on the network change and the highest during peak-hours at certain locations. One of the goals of this research was to explore the topological metrics which identify time-dependent critical network links. In this study, betweenness has shown to be a valuable indicator of link criticality using our model approach. Considering capacity utilization as an important performance metric, disruptions of high-impact non-bridge links showed a small decrease in capacity utilization in preceding and succeeding links and a more significant increase in capacity utilization for parallel links. This parallel effect was less significant in terms of capacity utilization for non-bridge links which have a low betweenness centrality, instead effecting the capacity utilization of neighboring links in a more diffuse manner. Finally, we expected to see a spatial change in the effect of disruption events over time, but the analysis of our model results did not reflect this expectation. The results primed exciting directions for future research, and has given us valuable initial insights on time dependency of public transport resilience.  

## Table of Contents
- [Data](#data)
- [Scripts](#Scripts)
- [Modelling](#modelling)
- [Results](#Results)
- [Closing](#closing)

## Data
For this research, we used passenger data from TFL (Transport For London) in order to estimate
passenger loads on the London Underground network. However, our model methodology can be
applied to other public transport networks using similar data. The passenger data used in the
research can almost exclusively found on the TFL crowding open data website (http://crowding.data.tfl.gov.uk/). The data, published under the name project NUBMAT, contains a static view of
travel patterns and usage of the TFL railway services. It contains passenger data for Monday-Thursday, and Friday, Saturday and Sunday separately. The Monday-Thursday data is
aggregated, so therefore the data from Friday was considered. The Friday dataset contains two
datasets which are of importance to our research: the train frequency table is required in order to
estimate the capacity of the links throughout the day, and the O-D (origin-destination) matrix is
used to assign passengers to links using trip-assignment. An O-D Matrix shows the amount of
passengers traveling between two stations during a certain time period, and is therefore
representative for the trips passengers have taken in the network. The TFL O-D Matrix contains
8 discrete time-steps for which passenger journeys are shown, namely:
    ```['Morning (0500-0700)', 'AM Peak (0700-1000)', ‘Inter-Peak (1000-1600)', 'PM Peak
    (1600-1900)', 'Evening (1900-2200)', 'Late (2200-0030)', 'Night (0030-0300)', 'Early
    (0300-0500)']```
Since these are the time-slots used in the source data, we will be using the same time-slots for the
analysis of time dependency of network resilience. Notice that not all lengths of the time-slots
are identical; the Morning timeslot is two hours, whereas the Inter-peak timeslot is 6. Lastly, an 
external source was used to create the London Underground network graph. This graph data was
compared to TFL data in order to remove discrepancies between the data sources, such as station
names that did not match.

## Scripts
In fileloader.py, logic is written to quickly load and pre-format the xlsx files from the TFL London Data. 
For example: 
```python
def get_loads(): #pre-formating for easier use
    load = pd.read_excel(r'../data/NUMBAT/FRIDAY/2018FRI_Link_Load.xlsx',
         sheet_name='2018FRI_Link_Load')
    load.columns = load.iloc[1] 
    load = load[2:]
    return load
```

Additionally, the NetworkX object containing then processed CSV file with appropriately formatted station and edge names can be created using the get_network() function:
```python
def get_network(): 
    
    lines = pd.read_csv(r'../data/londongraphs/processed/london.lines.csv', index_col='line')
    stations = pd.read_csv(r'../data/londongraphs/processed/london.stations.csv')
    connections = pd.read_csv(r'../data/londongraphs/processed/london.connections.csv')
    graph = nx.Graph()
    for station_id, station in stations.iterrows():
        graph.add_node(station['name'], lon=round(station['longitude'],4), 
            lat=round(station['latitude'],4), s_id=station['id'])

    for connection_id, connection in connections.iterrows():
        station1_name = stations.loc[stations['id'] == connection['station1'],'name'].item()
        station2_name = stations.loc[stations['id'] == connection['station2'],'name'].item()
        graph.add_edge(station1_name, station2_name, time = connection['time'], 
            line = lines.loc[connection['line'], 'name'])
        
    return graph
```

Lastly, The pickle libarary is used to save and load load in the Pickle directory, since certain calculations can take a long time.

As for the scripts file: Passengers traveling through the network model are assigned the links between their origin-destination according to the shortest path between those nodes, weighed on 'time'. NetworkX's built in shortest path algorithm (Dijkstra) is used: 

```python 
def create_shortest_paths(graph, OD):
    """
    Calculate shortest paths for each O-D pair in the OD matrix, where possible. 
    """
    paths = {}
    for od_id, od in OD.iterrows():
        origin = od['Origin Station Name']
        destination = od['Destination Station Name']
        try:             
            path = nx.shortest_path(graph, origin, destination, weight='time') 
        except nx.NetworkXNoPath: 
            path = []
        except nx.NodeNotFound:
            path = []
        paths.update({(origin, destination): path})
    return paths
```

When disrupting (effectively removing) a link, the shortest path needs to be updated according to the new network topology: 

``` python
def update_shortest_paths(basegraph, removed_edge, baseshortest):
    tempgraph = copy.deepcopy(basegraph) #prevent changes to original copy of graph
    tempgraph.remove_edge(removed_edge[0], removed_edge[1])
    newshort = copy.deepcopy(baseshortest) #new shortest paths dict
    """
    First, we check if the removed edge is in any of the paths in the base shortest path dict.
    If it is, we then re-calculate the shortest path using the new topology. This is not
    always possible, in which case an empty path is saved for the origin-destination pair. 
    """
    for key in newshort:
        path = newshort.get(key)
        for i in range(len(path)-1): #if the removed edge pair is in the shortest path, recalculate it. 
            if (([removed_edge[1], removed_edge[0]] == path[i:i+2]) 
                or [removed_edge[0], removed_edge[1]] == path[i:i+2]):
                try:
                    newpath = nx.shortest_path(tempgraph, key[0], key[1], weight='time')
                except nx.NetworkXNoPath: 
                    newpath = []
                    print('no new path found')
                except nx.NodeNotFound:
                    newpath = []
                    print('node not found')
                newshort.update({key: newpath})
    return newshort
```
Arguably the most important function - adding passenger load and travel times, is shown below. It is fairly straightforward, as it iterates through the od-matrix to grab the passengers required to be added per origin-destination pair, after which it iterates through the respective links of the shortest path from that o-d pair. 
```python
def add_passengers_time(pgraph, OD, timeslot, paths): 
    """Adds estimates of passenger loads to a graph using origin-destination pairs and their respective shortest paths

    Keyword arguments:
    pgraph -- the graph to add passenger and traveltime attribute to
    OD -- London Underground OD matrix from TFL 
    timeslot - timeslot from OD matrix columns
    paths - shortest path - precaculated to improve performance
    """
    nx.set_edge_attributes(pgraph, 0, 'passengers')
    nx.set_edge_attributes(pgraph, 0, 'traveltime')
    nx.set_edge_attributes(pgraph, timeslot, 'timeslot')
    passengersAdded = 0
    passengersNotAdded = 0
    for od_id, od in OD.iterrows():
        origin = od['Origin Station Name']
        destination = od['Destination Station Name']
        passengers = int(od[timeslot])
        if paths.get((origin, destination)) is not None: #is there a shortest path to be found?
            path = paths.get((origin, destination))
        else: #if not, continue (no passengers can be added)
            passengersNotAdded += passengers
            print(origin, destination)
            continue
        
        if len(path) == 0:  #an empty path array indicates that no shortest path was found, and passengers can't be added
            print(origin, destination, passengers)
            passengersNotAdded += passengers
            continue
        passengersAdded += passengers
        for i in range(len(path)-1): 
            pgraph[path[i]][path[i+1]]['passengers'] += passengers #adding passengers
            pgraph[path[i]][path[i+1]]['traveltime'] += passengers * int(pgraph[path[i]][path[i+1]]['time']) #adding total travel time
            
    print('Added passengers for timeslot: {}, total rows: {}'.format(timeslot, len(OD)))
    return (pgraph, {'passadd':passengersAdded, 'passnotadd':passengersNotAdded})
```

This form of trip assignment is an all-or-nothing approach similar to prior research [(Gautheir et al., 2018)](https://journals.sagepub.com/doi/abs/10.1177/0361198118792115?journalCode=trra). An alternative form of trip assignment was considered, but was quite computationaly heavy. In this case, an exponential disribution was used in order to assign passengers to n shortest possible paths between their origin and destination: 

```python
def nshortestpaths(graph, origin, destination, npath=3):
    #First, create a generator item for n shortest paths
    pathgen = nx.shortest_simple_paths(graph, source=origin, target=destination, weight='time') 
    #Next, return the n shortest paths in a list
    return [next(pathgen) for i in range(npath) if next(pathgen) is not None] 
```
Next, the trip assignment was changed in order to distribute the passengers over the shortest paths: 

```python
def trip_assigment(graph, paths, passengers):
    npaths = len(paths)

    e = 2.5 #exponential distribution to follow
    #create exponential distribution to assign passengers to:
    dist = [e**i/(sum([e**j for j in range(npaths)])) for i in range(npaths)][::-1] 
    for i in range(npaths):
        path = paths[i]
        npass = int(dist[i] * passengers)
        for i in range(len(path)-1): 
            graph[path[i]][path[i+1]]['passengers'] += npass #adding passengers
            graph[path[i]][path[i+1]]['traveltime'] += npass * int(graph[path[i]][path[i+1]]['time']) 

    return graph
```

## Modelling
In certain (late) timeslots, due to very low train frequency, capacity is at 0. This skews results, therefore we iteratively take the average capacity of neighbouring links which sligtly increases average capacity, but allows for better analysis of results: 
```python
def fixCapacity(bgraph, depth):
    depth += 1 #keep track of depth to prevent stack overflow
    #create a list of edges with no capacity
    nocap = [(a, b) for a, b, data in bgraph.edges(data=True) 
        if data['capacity'] == 0] 

    for start, end in nocap:
        sneighbors = [n for n in bgraph.neighbors(start)] 
        eneighbors = [n for n in bgraph.neighbors(end)]
        #average of neighbours at start of link
        savg = sum(bgraph[s][start]['capacity'] 
            for s in sneighbors)/len(sneighbors) 

        #average of neighbours at end of link
        eavg = sum(bgraph[e][end]['capacity'] 
            for e in eneighbors)/len(sneighbors) 

        bgraph[start][end]['capacity'] = (savg + eavg)//2
    if depth > 100: #if it doesn't converge at 100 iterations, stop
        print('no solution found')
        return
    if len(nocap) > 0: 
        fixCapacity(bgraph, depth)
    return
```

In the notebook file 01- intial pickled models, the shortest paths are calculated and trip assignment is performed. In my actual research, I ended up uploading part of the code to AWS in order to let it run overnight, as the calculations were quite heavy. The code run on AWS is as follows: 

```python
import os.path
from os import path
import networkx as nx
import scripts2 as scr
import fileloader as fl
import dataframes as df
import time

graph = fl.get_network()
basegraphs = fl.load_obj('basegraphs')
od = fl.get_OD_LU()
for edge in graph.edges():
    starttime = time.time()
    edge = list(graph.edges())[i]
    name = ",".join(edge)
    if path.exists('Pickles/test/'+ name + '.pickle'): continue #if I already created this file, skip 
    tempshortest = fl.load_obj(name, 'shortest/')
    tempgraphs, passengers = scr.n1_analysis(basegraphs, od, tempshortest, edge)
    fl.save_obj(tempgraphs, name, 'awsgraphs/')
    fl.save_obj(passengers, name, 'passengers/')
    print('added for edge: {}, time taken {}'.format(name, starttime-time.time()))
```

## Analysis
In order to analyze the results, first (single and multidimentional) dataframes were created. These results were first explored in Python, after which they were exported to excel in order to visualize them in Tableau. 

Two approaches were used in order to analyse the data; first, purely looking at metrics of each of the N-1 models. Secondly, and more interestingly, aggregating these results and plotting them spatially over the london underground map. To do the latter, we must first create a reference excel sheet which tableau can use to plot the edges, this was done using the following code: 

```python
networkdf = pd.DataFrame()
lons, lats = map(nx.get_node_attributes, [graph, graph], ['lon', 'lat'])
lines, times = map(nx.get_edge_attributes, [graph, graph], ['line', 'time'])

for edge in list(graph.edges()):
    networkdf = networkdf.append({"s-e":'start', 
    'edge':edge, 
    'station':edge[0], 
    'lon': lons.get(edge[0]),
    'lat': lats.get(edge[0]),
    'line': lines.get(edge),
    'time' : times.get(edge)
    }, ignore_index=True)
    networkdf = networkdf.append({"s-e":'end', 
    'edge':edge, 
    'station':edge[1], 
    'lon': lons.get(edge[1]),
    'lat': lats.get(edge[1]),
    'line': lines.get(edge),
    'time' : times.get(edge)
    }, ignore_index=True)   
    
networkdf.to_excel('networkgraph.xlsx')    
```
This grabs the relevant data from the basegraph and creates an excelsheet which can be merged with the metrics' excel sheets in order to plot the data spatially using tableau. 

### This section is TODO. 

## Results
### This section is TODO. 


