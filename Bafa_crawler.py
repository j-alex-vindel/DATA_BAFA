import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
from bafa_scrapper import table_scrap, division_names, table_links
import pandas as pd

base = 'https://bafanle.leaguerepublic.com/index.html'

results_url = 'https://bafanle.leaguerepublic.com/fg/1_567612366.html'

divisions = division_names(base)

master_links = table_links(divisions, results_url)

df = pd.DataFrame(columns=['Game_Date','Game_Time','Home_Team','Away_Team','Home_Score','Away_Score','Division'])
for name in master_links.keys():
    table_url = master_links[name]['1']
    table1 = table_scrap(table_url)
    print(f"->> Dvision {name}")
    print('->',table1)
    df.append(table1,ignore_index=True)
    if master_links[name]['2'] != None:
        table2_url = master_links[name]['2']
        table2 = table_scrap(table2_url)
        print('->',table2)
        df.append(table2,ignore_index=True)
        print(f"->> {table_url},'\n', ->>{table2_url}")
