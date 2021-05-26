#!/usr/bin/env python
"""
INFO: This is basically just two functions, with a lot of if-else statements that controls the workflow and bundles up all the utility functions. This is usefull, since I'm doing the same work flow multiple times. That way, I only need to change the logic once, rather than multiple times.  
"""
"""
---------------- Import libraries ----------------
"""
# System tools
import os
import sys

# Data analysis
import pandas as pd

# time keeping
from tqdm import tqdm

# network analysis
import networkx as nx
sys.path.append(os.path.join(".."))
import utils.network_utils as nu
"""
---------------- Calculate centralities and plot them ----------------
"""
def plot_and_calc_centralities(df, output_folder, season):
    #Make dir for season
    filepath = os.path.join("..", "output", output_folder)
    os.makedirs(filepath, exist_ok = True) 
    
    #Calculate centralities
    G_directed, G_undirected, ev, bc, dc = nu.calc_centralities(df)
        
    # Position layout directed graph
    pos = nx.nx_agraph.graphviz_layout(G_directed, prog="neato")
    # Position layout undirected graph
    # Betweenes can only be calculated with an undirected graph
    pos = nx.nx_agraph.graphviz_layout(G_undirected, prog="neato")
    
    #Plot network based on centrality
    # Eigenvector
    print("Eigenvector ...")
    nu.plot_network(G_directed, pos, centrality = ev, title = "Eigenvector Centrality",
                    output_file = os.path.join(filepath, f"season_{str(season)}_eigenvector_viz.png"),
                    directed = True)
        
    print("Betweenes ...")
    # Betweenes
    # Can only be calculated with an undirected graph
    nu.plot_network(G_undirected, pos, centrality = bc, title = "Betweenes Centrality",
                    output_file = os.path.join(filepath, f"season_{str(season)}_betweenes_viz.png"),
                    directed = False)
        
    print("Degree ...")
    #degree
    nu.plot_network(G_directed, pos, centrality = dc, title = "Degree Centrality",
                    output_file = os.path.join(filepath, f"season_{str(season)}_degree_viz.png"), 
                    directed = True)
        
    print(f"Saving centrality measures ...")
    #save centrality measures in csv 
    nu.save_centrality_measures(ev, bc, dc,
                                output_file = os.path.join(filepath, f"season_{str(season)}_centralities.csv"))

"""
---------------- Control how to deal with edgelists ----------------
"""
def control_flow(data, season = "all_seasons",
                 filter_full = 4,
                 filter_first = 4,
                 entity_label = "PERSON",
                 batch_size = 200):
    
    print(f"Creating edgelists for season '{str(season)}' ...")  
    full_edges_df, first_edges_df, house_edges_df, regions_edges_df = nu.create_edgelist(data,
                                                                                         entity_label = entity_label,
                                                                                         batch = batch_size)    
    print(f"Calculating centralities for season '{str(season)}' ...")
        
    # Skip season if there are no nodes with a weight above filter
    #filter data based on weight
    full_edges_df = full_edges_df[full_edges_df["weight"]>filter_full]
    # Full names
    if len(full_edges_df.index) == 0:
        print(f"[WARNING] There are no nodes with a weight above {filter_seasons} in this season for full names...")
        print(f"[WARNING] Skipping full names for season '{str(season)}' ...")            
    else:
        print(f"Plotting for full names ...")
        plot_and_calc_centralities(full_edges_df, os.path.join("season_" + str(season), "full_names"), season)
    
    # Skip season if there are no nodes with a weight above filter
    #filter data based on weight
    first_edges_df = first_edges_df[first_edges_df["weight"]>filter_first]    
    # First name            
    if len(first_edges_df.index) == 0:
        print(f"[WARNING] There are no nodes with a weight above {filter_seasons} in this season for first names...")
        print(f"[WARNING] Skipping full names for season '{str(season)}' ...")              
    else:
        print(f"Plotting for first names ...")
        plot_and_calc_centralities(first_edges_df, os.path.join("season_" + str(season), "first_names"), season)        
    
    # Skip house names if there are no nodes above 0 (not adding filter since there are so few nodes)
    # House names           
    if len(house_edges_df.index) == 0:
        print(f"[WARNING] There are no nodes with a weight above '{filter_seasons}' in this season for house names...")
        print(f"[WARNING] Skipping house names for season '{str(season)}' ...")           
    else:
        print(f"Plotting for house names ...")
        plot_and_calc_centralities(house_edges_df, os.path.join("season_" + str(season), "house_names"), season)
    
    # Skip region names if there are no nodes above 0 (not adding filter since there are so few nodes)
    # Region names           
    if len(regions_edges_df.index) == 0:
        print(f"[WARNING] There are no nodes with a weight above '{filter_seasons}' in this season for region names...")
        print(f"[WARNING] Skipping Region names for season '{str(season)}' ...")         
    else:
        print(f"Plotting for region names ...")
        plot_and_calc_centralities(regions_edges_df, os.path.join("season_" + str(season), "region_names"), season)
#Define behaviour when called from command line
if __name__=="__main__":
    pass