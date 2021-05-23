import pandas as pd
import os

# I'm creating three data sets one which contains house names, one for individual characters' first names and one for characters' full name 

# ----------- Data set for houses ------------ 
# Load data
df_houses = pd.read_csv(os.path.join("..", "data", "raw_data", "Game_of_Thrones_Script.csv"))
# Keep only last name
df_houses["Name"] = df_houses["Name"].str.split(" ").str[-1]

#I'm renaming columns so the dataset can be fed directly to the script "create_edgelists"
df_houses.rename({"Sentence": "text", "Episode Title": "title"}, axis="columns", inplace =True)

# Put the speaker's last name in the text column
# This makes it way easier to work with the edgelist. 
# It shouldn't make a difference since my weighted edgelist doesn't count direction
df_houses["text"] = df_houses["Name"] + " " + df_houses["text"]

# Save csv
df_houses.to_csv(os.path.join("..", "data", "raw_data", "network_houses_GOT.csv"))

# ------------- Data set for characters -------------
# Keep only first name
df_characters =  pd.read_csv(os.path.join("..", "data", "raw_data", "Game_of_Thrones_Script.csv"))
df_characters["Name"] = df_characters["Name"].str.split().str[0]
# I'm renaming columns so the dataset can be fed directly to the script "create_edgelists"
df_characters.rename({"Sentence": "text", "Episode Title": "title"}, axis = "columns", inplace=True)

# Put the speaker's first name in the text column
# This makes it way easier to work with the edgelist. 
# It shouldn't make a difference since my weighted edgelist doesn't count direction
df_characters["text"] = df_characters["Name"] + " " + df_characters["text"]

# save csv
df_characters.to_csv(os.path.join("..", "data", "raw_data", "network_characters_GOT.csv"))

# ------------ Data set with full names -----------
df_full_names =  pd.read_csv(os.path.join("..", "data", "raw_data", "Game_of_Thrones_Script.csv"))
# I'm renaming columns so the dataset can be fed directly to the script "create_edgelists"
df_full_names.rename({"Sentence": "text", "Episode Title": "title"}, axis = "columns", inplace=True)

# Put the speaker's name in the text column
# This makes it way easier to work with the edgelist. 
# It shouldn't make a difference since my weighted edgelist doesn't count direction
df_full_names["text"] = df_full_names["Name"] + " " + df_full_names["text"]

# save csv
df_full_names.to_csv(os.path.join("..", "data", "raw_data", "network_full_names_GOT.csv"))