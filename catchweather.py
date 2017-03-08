#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 16:55:51 2017

@author: joshua.cabanas
"""
import pandas as pd
import numpy as np
import os


def T2Str(x):
    #This fuction converts the existing observationtime to the right 
    #string for datetime parsing 
    if x < 10:
        return '0' + str(x) + '0000'
    else:
        return str(x) + '0000'
     
def getLoc():
    
    print 'do stuff' 


if __name__ == "__main__":
##
    path = '/home/ts-catapult.org.uk/joshua.cabanas/Catch/'
    jpath = '/home/ts-catapult.org.uk/joshua.cabanas/Catch/travelAIRData-master'

    #Loading the hourly met office historical weather data
    obs = pd.read_csv(os.path.join(path,'observations.csv'))
    #Removing significantweathercode missing values
    obs = obs.loc[obs.significantweathercode != -99]
    #combines the date and time to the right format
    obs['datetime'] = map(lambda x,y: str(x)[:8] + T2Str(y),obs.observationdate,obs.observationtime)
    #parses the datetime string to datetime object
    obs['datetime'] = pd.to_datetime(obs.datetime,format = '%Y%m%d%H%M%S')
    #combine the latitude and longtitude into a vector, the vector is stored as latlong feature
    obs['latlong'] = map(lambda x,y: np.array([[x,y]]),obs.latitude,obs.longitude)
    
    #deletes observationdate, observationtime, latitude and longitude  features
    del obs['observationdate'], obs['observationtime'], obs['latitude'], obs['longitude']

    wcodes = pd.read_csv(os.path.join(path,'WeatherCodes.csv'))
    wcodes.columns = ['significantweathercode','weathertype']


    Journey_files = [os.path.join(jpath,f) for f in os.listdir(jpath) if f.startswith('randJourneys') and f.endswith('csv')]
    
    Jdirection = {'from_weathertype':'from_latlong','to_weathertype':'to_latlong'}
    
    for j in Journey_files:
        
        jdat = pd.read_csv(j)
        
        jdat['from_latlong'] = map(lambda x,y: np.array([[x,y]]),jdat.from_locx,jdat.from_locy)
        jdat['to_latlong'] = map(lambda x,y: np.array([[x,y]]),jdat.to_locx,jdat.to_locy)
        
        jdat['rdatetime'] = pd.to_datetime(jdat.dateTime)
        jdat['rdatetime'] = pd.DatetimeIndex(jdat.dateTime).round('H')
        
        for k in Jdirection.keys():
            
            for i in range(len(jdat)-1):
                subset = obs.loc[obs.datetime == jdat.rdatetime.ix[i]]
                subset = subset.reset_index()
                ind = np.argmin([np.linalg.norm(jdat[Jdirection[k]].ix[i] - v) for v in subset.latlong])
                
                jdat['significantweathercode'] = subset.significantweathercode.ix[ind]
            
            
            jdat = jdat.merge(wcodes,on = 'significantweathercode',how = 'left')
            
            jdat.rename(columns={'weathertype':k}, inplace=True)
            del jdat['significantweathercode'] 
        
        
        
        k = j.strip('.csv') + '-W.csv'
        jdat.to_csv(k,index=False)

