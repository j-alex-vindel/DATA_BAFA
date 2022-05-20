import multiprocessing
import os
from bafa_scrapper import distance_crawler,division_distance
import pandas as pd

divisions = ['NFC 1 North','NFC 1 South','NFC 2 North','NFC 2 South','NFC 2 West','Premiership North',
'Premiership South','SFC 1 East','SFC 1 West','SFC 2 North','SFC 2 South','SFC 2 West']

if __name__ == '__main__':
    processes = [multiprocessing.Process(target=division_distance,args=[filename]) 
    for filename in divisions]

    for process in processes:
        process.start()

    for process in processes:
        process.join()
        
    master_dist = []
    for division in divisions:
        dispdf = pd.read_csv('BAFA_2019_D_%s.csv'%division,index_col=False)
        master_dist.append(dispdf)
    master_distance_df = pd.concat(master_dist,ignore_index=True)
    
    master_distance_df.to_csv('BAFA_D_2019_All.csv',header=True,index=False)
    master_distance_df.to_pickle('BAFA_2029_D_All.pkl')
