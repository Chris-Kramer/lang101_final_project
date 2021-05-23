#!/usr/bin/env python
"""
---------------------------------- Import libraries-------------------------------------------
"""
import re #regex
import os
from pathlib import Path
import csv 
import pandas as pd
from collections import Counter
from itertools import combinations 
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import spacy
nlp = spacy.load("en_core_web_sm")

"""
------------- Make a csv file from a directory of txt files--------------
"""
def dir_to_csv(directory, output):
    #Write csv file
    with open(output, mode = "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["title", "text"])
        writer.writeheader()
        # For each file
        for file_name in Path(directory).glob("*.txt"):
            #Find its title
            title = re.findall(r"(?!.*/).*txt", str(file_name))
            #Open file
            with open(file_name, "r", encoding = "utf-8") as file:
                #Read file
                text = file.read()
            #add row with filename and text
            writer.writerow({"title":title[0], "text": text })
            
"""
------------- Make a csv file from a txt file--------------
"""
        
def txt_to_csv(txt_file, output_file):
    #Write csv
    with open(output_file, mode = "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["title", "text"])
        writer.writeheader()
        #find title
        title = re.findall(r"(?!.*/).*txt", txt_file)
        # Open txt file
        with open(txt_file, "r", encoding = "utf-8") as file:
            #Read file
            text = file.read()
            #Add row with title and text
            writer.writerow({"title":title[0], "text": text })
"""
------------- draw centrality as a heatmap -------------
"""
# this function has been found here and adjusted
# https://aksakalli.github.io/2017/07/17/network-centrality-measures-and-their-visualization.html#eigenvector-centrality 

def draw_centrality(G, pos, measures, measure_name):
    
    nodes = nx.draw_networkx_nodes(G, pos, node_size=250, cmap=plt.cm.plasma, 
                                   node_color=list(measures.values()),
                                   nodelist=measures.keys())
    nodes.set_norm(mcolors.SymLogNorm(linthresh=0.01, linscale=1, base=10))
    # labels = nx.draw_networkx_labels(G, pos)
    edges = nx.draw_networkx_edges(G, pos)

    plt.title(measure_name)
    plt.colorbar(nodes)
    plt.axis('off')
    plt.show()

"""
------------- Edgelists and helper functions--------------
"""

def create_edges(text_entities):    
    edgelist = []
    # iterate over every document
    for text in text_entities:
        # use itertools.combinations() to create edgelist
        edges = list(combinations(text, 2))
        # for each combination - i.e. each pair of 'nodes'
        for edge in edges:
            # append this to final edgelist
            edgelist.append(tuple(sorted(edge)))
    return edgelist

def count_edges(edgelist):  
    # Count edges
    counted_edges = []
    for key, value in Counter(edgelist).items():
        source = key[0]
        target = key[1]
        weight = value
        counted_edges.append((source, target, weight))

    return counted_edges

# ------------- Edgelist for full names -------------
def create_edgelist_full_names(csv_file, output_dest, entity_label, batch = 500): 
    #read data
    data = pd.read_csv(csv_file)["text"]
    #List of text_entities
    text_entities = []
    i = 0
    for text in data:
        i += 1
        # Skip entries, that aren't a string
        if isinstance(text, str) == False:
            print(f"[WARNING] Index: {i}, Value {text} is not a string... skipping it...")
            continue
        # create temporary list 
        tmp_entities = []
        # create doc object
        nlp.max_length = len(text)
        doc = nlp(text)
        #get speaker
        speaker = re.findall("^.+:", text)[0]
        # for every named entity
        for entity in doc.ents:
            # if that entity is "label" and it isn't the speaker
            if entity.label_ == entity_label and entity.text != speaker:
                # append to temp list
                tmp_entities.append(entity.text.lower())
        
        # Prepend the speaker without the : 
        speaker = re.findall("[^:]*", text)[0].lower()
        tmp_entities.insert(0,  speaker)
        # append temp list to main list
        text_entities.append(tmp_entities)
    
    # Create edgelist
    edgelist = create_edges(text_entities)
    # Count edges
    counted_edges = count_edges(edgelist)
    
    # Create df with edges (i.e. the edgelist)
    edges_df = pd.DataFrame(counted_edges, columns=["nodeA", "nodeB", "weight"])
    # Make df to csv file
    edges_df.to_csv(output_dest, index=False)

# ------------- Edgelist for houses/Last names -------------
def create_edgelist_name_pos(csv_file, output_dest, entity_label, name_pos = 0, batch = 500): 
    #read data
    data = pd.read_csv(csv_file)["text"]
    #List of text_entities
    text_entities = []
    i = 0
    for text in data:
        i += 1
        # Skip entries, that aren't a string
        if isinstance(text, str) == False:
            print(f"[WARNING] Index: {i}, Value {text} is not a string... skipping it...")
            continue
        # create temporary list 
        tmp_entities = []
        # create doc object
        nlp.max_length = len(text)
        doc = nlp(text)
        #get speaker
        speaker = re.findall("^.+:", text)[0]
        # for every named entity
        for entity in doc.ents:
            # if that entity is "label" and it isn't the speaker
            if entity.label_ == entity_label and entity.text != speaker:
                # append to temp list
                tmp_entities.append(entity.text.split()[name_pos].lower())
        
        # Prepend the speaker without the : 
        speaker = re.findall("[^:]*", text)[0].split()[name_pos].lower()
        tmp_entities.insert(0,  speaker)
        # append temp list to main list
        text_entities.append(tmp_entities)
    
    # Create edgelist
    edgelist = create_edges(text_entities)
    # Count edges
    counted_edges = count_edges(edgelist)
    
    # Create df with edges (i.e. the edgelist)
    edges_df = pd.DataFrame(counted_edges, columns=["nodeA", "nodeB", "weight"])
    # Make df to csv file
    edges_df.to_csv(output_dest, index=False)

 # ------------- Edgelist that does it all (I find this code very ugly, but it works) -------------
def create_edgelist(csv_file, output_dest, entity_label, name_pos = "full_name", batch = 500): 
    #read data
    data = pd.read_csv(csv_file)["text"]
    #List of text_entities
    text_entities = []
    i = 0
    for text in data:
        i += 1
        # Skip entries, that aren't a string
        if isinstance(text, str) == False:
            print(f"[WARNING] Index: {i}, Value {text} is not a string... skipping it...")
            continue
        # create temporary list 
        #tmp_entities = []
        # create doc object
        nlp.max_length = len(text)
        doc = nlp(text)
        
        #Get either full name or a specific name position (such as first name, last name or middle name)
        if name_pos == "full_name":
            #get speaker
            speaker = re.findall("[^:]*", text)[0].lower()
        else:
            speaker = re.findall("[^:]*", text)[0].split()[name_pos].lower()              
        
        # for every named entity
        for entity in doc.ents:
            # create temporary list 
            tmp_entities = []
            # if that entity is "label" and it isn't the speaker
            if entity.label_ == entity_label
            and entity.text.lower() != speaker:
                # If user want the full name
                if name_pos == "full_name":
                    # append the full text to temp list
                    tmp_entities.append(speaker)
                    tmp_entities.append(entity.text.lower())
                else:
                    # append specific name position to temp list
                    tmp_entities.append(speaker)
                    tmp_entities.append(entity.text.split()[name_pos].lower())
            
            #Append temporary list to main list            
            text_entities.append(tmp_entities)
    
    # Create edgelist
    edgelist = create_edges(text_entities)
    # Count edges
    counted_edges = count_edges(edgelist)
    
    # Create df with edges (i.e. the edgelist)
    edges_df = pd.DataFrame(counted_edges, columns=["nodeA", "nodeB", "weight"])
    # Make df to csv file
    edges_df.to_csv(output_dest, index=False)
if __name__=="__main__":
    pass