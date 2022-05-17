import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
from bafa_scrapper import table_scrap, division_names, table_links
import pandas as pd

base = 'https://bafanle.leaguerepublic.com/index.html'

results_url = 'https://bafanle.leaguerepublic.com/fg/1_567612366.html'

divisions = division_names(base)

master_links = table_links(divisions, results_url)

master_list = []

for name in master_links.keys():
    division_list = []
    print(f" -> Division {name}")
    table_url = master_links[name]['1']
    table1 = table_scrap(table_url)
    division_list.append(table1)
    if master_links[name]['2'] != None:
        table2_url = master_links[name]['2']
        table2 = table_scrap(table2_url)
        division_list.append(table2)

    division_df = pd.concat(division_list,ignore_index=True)
    division_df.to_csv('%s.csv'%name,header=True)
    
    master_list.append(division_df)
    
master_df = pd.concat(master_list,ignore_index=True)
master_df.to_csv('BAFA_2019.csv',header=True)
