#!/usr/bin/env python
import pandas as pd
import numpy as np
"""
This function takes my Game of thrones data, cleans it and makes it into x and y data
I'm using the data in two scripts, by having it in a function, I don't need to make changes twice when changing the preprocessing.
It finds all characters who share last name and concactinates their lines based on episodes (e.g. All characters with the last name
"Stark" will have all their lines concactinated in each episode, so there will be 72 entries (a member of the stark familily is in all 72 episodes) for "stark".
The parameter n_episodes refers to how many episodes a member of a house at least should appear in (That way I'm avoiding houses that only appear in one episode, which can mess up the results).  
* It returns 3 values: X data, y data and label names
"""
def get_xy_data(data, n_episodes = 45):
    # -------- Basic cleaning -------
    #load raw data set
    raw_df = pd.read_csv(data) 
    #Only keep last name
    raw_df["Name"] = raw_df["Name"].str.split().str[-1]
    # Remove "man", since this is a generic term for unnamed characters
    raw_df = raw_df[raw_df["Name"] != "man"]
    
    #------------ Concactinate episodes --------
    # This is probably a bit overengineered, but it works well enough
    final_df= pd.DataFrame() #Empty dataframe to append values
    
    #For each unique last name
    for name in raw_df["Name"].unique():
        #Get all sentences uttered by members of current house
        names_df = raw_df[raw_df["Name"] == name]
        #For each episode that a member of the house occurs in
        for episode in names_df["Episode Title"].unique():
            # Create af dataframe containing each sentence this last name utters in the episode
            episode_df = names_df[names_df["Episode Title"] == episode]
            # Concactinate the sentences to one long string
            episode_sentences  = " ".join(episode_df["Sentence"])
            #Create a dictionary with the name and the concactinated sentences
            character_lines_df = {"name": name, "episode": episode_sentences}
            #append dictionary to dataframe
            final_df = final_df.append(character_lines_df, ignore_index = True)

    # Remove rows without values
    final_df = final_df[final_df["episode"] != ""]

    # ---------- Remove houses that only appear in less than 45 episodes -------
    #For each house
    for name in final_df["name"].unique():
        #If the house is in less than 45 episodes
        if len(final_df[final_df["name"]==name]) < n_episodes:
            #Remove all rows, with this house
            final_df = final_df[final_df["name"] != name]
    
    #---------- Save X, y and label data ---------
    X = final_df["episode"]
    y = final_df["name"]
    label_names = y.unique()
    
    return X, y, label_names
    
"""
Function for getting the lenght of the longest entry in X data
Used to set maxlen of a doc
"""
def get_longest_entry(X):
    lengths = [] #array with all lengths
    i = 0 # Counter
    for i in range(0,len(X)):
        #Get the length of the entry
        length = len(X.iloc[i].split())
        lengths.append(length)
        i=+1
    #return the length of the longest episode
    return max(lengths)
    
if __name__=="__main__":
    pass