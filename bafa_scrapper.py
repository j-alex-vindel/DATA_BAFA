from logging.config import DEFAULT_LOGGING_CONFIG_PORT
from wsgiref import headers
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
chromedriver_autoinstaller.install()


def table_scrap(url):
    response = requests.get(url)
    html_text = response.text
    soup = BeautifulSoup(html_text,'html.parser')
    # --- Returns a list of lists with the information of each game
    # [['date \r\n\t    \t14:00',home_team,score,away_team],....]
    data = []
    table = soup.find('table',attrs={'class':'fixed'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    division = soup.find('option',attrs={'value':'-1_-1'}).next_sibling.next_sibling.string
    
    games = {'Game_Date':[],'Game_Time':[],'Home_Team':[],'Away_Team':[],'Home_Score':[],
            'Away_score':[],'Division':[]}
    for game,entry in enumerate(data):
        game_date = re.findall("[0-9]{2}/[0-9]{2}/[0-9]{2}",game[0])
        game_time = re.findall("[0-9]{2}:[0-9]{2}",game[0])
        home = game[1]
        away = game[3]
        if game[2][0] not in [str(i) for i in range(10)]:
            if game[2][0] == 'A':
                score_home = 'A'
                score_away = 'W'
            elif game[2][0] == 'H':
                score_home = 'W'
                score_away - 'A'
        else:
            real_score = re.findall(r"\d+",game[2])
            score_home = int(real_score[0])
            score_away = int(real_score[1])
            
        games['Game_Date'].append(game_date)
        games['Game_Time'].append(game_time)
        games['Home_team'].append(home)
        games['Away_team'].append(away)
        games['Home_score'].append(score_home)
        games['Away_score'].append(score_away)
        games['Division'].append(division)
    response.close()
    return games

def division_names(base_url):
 
    r1 = requests.get(base_url)
    soup = BeautifulSoup(r1.text,'html.parser')

    divisions = []
    for title in soup.find('section',attrs={'id':'match-groups-section'}).find_all('a'):
        # print(f"Division : {title.text.strip()}")
        divisions.append(title.text.strip())
    r1.close()
    return divisions

def table_links(divisions,results_url):
    master_links = {}
    for division in divisions:
        print("="*20,f"{division}","="*20)
        driver = webdriver.Chrome()
        driver.get(results_url)
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

def addres_finder(sop):
    postcode = sop.address.find('span',attrs={'class':'uppercase'}).text
    name     = sop.h2.text
    if name[0] !='@' and name[1] != ' ':
        team_name = name
    elif name[0] == '@' and name[1] == ' ':
        team_name = name[2:]
    else:
        team_name = name[1:] 
    
    return postcode, team_name
def distance_crawler(pair,postcodedf,name):
    
    team_home,team_away = pair
    invpair = (team_away,team_home)
    p1 = postcodedf['PostCode'][postcodedf.Team_name.str.contains(team_home)].tolist()[0]
    p2 = postcodedf['PostCode'][postcodedf.Team_name.str.contains(team_away)].tolist()[0]
  
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches',['enable-logging'])
    driver = webdriver.Chrome(options=options)
    driver.get("http://www.postcode-distance.com/distance-between-postcodes")
    postcode1 = driver.find_element(By.XPATH,"//input[@id='zipcode1']")
    postcode1.send_keys(p1) 

    postcode2 = driver.find_element(By.XPATH,"//input[@id='zipcode2']")
    postcode2.send_keys(p2)

    distance_dd = driver.find_element(By.XPATH,"//select[@id='unit']")

    km_dd = Select(distance_dd)
    km_dd.select_by_visible_text('in km')
    time.sleep(5)
    driver.find_element(By.XPATH,"//input[@value='Calculate...']").click()
    time.sleep(5)
    if WebDriverWait(driver, 50).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@name='map']"))):
        # driver.switch_to.frame("map")
        time.sleep(5)
        result = driver.find_element(By.XPATH,"//div[@id='outputDiv']").get_attribute('innerText').split()
        # print(result)
        km_road = int(result[2])
        km_bee =  int(result[6])
    
    driver.switch_to.default_content()

    driver.quit()

    return pd.DataFrame.from_dict({'Teams':[pair,invpair],'Road_km':[km_road,km_road],'Bee_km':[km_bee,km_bee],'Division':[name,name]}) 

def division_distance(name):
    df = pd.read_csv('BAFA_2019_%s.csv'%name,index_col=False)
    postcodedf = pd.read_csv('BAFA_2019_Team_Venues.csv',index_col=False)
    teams = list(df['Home_Team'].unique())
    pairs = list(combinations(teams,2))
    master_dfs = []
    print('='*20,f"Division: {name}",'='*20)
    for pair in pairs:
        pairdf = distance_crawler(pair,postcodedf,name)
        master_dfs.append(pairdf)
    distance_df = pd.concat(master_dfs,ignore_index=True)
    distance_df.to_csv("BAFA_2019_D_%s.csv"%name,header=True,index=False)
    print(f"Division {name} saved (processed)!")
    
def geolocation_scrapp(postcode):
    base = 'https://api.getthedata.com/postcode/'
    p1 = base+postcode
    print(p1)
    response = requests.get(p1)
    p1 = response.json()
    if p1['status'] == 'match':
        latitude = p1['data']['latitude']
        longitude = p1['data']['longitude']
    else:
        latitude = 'N/A'
        longitude = 'N/A'
    return (latitude,longitude)
