# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 10:47:49 2019

@author: dwben
"""

# PP and Regular Goals
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


#################################

def PPandRegularGoals(df, dates):
    df["tag_4_length"] = df["tag_4"].str.len()
    df["tag_6_length"] = df["tag_6"].str.len()
    df["tag_9_length"] = df["tag_9"].str.len()
    df["tag_10_length"] = df["tag_10"].str.len()
    df["tag_11_length"] = df["tag_11"].str.len()
    
    for i in range(0,len(df)):
        if df.loc[i,"tag_4_length"] ==2:
            df.loc[i,'tag_3'] = df.loc[i,"tag_4"]
        elif df.loc[i,"tag_4_length"] == 4:#
            df.loc[i,'tag_3'] = df.loc[i,"tag_4"]#
        elif df.loc[i,"tag_6_length"] ==2:
            df.loc[i,'tag_3'] = df.loc[i,"tag_6"]
            df.loc[i,'tag_6'] = np.NaN
        else:
            df.loc[i,'tag_3'] = df.loc[i,"tag_3"]
            
    for i in range(0,len(df)):
        if df.loc[i,"tag_9_length"] > 2:
            df.loc[i,'tag_4'] = df.loc[i,"tag_9"]
        else:
            df.loc[i,'tag_4'] = df.loc[i,"tag_4"]
        
    for i in range(0,len(df)):
        if df.loc[i,"tag_10_length"] > 2:
            df.loc[i,'tag_5'] = df.loc[i,"tag_10"]
        else:
            df.loc[i,'tag_5'] = df.loc[i,"tag_5"]
        
    for i in range(0,len(df)):
        if df.loc[i,"tag_11_length"] > 2:
            df.loc[i,'tag_6'] = df.loc[i,"tag_11"]
        else:
            df.loc[i,'tag_6'] = df.loc[i,"tag_6"]
         
    df = df.iloc[:, 1:8]
    df
    df.columns = ['Period', 'Time in Period', "Team", "Type", 'Scorer', 'Assist1', 'Assist2']
    df['Period'] = df['Period'].str.strip('[')
             
        
    df['Period'] = df['Period'].replace("", np.NaN)
    df['Period'] = df['Period'].replace(" ", np.NaN)
    df['Period'] = df['Period'].fillna(method = 'ffill')
        
    df = df.dropna(thresh = 4).reset_index().drop(['index'], axis = 1)
    df['Scorer'], df['Season Goal Number'] = df['Scorer'].str.split('(',1).str
    df['Season Goal Number'] = df['Season Goal Number'].str.rstrip(')')
    df['Period'] = df['Period'].str.replace(r"[a-zA-Z]", "").str.strip().astype(int)
    df['Assist2'] = df['Assist2'].str.strip(' and ')
    df['Date'] = dates
        
    df["Time in Period (split)"] = df["Time in Period"].str.split(":")
    tags = df["Time in Period (split)"].apply(pd.Series)
    tags = tags.rename(columns = lambda x: 'tag_' + str(x))
    df = pd.concat([df[:], tags[:]], axis = 1)
        
    for i in range(0,len(df)):
        if df.loc[i,"Period"] == 1:
            df.loc[i,"tag_0"] = df.loc[i,"tag_0"]
        elif df.loc[i, "Period"] == 2:
            df.loc[i,"tag_0"] = str(int(df.loc[i,"tag_0"]) + 20)
        elif df.loc[i, "Period"] == 3:
            df.loc[i,"tag_0"] = str(int(df.loc[i,"tag_0"]) + 40)
    df["Time in Game"] = "00:" + df["tag_0"] + ":" + df["tag_1"]
    df['Time in Game'] = pd.to_datetime(df['Time in Game']).dt.time #The .dt is called a .dt accessor
    df = df.drop(["Time in Period (split)", "tag_0", "tag_1"], axis = 1)
    df['Time in Period'] = "00:" + df["Time in Period"]
    df['Time in Period'] = pd.to_datetime(df['Time in Period']).dt.time
    df["Date"] = str(dates)[:8]
    df["Date"] = pd.to_datetime(df["Date"])
    df["Home Team"] = str(dates)[9:]
    cleanedDF = df
    return cleanedDF    
    

######################
# Testing based on two games
######################
#date = ['201810030WSH', '201810080BOS'] #length of 15
date = ['201810170CGY', '201810270BOS'] #length of 14

game_list = []

for dates in date:
    url = f"https://www.hockey-reference.com/boxscores/{dates}.html#all_scoring"
    games_html = urlopen(url)
    #games_html = open(f"C:\\Users\\dbge\\OneDrive - Chevron\\Random\\{dates}.html")
    games_soup = BeautifulSoup(games_html, 'lxml')
        
    table = games_soup.find('table')
    rows = table.findAll('tr')
    str_cells = str(rows)
    cleantext = BeautifulSoup(str_cells, 'lxml').get_text()
        
    s = cleantext.split(',')
        
    for i in range(1,len(s)):
        s[i] = s[i].replace("\t", "")
        
    df = pd.DataFrame(s)
        
    df[0] = df[0].str.split('\n')
    tags = df[0].apply(pd.Series)
    tags = tags.rename(columns = lambda x: 'tag_' + str(x))
    df = pd.concat([df[:], tags[:]], axis = 1)
    df_width = len(df.columns)
    
    cleanedDF = PPandRegularGoals(df, dates)
    game_list.append(cleanedDF)
    
goals = pd.concat(game_list).reset_index().drop(columns = ['index'])