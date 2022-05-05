import requests
from bs4 import BeautifulSoup
import pandas as pd
from bafa_scrapper import addres_finder


initial_url = 'https://bafanle.leaguerepublic.com/venues.html'
html_text = requests.get(initial_url).text
form_soup = BeautifulSoup(html_text,'html.parser')

values = []
for value in form_soup.find('form').find_all('option'):
    values.append(value.attrs.get('value',''))

venues = {'Team_name':[],'PostCode':[]}

for value in values:
    team = {'selectedVenueID':value}
    r = requests.get(initial_url,params=team)
    team_soup = BeautifulSoup(r.text,'html.parser')

    zipcode, teamname = addres_finder(team_soup)

    venues['PostCode'].append(zipcode)
    venues['Team_name'].append(teamname)

df = pd.DataFrame.from_dict(venues)

df.to_csv('team_venues.csv',header=True)



