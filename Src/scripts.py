import pandas as pd
import networkx as nx
import copy
import fileloader as fl
import sys

#predefined timeslots from OD Matrix
timeslots = ['Morning (0500-0700)',
             'AM Peak (0700-1000)', 
             'Inter Peak (1000-1600)', 
             'PM Peak (1600-1900)', 
             'Evening (1900-2200)', 
             'Late (2200-0030)', 
             'Night (0030-0300)', 
             'Early (0300-0500)']
    
def create_base_graphs(basegraph, frequency):
    ### Creates a dictionary of graphs and adds capacity according to frequency table
    
    graphs = {} 
    
    for timeslot in timeslots:
        tempgraph = copy.deepcopy(basegraph) #create a networkx graph object
        tempgraph = add_capacity(tempgraph, frequency, timeslot) 
        graphs.update({timeslot:tempgraph})
    
    return graphs


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



def add_passengers_time(pgraph, OD, timeslot, paths): # adding estimates of passengers going through certain links in the network using the OD matrix, per specific timeslot
    """Adds estimates of passengers going through links in the network using OD matrix and timeslot

    Keyword arguments:
    pgraph -- the graph to add passenger attribute to
    OD -- OD matrix from TFL
    timeslot - timeslot from OD matrix columns
    paths - shortest path - precalced to improve performance
    """
    nx.set_edge_attributes(pgraph, 0, 'passengers')
    nx.set_edge_attributes(pgraph, 0, 'traveltime')
    nx.set_edge_attributes(pgraph, timeslot, 'timeslot')
    passengersAdded = 0
    passengersNotAdded = 0
    notfound = set()
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

def n1_analysis(graphs, od, shortest_paths, redge):
    tempgraphs = copy.deepcopy(graphs) #create deepcopy to prevent container issues
    passengers = {} # how many passengers added in the analyis, and disconnected from the network
    print(redge)
    for timeslot in timeslots: 
        tempgraph = tempgraphs.get(timeslot)
        tempgraph = add_passengers_time(tempgraph, od, timeslot, shortest_paths)

        tempgraphs.update({timeslot : tempgraph[0]})
        passengers.update({timeslot : tempgraph[1]})
    return tempgraphs, passengers


def add_capacity(graph, frequency, timeslot):
    timetable = { #very ugly table, but it gets the job done
    'Morning (0500-0700)':["0500-0515", '0515-0530', "0530-0545", '0545-0600', '0600-0615', 
     '0615-0630', '0630-0645', '0645-0700'],
    'AM Peak (0700-1000)':['0700-0715', '0715-0730', '0730-0745', '0745-0800', '0800-0815',
       '0815-0830', '0830-0845', '0845-0900', '0900-0915', '0915-0930',
       '0930-0945', '0945-1000'],
    'Inter Peak (1000-1600)':['1000-1015', '1015-1030', '1030-1045', '1045-1100', '1100-1115', '1115-1130',
       '1130-1145', '1145-1200', '1200-1215', '1215-1230', '1230-1245',
       '1245-1300', '1300-1315', '1315-1330', '1330-1345', '1345-1400',
       '1400-1415', '1415-1430', '1430-1445', '1445-1500', '1500-1515',
       '1515-1530', '1530-1545', '1545-1600'],
    'PM Peak (1600-1900)':['1600-1615', '1615-1630', '1630-1645', '1645-1700', '1700-1715', '1715-1730',
       '1730-1745', '1745-1800', '1800-1815', '1815-1830', '1830-1845',
       '1845-1900'],
    'Evening (1900-2200)':['1900-1915', '1915-1930', '1930-1945', '1945-2000', '2000-2015',
       '2015-2030', '2030-2045', '2045-2100', '2100-2115', '2115-2130',
       '2130-2145', '2145-2200'],
    'Late (2200-0030)':['2200-2215', '2215-2230', '2230-2245', '2245-2300', '2300-2315',
       '2315-2330', '2330-2345', '2345-0000', '0000-0015', '0015-0030'],
    'Night (0030-0300)':['0030-0045', '0045-0100', '0100-0115', '0115-0130', '0130-0145',
       '0145-0200', '0200-0215', '0215-0230', '0230-0245', '0245-0300'],
    'Early (0300-0500)':['0300-0315', '0315-0330', '0330-0345', '0345-0400', '0400-0415',
       '0415-0430', '0430-0445', '0445-0500']
    }
    
    traincapacity={ #https://www.whatdotheyknow.com/cy/request/284276/response/737827/attach/6/RS%20Info%20Sheets%204%20Edition.pdf
    'Bakerloo Line':700,
    'Circle Line':953,
    'Hammersmith & City Line':953,
    'Jubilee Line':875,
    'Victoria Line':1028,
    'Central Line':930,
    'District Line':821,
    'East London Line':840, #https://www.whatdotheyknow.com/request/339955/response/848693/attach/3/Class%20378%20Data%20Sheet.pdf
    'Metropolitan Line':1044,
    'Northern Line':662,
    'Piccadilly Line':684,
    'Waterloo & City Line':444,
    'Docklands Light Railway':284 #https://www.railwaygazette.com/28662.article
    }
    
    nx.set_edge_attributes(graph, 0, 'capacity')

    for edge in graph.edges():
        sumfrequency =  0
        for time in timetable.get(timeslot): #sum the frequencies for all the times in the specific timeslot
            sumfrequency += (frequency.loc[(frequency['From Station (Name)'] == edge[0]) 
                & (frequency['To Station (Name)'] == edge[1])][time])

        avg = lambda x : 0 if x is None or not len(x) else int(sum(x)/len(x)) #sometimes 2 values are found, taking average if possible
        sumfrequency = avg(sumfrequency) 

        tcap = traincapacity.get(graph.edges[edge].get('line')) #get the capacity of the trains running on the line

        graph[edge[0]][edge[1]]['capacity'] = tcap * sumfrequency
    
    print('Added capacity for timeslot: {}'.format(timeslot))

    return graph




