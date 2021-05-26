#!/usr/bin/env python3
# Webscraping
from urllib.error import HTTPError #Handling errors
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.request import Request, urlopen
from bs4  import BeautifulSoup 

# System tool
import os

# Data processing
import pandas as pd

def main():
    # had problems webscraping the list of houses
    # solution found here:
    # https://stackoverflow.com/questions/13055208/httperror-http-error-403-forbidden 
    site = "https://awoiaf.westeros.org/index.php/List_of_Houses"
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(site,headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page)
    
    # Empty df for csv
    df = pd.DataFrame(columns=["region", "house"])
    houses = []
    regions = []
    # find row elements
    tr_elements = soup.find_all("tr")
    # loop through elements
    for element in tr_elements:
        # find reion and house
        region = element.findChildren()[0].getText().split()[0].lower()
        house = element.findChildren()[1].getText().split()[0].lower()
        # Create row and append to df
        
        #Some houses have different subhouses based on region
        # These should not be included
        if house not in houses:
            print(f"REGION {region}, HOUSE {house}")
            houses.append(house)
            regions.append(region)
    
    df["house"] = houses
    df["region"] = regions
    #This row is for unknown houses:
    df_row_unknown = {"region": "unknown", "house": "unknown"}
    df = df.append(df_row_unknown, ignore_index = True)
    df.to_csv(os.path.join("..", "data", "houses_regions.csv"), index = False)

if __name__ == "__main__":
    main()