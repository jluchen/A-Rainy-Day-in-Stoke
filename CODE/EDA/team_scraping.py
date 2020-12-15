import pandas as pd
import numpy as np

import sys
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

### Use get_data1 for all BUT Fifa World Cup, Euros (both M and W)
def get_data1(league_dict,code,league,gender,driver_url=None):
    ### Inputs:
    # driver_url: local location of Chromedriver for Selenium
    # league_dict: dictionary {year:url code}
    # >>> for all years to be scraped for the league along with unique fbref.com URL CODE for season
    # code: integer with unique fbref.com URL CODE for league
    # league: string with Full League Name
    # gender: string "M" or "F"

    try:
        driver = webdriver.Chrome(driver_url)
    except:
        print("Need Accurate Location of Chromedriver in PATH")
        return None
    delay = 3
    data_types = ['standard', 'keeper', 'shooting', 'playing_time', 'misc']
    
    df_list = []
    for year in league_dict:
        print('NEW YEAR: ', year)
        year_df = pd.DataFrame()
        url = "https://fbref.com/en/comps/"+ str(code) + "/" + str(league_dict[year])
        for type in data_types:
            #print(code)
            #url = "https://fbref.com/en/comps/"+ str(code) + "/" + str(league_dict[year]) + "/" + type[0] + "/"
            #print(url)
            try:
                driver.get(url)
                #print('hi')
                myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'all_stats_'+type+'_squads')))
                #print(myElem)
                df = pd.read_html(myElem.get_attribute('outerHTML'))[0]
                #print(type[1], len(df))
                for col in df.columns:
                    year_col = col
                    if 'Unnamed' in col[0]:
                        year_col =  col[1]
                    if year_col not in year_df.columns:
                        year_df[year_col] = df[col]
            except Exception as e:
                print('not found')
                print(year, type)
        
        #try:
        #    year_df.drop(labels = list(range(25, len(year_df), 26)), axis = 0, inplace = True)
        #    year_df.drop(labels = 'Matches', axis = 1, inplace = True)
        #except:
        #    print('idfk')

        year_df['Season'] = str(year)
        year_df['League'] = league
        year_df['Gender'] = gender
        df_list.append(year_df)
        
    driver.quit()
    full_df = pd.concat(df_list, axis = 0, join = "outer", sort = False)
    return full_df

### Use get_data2 for Fifa World Cup, Euros (both M and W)
def get_data2(league_dict,code,league,gender,driver_url=None):
    ### Inputs:
    # driver_url: local location of Chromedriver for Selenium
    # league_dict: dictionary {year:url code}
    # >>> for all years to be scraped for the league along with unique fbref.com URL CODE for season
    # code: integer with unique fbref.com URL CODE for league
    # league: string with Full League Name
    # gender: string "M" or "F"

    try:
        driver = webdriver.Chrome(driver_url)
    except:
        print("Need Accurate Location of Chromedriver in PATH")
        return None
    delay = 3

    data_types = [['stats', 'standard'], ['keepers', 'keeper'], ['shooting', 'shooting'],
                  ['playingtime','playing_time'],['misc', 'misc']]
    #data_types = ['standard', 'keeper', 'shooting', 'playing_time', 'misc']
    df_list = []
    for year in league_dict:
        print('NEW YEAR: ', year)
        year_df = pd.DataFrame()
        #url = "https://fbref.com/en/comps/"+ str(code) + "/" + str(league_dict[year])
        for type in data_types:
            #print(code)
            url = "https://fbref.com/en/comps/"+ str(code) + "/" + str(league_dict[year]) + "/" + type[0] + "/"
            #print(url)
            try:
                driver.get(url)
                #print('hi')
                #myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'all_stats_'+type+'_squads')))
                myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'all_stats_'+type[1]+'_squads')))
                #print(myElem)
                df = pd.read_html(myElem.get_attribute('outerHTML'))[0]
                #print(type[1], len(df))
                for col in df.columns:
                    year_col = col
                    if 'Unnamed' in col[0]:
                        year_col =  col[1]
                    if year_col not in year_df.columns:
                        year_df[year_col] = df[col]
            except Exception as e:
                print('not found')
                print(year, type)
        
        #try:
        #    year_df.drop(labels = list(range(25, len(year_df), 26)), axis = 0, inplace = True)
        #    year_df.drop(labels = 'Matches', axis = 1, inplace = True)
        #except:
        #    print('idfk')

        year_df['Season'] = str(year)
        year_df['League'] = league
        year_df['Gender'] = gender
        df_list.append(year_df)
        
    driver.quit()
    full_df = pd.concat(df_list, axis = 0, join = "outer", sort = False)
    return full_df

def main():
    ### NEED LOCAL LOCATION OF CHROME WEBDRIVER
    if (len(sys.argv)-1) > 0:
        driver_url_ex = sys.argv[1] #update this line !!!

        ### League Dictionary/ies:
        men_fifa_years = {2002:17, 2018:''} # example
        mls_years = {1996:30, 2019:2798}

        testdf1 = get_data1(mls_years, 22, "MLS", "M",driver_url_ex)
        testdf1.to_csv("example_team.csv")

        testdf2 = get_data2(men_fifa_years, 1, "FIFA World Cup", "M",driver_url_ex)
        testdf2.to_csv("example_team2.csv")

    else:
        print("Need Location of Chromedriver in PATH")

if __name__ == '__main__':
    main()
    print()
    print("Terminated")