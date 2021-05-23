#!/usr/bin/env python
"""
---------- Import libs ----------
"""
# System tools
import os
import sys

#Argparse
import argparse
from argparse import RawTextHelpFormatter # Formatting -help

# Data analysis
import pandas as pd
from collections import Counter
from itertools import combinations 
from tqdm import tqdm

# NLP
import spacy
nlp = spacy.load("en_core_web_sm")

# drawing
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolor #Heatmap
plt.rcParams["figure.figsize"] = (20,20)

sys.path.append(os.path.join(".."))
#Homebrewed functions
import utils.network_utils as nu

"""
----------- Main function ------------
"""
def main():
    """
    ---------- Parameters -----------
    """
    #Create an argument parser from argparse
    ap = argparse.ArgumentParser(description = "[INFO] Plot edgelist and calculate centrality measures",
                                 formatter_class=RawTextHelpFormatter) 
    
    #edgelist 
    ap.add_argument("-el", "--edgelist",
                    required = False,
                    default = "real_news_edgelist.csv",
                    type = str,
                    help =
                    "[INFO] Name of the edgelist. It must be a csv file and located in the folder 'data/edgelists' \n" 
                    "[TYPE] str \n"
                    "[DEFAULT] real_news_edgelist.csv \n"
                    "[EXAMPLE] --edgelist Anon_Clara_edgelist.csv")
    
    #Cut of weight point
    ap.add_argument("-f", "--filter",
                    required = False,
                    default = 500,
                    type = int,
                    help =
                    "[INFO] If you only want edges with a weight above a certain number \n"
                    "[TYPE] int \n"
                    "[DEFAULT] 500 \n"
                    "[EXAMPLE] --filter 700")
    
    #name csv output
    ap.add_argument("-co", "--csv_output",
                    required = False,
                    default = "edgelist_centrality.csv",
                    type = str,
                    help =
                    "[INFO] Name of the csv output file (will be located in 'output') and must end in .csv \n"
                    "[TYPE] str \n"
                    "[DEFAULT] edgelist_centrality.csv \n"
                    "[EXAMPLE] --csv_output edgelist_anon_clara.csv")
    
    #name plot output
    ap.add_argument("-vo", "--viz_output",
                    default = "edgelist_graph.png",
                    required = False,
                    type = str,
                    help = 
                    "[INFO] Name of the plot output file (will be located in 'viz') must end in .png, .jpg or .jpeg \n"
                    "[TYPE] str \n"
                    "[DEFAULT] edgelist_graph.png \n"
                    "[EXAMPLE] plot_anon_clara.png")
    
    #return arguments
    args = vars(ap.parse_args())
    
    #Save parameters in variables (this is done for readability)
    data = pd.read_csv(os.path.join("..", "data", "edgelists", args["edgelist"]))
    weight_filter = args["filter"]
    output_file = os.path.join("..", "output", args["csv_output"])
    viz_output = args["viz_output"]
    
    #filter data based on weight
    data = data[data["weight"]>weight_filter]
    
    """
    -------- Calc centrality --------
    """
    print("Creating network...")
    #Create graph netvwork
    G=nx.from_pandas_edgelist(data, 'nodeA', 'nodeB', ["weight"])
    print("Calculating centrality measures ...")
    #Calc Eigenvector centrality
    ev = nx.eigenvector_centrality(G)
    #Calc Betweenness centrality
    bc = nx.betweenness_centrality(G)
    #Calc Degree centrality
    dc = nx.degree_centrality(G)

    """
    ------------- Plot edgelist and centrality -----------
    """
    print("Creating network...")
    #Create graph netvwork
    G=nx.from_pandas_edgelist(data, 'nodeA', 'nodeB', ["weight"])
    print("Plotting network ...")
    #Plot it
    pos = nx.nx_agraph.graphviz_layout(G, prog="neato")
    
    # Plot eigenvector
    #fig = plt.figure()  
    #nx.draw(G, pos, with_labels=True, node_size=20, font_size=10) 
    #nu.draw_centrality(G, pos, ev, "Eigenvector Centrality")
    #Save plot
    #fig.savefig(os.path.join("..", "viz", "eigenvector_" + viz_output), bbox_inches="tight")
    
    # Plot betweenes
    #fig = plt.figure()  
    #nx.draw(G, pos, with_labels=True, node_size=20, font_size=10)     
    #nu.draw_centrality(G, pos, bc, "Betweenes Centrality")
    #Save plot
    #fig.savefig(os.path.join("..", "viz", "Betweenes_"+ viz_output), bbox_inches="tight")
    
    # Plot degree
    #fig = plt.figure()  
    #nx.draw(G, pos, with_labels=True, node_size=20, font_size=10)
    #nu.draw_centrality(G, pos, dc, "Degree Centrality")
    #Save plot
    #fig.savefig(os.path.join("..", "viz", "Degree_"+ viz_output), bbox_inches="tight")
    
    # Plot eigenvector - directed
    G=nx.from_pandas_edgelist(data, 'nodeA', 'nodeB', ["weight"], create_using = nx.MultiDiGraph)
    fig = plt.figure()  
    nx.draw(G, pos, with_labels=True, node_size=20, font_size=10) 
    nu.draw_centrality(G, pos, ev, "Eigenvector Centrality")
    #Save plot
    fig.savefig(os.path.join("..", "viz", "test_eigenvector_" + viz_output), bbox_inches="tight")
    
    """
    --------- Create dataframes ---------
    """
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
    
    """
    --------- Merge dataframes and save csv---------
    """
    #Merge dataframes
    result = pd.merge(df_ev, df_bc,  how="left", on=[0, 0])
    result = pd.merge(result, df_dc,  how="left", on=[0, 0])
    
    #Rename column "0" to node
    result = result.rename(columns={0: "node"})
    # Sort by eigenvector centrality
    result = result.sort_values("eigenvector", axis = 0, ascending=False)
    #Save df as csv
    result.to_csv(output_file, index = False)
    
#Define behaviour when called from command line
if __name__ == "__main__":
    main()