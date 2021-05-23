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
------------- Create csv_file with edgelist, from a csv_file of text--------------
"""
            
def create_edgelist(csv_file, output_dest, entity_label, batch = 500): 
    #read data
    data = pd.read_csv(csv_file)["text"]
    #List of text_entities
    text_entities = []
    i = 0
    for text in data:
        i +=1
        # Skip entries, that aren't a string
        if isinstance(text, str) == False:
            print(f"[WARNING] Index: {i}, Value {text} is not a string... skipping it...")
            continue
        # create temporary list 
        tmp_entities = []
        # create doc object
        nlp.max_length = len(text)
        doc = nlp(text)
        # for every named entity
        for entity in doc.ents:
            # if that entity is "label"
            if entity.label_ == entity_label:
                # append to temp list
                tmp_entities.append(entity.text)
        # append temp list to main list
        text_entities.append(tmp_entities)

    edgelist = []
    # iterate over every document
    for text in text_entities:
        # use itertools.combinations() to create edgelist
        edges = list(combinations(text, 2))
        # for each combination - i.e. each pair of 'nodes'
        for edge in edges:
            # append this to final edgelist
            edgelist.append(tuple(sorted(edge)))
        
    # Count edges
    counted_edges = []
    for key, value in Counter(edgelist).items():
        source = key[0]
        target = key[1]
        weight = value
        counted_edges.append((source, target, weight))
    # Create df with edges (i.e. the edgelist)
    edges_df = pd.DataFrame(counted_edges, columns=["nodeA", "nodeB", "weight"])
    # Make df to csv file
    edges_df.to_csv(output_dest, index=False)

#Define behaviour when called from command line
if __name__=="__main__":
    pass