from logging.config import DEFAULT_LOGGING_CONFIG_PORT
from wsgiref import headers
import requests
from bs4 import BeautifulSoup
import pandas as pd


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
            score_home = real_score[0]
            score_away = real_score[1]
            
        games['Game_Date'].append(game_date)
        games['Game_Time'].append(game_time)
        games['Home_team'].append(home)
        games['Away_team'].append(away)
        games['Home_score'].append(score_home)
        games['Away_score'].append(score_away)
        games['Division'].append(division)
    response.close()
    return games

# def savetable(tables,name):
    
#     base_dict = tables[0]

#     for index,d in enumerate(tables):
#         if index != 0:
#             for name, values in d.items():
#                 for value in values:
#                     base_dict[name].append(value)
                    
#     df = pd.DataFrame.from_dict(base_dict)
    
#     df.to_csv('%s.csv'%name,header=True)
    
#     return f"Table saved!"

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
  
