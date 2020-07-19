import pandas as pd
import networkx as nx
import pickle

def get_loads(): #pre-formating for easier use
    load = pd.read_excel(r'../data/NUMBAT/FRIDAY/2018FRI_Link_Load.xlsx', sheet_name='2018FRI_Link_Load')
    load.columns = load.iloc[1] 
    load = load[2:]
    return load

def get_frequency(): #pre-formating for easier use
    frequency = pd.read_excel(r'../data/NUMBAT/FRIDAY/2018FRI_Link_Frequency.xlsx', sheet_name='2018FRI_Link_Frequency')
    frequency.columns = frequency.iloc[1]
    frequency = frequency[2:]
    return frequency

def get_OD_LU(): #pre-formating for easier use
    od_network = pd.read_excel(r'../data/NUMBAT/FRIDAY/2018FRI_OD_LU.xlsx', sheet_name='2018FRI_OD_LU')
    od_network.columns = od_network.iloc[1]
    od_network = od_network[2:]
    return od_network

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

def save_obj(obj, name, subdir=""): 
    loc = '../Pickles/' + subdir + str(name) + '.pickle'
    with open(loc, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, subdir = ""):
    loc = '../Pickles/' + subdir + str(name) + '.pickle'
    with open(loc, 'rb') as f:
        data = pickle.load(f)
        return data

