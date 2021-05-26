#!/usr/bin/env python
"""
---------------------------------- Import libraries-------------------------------------------
"""
# System tools
import os
from pathlib import Path

# Cleaning and reading data
import csv 
import pandas as pd
import re #regex

# Working with lists
from collections import Counter
from itertools import combinations 
from tqdm import tqdm

# NLP
import spacy
nlp = spacy.load("en_core_web_sm")

#Network analysis
import networkx as nx

#Plotting
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (20,20)
import matplotlib.colors as mcolors #Heatmap
from matplotlib.collections import PatchCollection #Plotting directed edgelists
from matplotlib import ticker
"""
------------- Make a df from a txt file--------------
"""
        
def txt_to_df(txt_file):
    
    df = pd.DataFrame(columns = ["title", "text"])    
    # Open txt file
    with open(txt_file, "r", encoding = "utf-8") as file:
        #Read file
        text = file.read()
        #Get title
        title = re.findall(r"(?!.*/).*txt", txt_file)
        #create row and append it
        df_row = {"title": title, "text": text}
        df = df.append(df_row, ignore_index = True)
        
    return df

"""
------------- Caculate centrality measures -------------
"""   
def calc_centralities(data):
    # Create directed graph 
    G_directed = nx.from_pandas_edgelist(data, 'nodeA', 'nodeB', ["weight"], create_using=nx.MultiDiGraph())
    #Calc Eigenvector centrality
    ev = nx.eigenvector_centrality_numpy(G_directed)
    #Calc Degree centrality
    dc = nx.degree_centrality(G_directed)
    
    # Create undirected graph
    # This is done, since betweenes can't be calculated in a directed graph
    G_undirected = nx.from_pandas_edgelist(data, "nodeA", "nodeB", ["weight"])
    bc = nx.betweenness_centrality(G_undirected)
        
    return G_directed, G_undirected, ev, bc, dc
"""
------------- Plot network -------------
"""
# this function for adding headmap to nodes was originally found here 
# https://aksakalli.github.io/2017/07/17/network-centrality-measures-and-their-visualization.html
# However it has been changed substantially and bears little resemblances to the original function
def plot_network(G, pos, centrality, title, output_file, directed = False):
    
    # Draw network
    nx.draw(G, pos, with_labels=True, node_size=20,
            font_size=12, font_color = "k",
            font_family="monospace",
            font_weight = "bold")
    
    # Draw nodes with colormap
    nodes = nx.draw_networkx_nodes(G, pos, node_size=250, cmap=plt.cm.winter, 
                                   node_color=list(centrality.values()),
                                   nodelist=centrality.keys())
    # Set normalization for colors (using logarithmic)
    nodes.set_norm(mcolors.SymLogNorm(linthresh=0.01, linscale=1, base=10))
    
    # Add arrows if it is a directed network graph
    # Get weights and change color depending on weight
    if directed:
        # Get weights
        edges = G.edges()
        weights = []
        for nodeA, nodeB in edges:
            weights.append(G[nodeA][nodeB][0]["weight"])
        # Draw edges
        edges = nx.draw_networkx_edges(G, pos, edge_cmap = plt.cm.viridis, arrows = True, edge_color = weights)
        #Colorbar for edges
        pc = PatchCollection(edges, cmap=plt.cm.viridis)
        pc.set_array(weights)
        plt.colorbar(pc, orientation = "horizontal", label = "Edge weight")
        plt.axis('off')
        
    else:
        # Get weights
        edges = G.edges()
        weights = []
        for nodeA, nodeB in edges:
            weights.append(G[nodeA][nodeB]["weight"])          
        # Draw edges
        edges = nx.draw_networkx_edges(G, pos, edge_cmap = plt.cm.viridis, edge_color = weights)
        plt.colorbar(edges, orientation = "horizontal", label = "Edge weight")
        plt.axis('off')
     
    # Title
    plt.title(title)
    #Colorbar for nodes
    cbar = plt.colorbar(nodes, orientation="vertical", label= "Node Centrality")
    plt.axis('off')
    #Save and close plt
    plt.savefig(output_file, bbox_inches="tight")
    plt.close("all")

"""
--------- Create dataframes ---------
"""
def save_centrality_measures(ev, bc, dc, output_file = "centrality_measures.csv"):
    print("Creating dataframes ...")
    #Create dataframes
    #eigenvector
    df_ev = pd.DataFrame(ev.items())
    #change eigenvector columnname
    df_ev = df_ev.rename(columns={1: "eigenvector"})
    
    #Betweenes centrality
    df_bc = pd.DataFrame(bc.items())
    #change Betweenes centrality columnname
    df_bc = df_bc.rename(columns={1: "betweenes"})
    
    #Degree centrality
    df_dc =pd.DataFrame(dc.items())
    #change Degree centrality columnname
    df_dc = df_dc.rename(columns={1: "degree"})
        
    # ------ Merge dataframes and save csv
    #Merge dataframes
    result = pd.merge(df_ev, df_bc,  how="left", on=[0, 0])
    result = pd.merge(result, df_dc,  how="left", on=[0, 0])
    #Rename column "0" to node
    result = result.rename(columns={0: "node"})
    # Sort by eigenvector centrality
    result = result.sort_values("eigenvector", axis = 0, ascending=False)
    #Save df as csv
    result.to_csv(output_file, index = False)

