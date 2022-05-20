import multiprocessing
import os
from bafa_scrapper import distance_crawler,division_distance

divisions = ['NFC 1 North','NFC 1 South','NFC 2 North','NFC 2 South','NFC 2 West','Premiership North',
'Premiership South','SFC 1 East','SFC 1 West','SFC 2 North','SFC 2 South','SFC 2 West']

if __name__ == '__main__':
    processes = [multiprocessing.Process(target=division_distance,args=[filename]) 
    for filename in divisions]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

