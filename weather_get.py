import pandas as pd
import requests
import creds

def filewriter(filename,key):
    masterdf = pd.read_csv(filename)
    indeces = masterdf['Index'].tolist()
    venues = pd.read_csv('BAFA_2019_Team_Venues.csv')
    games = pd.read_csv('BAFA_2019_Games.csv')

    # transform the dates into the dates the API will accept
    games['Game_Date'] = pd.to_datetime(games['Game_Date'])
    games['game_date'] = games['Game_Date'].dt.strftime('%Y-%m-%d')

    
    for i in range(len(games)):
        results = {'Index':[],'Temp':[],'Humidity':[],'Windspeed':[],
    'Visibility':[],'Precipitation':[],'Cast':[]} 
        if i not in indeces:
            print(f"game {i} -at {games['Home_Team'].loc[i]} -> {games.loc[i]['game_date']}")
            date = f"{games.loc[i]['game_date']}T{games.loc[i]['Game_Time']}:00"
            lat =  f"{venues['Lat'].loc[venues.loc[venues['Team_name'] == games.loc[i]['Home_Team']].index[0]]}"
            long = f"{venues['Long'].loc[venues.loc[venues['Team_name'] == games.loc[i]['Home_Team']].index[0]]}"
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{long}/{date}?key={key}"
            response = requests.get(url)
            if response.status_code == 200:
                info = response.json()
                feelslike = info['days'][0]['feelslike']
                humidity = info['days'][0]['humidity']
                windspeed = info['days'][0]['windspeed']
                visibility = info['days'][0]['visibility']
                precip = info['days'][0]['precip']
                cast = info['days'][0]['icon']
                results['Index'].append(i)
                results['Temp'].append(feelslike)
                results['Humidity'].append(humidity)
                results['Windspeed'].append(windspeed)
                results['Visibility'].append(visibility)
                results['Precipitation'].append(precip)
                results['Cast'].append(cast)

                dfaux = pd.DataFrame.from_dict(results)
                dfaux.to_csv(filename,mode='a',index=False,header=False)
            else:
                print(f'Requests Terminated!! on {i}')
                break
        

filewriter('BAFA_Game_Weather.csv',creds.a_key)
            