"""
------------- Edgelists and helper functions--------------
"""
def count_edges(edgelist):  
    print("Counting edges ...")
    # Count edges
    counted_edges = []
    for key, value in tqdm(Counter(edgelist).items()):
        try:
            source = key[0]
            target = key[1]
            weight = value
            counted_edges.append((source, target, weight))
        except IndexError:
            continue
            
    return counted_edges

def create_edges(text_entities):
    edgelist = []
    # iterate over every document
    for text in text_entities:
        try:
            # append entity pair as a tupple
            edgelist.append(tuple((text)))
        except IndexError:
            continue
                
    return edgelist

def create_edgelist(df, entity_label = "PERSON", batch = 500): 
    #read data
    data = df["text"]
    #List of text_entities
    text_entities_full_names = []
    text_entities_first_names = []
    text_entities_house_names = []
    text_entities_region_names = []
    
    # Get list of houses and regions
    houses_regions = pd.read_csv(os.path.join("..", "data", "houses_regions.csv"))
    i = 0
    for text in tqdm(data):
        i += 1
        # Skip entries, that aren't a string
        if isinstance(text, str) == False:
            print(f"[WARNING] Index: {i}, Value {text} is not a string... skipping it...")
            continue
        
        # create doc object
        nlp.max_length = len(text)
        doc = nlp(text)
        
        # Get speaker info
        speaker_full_name = re.findall("[^:]*", text)[0].lower()
        speaker_first_name = re.findall("[^:]*", text)[0].split()[0].lower()
        speaker_house_name = re.findall("[^:]*", text)[0].split()[-1].lower()
        speaker_region = "unknown"
        
        # for every named entity
        for entity in doc.ents:
            # create temporary lists 
            tmp_entities_full_name = []
            tmp_entities_first_name = []
            tmp_entities_house_name = []
            tmp_entities_region_name = []    
            
            # if that entity is "label" and it isn't the speaker
            if entity.label_ == entity_label and entity.text.lower() != speaker_full_name:
                
                # append full names 
                # The speaker is also appended since this creates a directed edgelist
                if entity.text.lower() != speaker_full_name:
                    tmp_entities_full_name.append(speaker_full_name)
                    tmp_entities_full_name.append(entity.text.lower())
                    text_entities_full_names.append(tmp_entities_full_name) 
                    
                # append first names 
                # The speaker is also appended since this creates a directed edgelist                
                if entity.text.split()[0].lower() != speaker_first_name:
                    tmp_entities_first_name.append(speaker_first_name)
                    tmp_entities_first_name.append(entity.text.split()[0].lower())
                    text_entities_first_names.append(tmp_entities_first_name)
                    
                # append house names 
                # The speaker's house name is also appended since this creates a directed edgelist
                if entity.text.split()[-1].lower() != speaker_house_name:
                    entity_house = entity.text.split()[-1].lower()
                    entity_region = "unknown" #Needs a value since I have sometimes experienced scope errors
                    
                    # IF the entities last name and speakers last name are in the list of houses them
                    for house in houses_regions.house:                        
                        if speaker_house_name == house:
                            speaker_region = houses_regions[houses_regions["house"] == speaker_house_name]["region"].values[0]
                            tmp_entities_house_name.append(house)
                            
                        elif entity_house == house:
                            entity_region = houses_regions[houses_regions["house"] == entity_house]["region"].values[0]
                            tmp_entities_house_name.append(house)
                        
                # If the speaker and target region are different, append regions
                if entity_region != speaker_region:
                            #Append region name
                            tmp_entities_region_name.append(speaker_region)
                            tmp_entities_region_name.append(entity_region)
                            text_entities_region_names.append(tmp_entities_region_name)
                    
                # append temp list with to main list if it contains a pair of nodes (otherwise the nodes aren't refering to eachother)
                # This way I'm getting a directed edgelist
                if len(tmp_entities_house_name) > 1:
                    text_entities_house_names.append(tmp_entities_house_name)
                    
    # Create edgelists
    edgelist_full_names = create_edges(text_entities_full_names)
    edgelist_first_names = create_edges(text_entities_first_names)
    edgelist_house_names = create_edges(text_entities_house_names)
    edgelist_region_names = create_edges(text_entities_region_names)
    
    # Count edges
    counted_edges_full_names = count_edges(edgelist_full_names)
    counted_edges_first_names = count_edges(edgelist_first_names)
    counted_edges_house_names = count_edges(edgelist_house_names)
    counted_edges_region_names = count_edges(edgelist_region_names)
    
    # Create dfs with edges and save as csv (i.e. the edgelist)
    full_edges_df = pd.DataFrame(counted_edges_full_names, columns=["nodeA", "nodeB", "weight"])
    first_edges_df = pd.DataFrame(counted_edges_first_names, columns=["nodeA", "nodeB", "weight"])
    house_edges_df = pd.DataFrame(counted_edges_house_names, columns=["nodeA", "nodeB", "weight"])
    regions_edges_df = pd.DataFrame(counted_edges_region_names, columns=["nodeA", "nodeB", "weight"])
    
    return full_edges_df, first_edges_df, house_edges_df, regions_edges_df 

#Define behaviour when called from command line
if __name__=="__main__":
    pass