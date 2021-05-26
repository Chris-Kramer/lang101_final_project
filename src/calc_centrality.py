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

sys.path.append(os.path.join(".."))
#Homebrewed functions
import utils.network_utils as nu
import utils.work_flow as wf # Controlling the workflow (i.e. if-else statements)
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
    
    #Cut of weight point for all seasons
    ap.add_argument("-f_a_u", "--filter_a_full",
                    required = False,
                    default = 8,
                    type = int,
                    help =
                    "[INFO] If you only want edges with a weight above a certain number for all seasons and full names\n"
                    "[TYPE] int \n"
                    "[DEFAULT] 8 \n"
                    "[EXAMPLE] --filter_a_full 10")
    
    #Cut of weight point for all seasons
    ap.add_argument("-f_a_i", "--filter_a_first",
                    required = False,
                    default = 8,
                    type = int,
                    help =
                    "[INFO] If you only want edges with a weight above a certain number for all seasons and first names\n"
                    "[TYPE] int \n"
                    "[DEFAULT] 8 \n"
                    "[EXAMPLE] --filter_a_first 10")
     
    
    #Cut of weight point for all seasons
    ap.add_argument("-f_s_u", "--filter_s_full",
                    required = False,
                    default = 2,
                    type = int,
                    help =
                    "[INFO] If you only want edges with a weight above a certain number for individual seasons and full names\n"
                    "[TYPE] int \n"
                    "[DEFAULT] 2 \n"
                    "[EXAMPLE] --filter_s_full 4")
    
    #Cut of weight point for all seasons
    ap.add_argument("-f_s_i", "--filter_s_first",
                    required = False,
                    default = 2,
                    type = int,
                    help =
                    "[INFO] If you only want edges with a weight above a certain number for individual seasons and first names\n"
                    "[TYPE] int \n"
                    "[DEFAULT] 2 \n"
                    "[EXAMPLE] --filter_s_first 4")
    
    #batch_size 
    ap.add_argument("-bs", "--batch_size",
                    required = False,
                    default = 200,
                    type = int,
                    help = 
                    "[INFO] The batch size for nlp pipe \n"
                    "[TYPE] int \n"
                    "[DEFAULT] 200 \n"
                    "[EXAMPLE] --batch_size 150")
    
    #return arguments
    args = vars(ap.parse_args())
    
    #Save parameters in variables (this is done for readability)
    filter_a_full = args["filter_a_full"]
    filter_a_first = args["filter_a_first"]
    filter_s_full = args["filter_s_full"]
    filter_s_first = args["filter_s_first"]
    batch_size = args["batch_size"]
    
    # ------ Clean data ------
    print("Cleaning data ...")
    df =  pd.read_csv(os.path.join("..", "data", "Game_of_Thrones_Script.csv"))
    # I'm renaming columns so the dataset can be fed directly to the utility functions
    df.rename({"Sentence": "text", "Episode Title": "title"}, axis = "columns", inplace=True)

    # Put the speaker's name in the text column
    # That way the speaker can be located with a simple regex
    df["text"] = df["Name"] + ": " + df["text"]
    
    
    # ------ Network analysis on all seasons ------
    print(f"Creating edgelists for 'all seasons' ...")  
    wf.control_flow(data = df,
                    season = "all_seasons",
                    filter_full = filter_a_full,
                    filter_first = filter_a_first,
                    batch_size = batch_size)
    
    # ----- Network analysis on individual seasons -----
    for season in range(1,6): # Season 1 to 5
        df_season = df.loc[df["Season"] == f"Season {str(season)}"]
        wf.control_flow(data = df_season,
                        season = season,
                        filter_full = filter_s_full,
                        filter_first = filter_s_first,
                        batch_size = batch_size)

#Define behaviour when called from command line
if __name__ == "__main__":
    main()