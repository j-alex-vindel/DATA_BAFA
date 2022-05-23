import pandas as pd
from bafa_scrapper import geolocation_scrapp

venues = pd.read_csv('BAFA_2019_Team_Venues.csv')
latitudes = []
longitudes = []
latlong = []
for index, postode in enumerate(venues.PostCode):
    
    geos = geolocation_scrapp(postode)
    print(f"{index} -> {geos}")
    latitudes.append(geos[0])
    longitudes.append(geos[1])
    latlong.append(geos)

venues['Lat'] = latitudes
venues['Long'] = longitudes
venues['geo'] = latlong

venues.to_csv('BAFA_2019_Team_Venues.csv',header=True,index=False)
venues.to_pickle('BAFA_2019_Team_Venues.pkl')
