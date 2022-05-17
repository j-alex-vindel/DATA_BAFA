import requests
from bs4 import BeautifulSoup
from requests.compat import urljoin
import time
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
chromedriver_autoinstaller.install()
from bafa_scrapper import w_scrap
import pandas as pd

def division_names():
    base = 'https://bafanle.leaguerepublic.com/index.html'
    r1 = requests.get(base)
    soup = BeautifulSoup(r1.text,'html.parser')

    divisions = []
    for title in soup.find('section',attrs={'id':'match-groups-section'}).find_all('a'):
        # print(f"Division : {title.text.strip()}")
        divisions.append(title.text.strip())
    r1.close()
    return divisions

def table_links(divisions):
    master_links = {}
    for division in divisions:
        print("="*20,f"{division}","="*20)
        driver = webdriver.Chrome()
        driver.get('https://bafanle.leaguerepublic.com/fg/1_567612366.html')
        division_dropdown =  driver.find_element(By.NAME,"fixtureGroupPageContent.filterFixtureGroupKey")
        try:
            dd = Select(division_dropdown)
            dd.select_by_visible_text(division)
            viewresults = driver.find_element(By.XPATH,"//a[normalize-space()='View All Results']")
            viewresults.click() 
            link1 = driver.current_url
            master_links[division] = {'1':link1,'2':None}
            print(f" -> Table 1")
            try:
                page2 = driver.find_element(By.XPATH,"//a[normalize-space()='2']")
                page2.click()
                link2 = driver.current_url
                master_links[division].update({'2':link2})

                print(f"-> Table 2")
            except:
                print(f"-> Division: {division} only has one table")
        
        except:
            print(f"!!!! Division: {division} Not played in 2019 !!!!")
    driver.close()
    return master_links
  
divisions = division_names()

master_links = table_links(divisions)

df = pd.DataFrame(columns=['Game_Date','Game_Time','Home_Team','Away_Team','Home_Score','Away_Score','Division'])
for name in master_links.keys():
    table_url = master_links[name]['1']
    table1 = w_scrap(table_url)
    print(f"->> Dvision {name}")
    print('->',table1)
    df.append(table1,ignore_index=True)
    if master_links[name]['2'] != None:
        table2_url = master_links[name]['2']
        table2 = w_scrap(table2_url)
        print('->',table2)
        df.append(table2,ignore_index=True)
        print(f"->> {table_url},'\n', ->>{table2_url}")
