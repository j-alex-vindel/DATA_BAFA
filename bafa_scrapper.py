from logging.config import DEFAULT_LOGGING_CONFIG_PORT
from wsgiref import headers
import requests
from bs4 import BeautifulSoup
import pandas as pd


def w_scrap(url):
    html_text = requests.get(url).text
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
        game_date = data[game][0][:8]
        game_time = data[game][0][-5:]
        home = data[game][1]
        away = data[game][3]
        score_home = data[game][2].split('-')[0].rstrip()
        score_away = data[game][2].split('-')[1].lstrip()
        games['Game_Date'].append(game_date)
        games['Game_Time'].append(game_time)
        games['Home_team'].append(home)
        games['Away_team'].append(away)
        games['Home_score'].append(score_home)
        games['Away_score'].append(score_away)
        games['Division'].append(division)
    
    df = pd.DataFrame.from_dict(games)

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
    
