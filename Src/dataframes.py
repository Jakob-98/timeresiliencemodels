import networkx as nx
import pandas as pd

def create_node_df(G):
    atts = ['testattr']

    df = pd.DataFrame(index=G.nodes())

    node_attributes_to_col(G, df, atts)
    node_metrics_to_col(G, df)

    return df
    


def node_attributes_to_col(G, df, atts: list):
    for att in atts:
        df[att] = pd.Series(nx.get_node_attributes(G, att))

def node_metrics_to_col(G, df):
    if type(G) == type(nx.Graph()): # some of these metrics don't work for multigraphs etc.
        df['clustering'] = pd.Series(nx.clustering(G))
        df['degree'] = pd.Series(G.degree())
        df['degree_centrality'] = pd.Series(nx.degree_centrality(G))
        df['closeness'] = pd.Series(nx.closeness_centrality(G))
        df['betweeness'] = pd.Series(nx.betweenness_centrality(G, normalized=True))

def create_edge_df(G): # TODO create edge df logic
    df = pd.DataFrame(index=G.edges())
    return df


def edge_attributes_to_col(G, df, atts: list):
    for att in atts:
        df[att] = pd.Series(nx.get_edge_attributes(G, att))
        
        
def create_weighed_node_df(G):
    
    attributes = set() #grabbing each of the attributes
    for node in G.nodes(data=True):
        for att in node[1].keys():
            attributes.add(att)

    df = pd.DataFrame(index=G.nodes())

    for att in attributes:
        df[att] = pd.Series(nx.get_node_attributes(G, att))
        
    df['clustering'] = pd.Series(nx.clustering(G))
    df['clust_weighed'] = pd.Series(nx.clustering(G, weight='passengers'))
    df['degree_centrality'] = pd.Series(nx.degree_centrality(G))
    #df['degree_centrality'] = pd.Series(nx.degree_centrality(G, weight='passengers')) #https://stackoverflow.com/questions/41912051/centralities-in-networkx-weighted-graph
    df['closeness'] = pd.Series(nx.closeness_centrality(G))
    df['closeness_weighed'] = pd.Series(nx.closeness_centrality(G, distance='passengers')) #
    df['betweeness'] = pd.Series(nx.betweenness_centrality(G, normalized=True))
    df['betweeness_weighed'] = pd.Series(nx.betweenness_centrality(G, normalized=True, weight='passengers'))

    # aggregate passenger loads from links to nodes
    get_p = lambda e : G[e[0]][e[1]].get('passengers') #get the passenger load from a link
    sumload = lambda n: sum([get_p(edge) for edge in G.edges() if n in edge]) #sum all passengers loads if a node is part of the link
    idx, vals = [node for node in G.nodes()], [sumload(node) for node in G.nodes()] #getting index and values using list comprehension
    df['aggregated_passengers'] = pd.Series(vals, index=idx) 
    
    #takes average of passenger loads from links to node
    # get_c = lambda e : G[e[0]][e[1]].get('cap_util_OD') #get the passenger load from a link
    # avgcap = lambda n: sum([get_c(edge) for edge in G.edges() if n in edge])/len([get_c(edge) for edge in G.edges() if n in edge]) #sum all passengers loads if a node is part of the link
    # idx, vals = [node for node in G.nodes()], [avgcap(node) for node in G.nodes()] #getting index and values using list comprehension
    # df['average_cap_util'] = pd.Series(vals, index=idx) 
    
    return df


def concat_frames(graphs, timeslots):
    dfs = {}
    for timeslot in timeslots:
        tempdf = timeslot
        tempg = graphs.get(timeslot)
        tempdf = create_weighed_node_df(tempg)
        dfs.update([(timeslot, tempdf)]) #for some obscure reason update(timeslot = tempdf) wasn't working. 
        
    return pd.concat(dfs, axis=1)


def create_timeseries_df(df, timeslots, attribute): #create timeseries dataframe from the concatenated dataframe
    tempdf = pd.DataFrame(index=df.index)
    for timeslot in timeslots:
        tempdf[timeslot] = pd.Series(df[timeslot][attribute])
        
    return tempdf











####
##OLD
###


#now added to create_weighed_node_df
def aggregate_link_attributes(G):
    

    df = pd.DataFrame(index=G.nodes())
    
    get_p = lambda e : G[e[0]][e[1]].get('passengers') #get the passenger load from a link
    sumload = lambda n: sum([get_p(edge) for edge in G.edges() if n in edge]) #sum all passengers loads if a node is part of the link
    idx, vals = [node for node in G.nodes()], [sumload(node) for node in G.nodes()] #getting index and values using list comprehension
    df['aggregated_passengers'] = pd.Series(vals, index=idx) 
    
    #much shorter but unreadable code: [(n, sum(g[e[0]][e[1]].get('passengers') for e in G.edges() if n in e)) for n in G.nodes()]
    
    get_c = lambda e : G[e[0]][e[1]].get('cap_util_OD') #get the passenger load from a link
    avgcap = lambda n: sum([get_c(edge) for edge in G.edges() if n in edge])/len([get_c(edge) for edge in G.edges() if n in edge]) #sum all passengers loads if a node is part of the link
    idx, vals = [node for node in G.nodes()], [avgcap(node) for node in G.nodes()] #getting index and values using list comprehension
    df['average_cap_util'] = pd.Series(vals, index=idx) 
    
    return df


