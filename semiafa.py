# SEMIAFA
# Simple Empirical Model of Ice Albedo Feedback in the Arctic

# ToDo:
# - check shade is never putting insolation into negative
# - make freezing rate dependent on (sqrt of) area of open sea
# - report minimum sea-ice extent by year
# - enable it to retain benefit from retaining multi-season ice?
# - (option to) calculate insolation in a separate step, for re-use in multiple runs?

# Load dependencies
import math
import numpy as np
import pandas as pd
import sys

# for insolation calculation in solarIrradiance()
import solarpy as sp
from datetime import datetime, timedelta, time

# set up Hydra conf
from omegaconf import DictConfig, OmegaConf
import hydra

# Read the config file
#hydra.initialize(version_base=None, config_path="config")
#cfg = hydra.compose(config_name="config") # https://stackoverflow.com/a/73813430

def getConfig():
    return cfg

# Define heat and melt calculation functions
def solarHeat(dayOfYear):
    return ( np.sin( (2*np.pi * dayOfYear/365) - (np.pi/2) ) + 1)/2

def solarMelt(sie,solarHeat,day_of_year):
    sea_area = 1 - (sie + shade(day_of_year))
    return cfg.sun_melt_multiplier * sea_area * solarHeat / 365
    # include albedo and sun-on-ice 
    #sea_melt = cfg.sun_melt_multiplier * sea_area * cfg.sea_albedo * solarHeat / 365  # ToDo - only apply when sea_melt > radiation_freeze
    #ice_melt = 0 # cfg.sun_melt_multiplier * sie * cfg.ice_albedo * solarHeat / 365
    #return sea_melt + ice_melt

def airHeat(day_of_year):
    lag = cfg.air_heat_lag
    return solarHeat(day_of_year - lag)

def airMelt(day_of_year):
    return cfg.air_melt_multiplier * airHeat(day_of_year) / 365

def shade(d):
    if d >= cfg.shade_start and d < cfg.shade_stop:
        return cfg.shade_area
    else:
        return 0

def windSpreadLoss(d):
    if d >= cfg.wind_spread_start and d < cfg.wind_spread_stop:
        return cfg.wind_spread_rate
    else:
        return 0

def oceanHeatMelt(sie):
    return cfg.ocean_heat_melt_multiplier * sie * (1/365)

def radiationFreeze(sie):
    sea_area = 1 - sie
    #return cfg.ice_freeze_multiplier * 1 / 365 # NOT influenced by area of open sea
    #return cfg.ice_freeze_multiplier * math.sqrt(sea_area) * 1 / 365 # partially influenced by area of open sea
    #return cfg.ice_freeze_multiplier * sea_area * 1 / 365 # directly influenced by area of open sea
    powered_sea_area = sea_area ** cfg.ice_power
    return cfg.ice_freeze_multiplier * (sea_area ** cfg.ice_power) * 1 / 365

def normaliseList(my_list):
    # normalise a list of numbers, see https://www.statology.org/numpy-normalize-between-0-and-1/
    return  (my_list - np.min(my_list)) / (np.max(my_list) - np.min(my_list))

def insolationByDayOfYear():
    lat = cfg.lat_for_insolation_calc
    insolation = []
    for day_num in range(365):

        # get data from day number, based on https://www.geeksforgeeks.org/python-convert-day-number-to-date-in-particular-year/
        day = str(day_num+1)
        day.rjust(3 + len(day), '0')
        date = datetime.strptime(str(cfg.insolation_year) + "-" + day, "%Y-%j") # .strftime("%m-%d-%Y") 

        # calc average insolation over 24 hours - see https://github.com/aqreed/solarpy/blob/master/examples/solar_irradiance.ipynb
        hours = [date + timedelta(hours=i) for i in range(0, 24)]
        G = [sp.beam_irradiance(0, time, lat) for time in hours]
        mean_G = sum(G) / len(G)
        insolation.append(mean_G)
    
    return normaliseList(insolation) #(insolation-np.min(insolation))/(np.max(insolation)-np.min(insolation))


def insolationByActualDate(start_year,num_years):
    lat = cfg.lat_for_insolation_calc
    insolation = []
    for num_year in range(num_years):
        year = start_year + num_year
        print(year, file=sys.stderr)
        for day_num in range(365):

            # get data from day number, based on https://www.geeksforgeeks.org/python-convert-day-number-to-date-in-particular-year/
            date_string = str(year) + str(day_num + 1).zfill(3)
            date = pd.to_datetime(date_string, format='%Y%j')

            # calc average insolation over 24 hours - see https://github.com/aqreed/solarpy/blob/master/examples/solar_irradiance.ipynb
            hours = [date + timedelta(hours=i) for i in range(0, 24)]
            G = [sp.beam_irradiance(0, time, lat) for time in hours]
            mean_G = sum(G) / len(G)
            print(date,mean_G, file=sys.stderr)
            insolation.append(mean_G)
    
    return normaliseList(insolation) #(insolation-np.min(insolation))/(np.max(insolation)-np.min(insolation))


# =================================== Pass the configuration and run the model ======================================================

# Decorator approach, won't work with a module that isn't defined in a folder with an __init__.py, see https://stackoverflow.com/a/70923074
#@hydra.main(version_base=None, config_path="config", config_name="config")
#def runModel(cfg: DictConfig):


# Quick and dirty approach, see https://stackoverflow.com/a/73813430
hydra.core.global_hydra.GlobalHydra.instance().clear() # see https://www.sscardapane.it/tutorials/hydra-tutorial/
hydra.initialize(version_base=None, config_path="config")
cfg = hydra.compose(config_name="config") 
# cfg = hydra.compose(config_name="config", overrides=["db=mysql", "db.user=me"])

def runModel(num_years = cfg.num_years):
    # time range
    #num_years = cfg.num_years

    # solar input
    #solarInput = ( np.sin( (2*np.pi * day/365) - (np.pi/2) ) + 1)/2
    #solarInput = solarHeat(day)

    #net_freeze_rate = cfg.ice_freeze_multiplier * (1/365) # should be influenced by area of open sea

    # Iterate over time period to model ice melt

    # Initialise properties -> put in init method for Class
    todays_sie = cfg.max_sie

    day_of_period = range(365 * num_years)
    data = dict()
    data['day'] = day_of_period
    data['sie'] = []
    data['solar_heat'] = []
    data['solar_melt'] = []
    data['ocean_melt'] = []
    data['air_melt'] = []
    data['wind_spread'] = []
    data['freeze'] = []
    data['date'] = []
    data['yyyyddd'] = []

    print('Calculating insolation', file=sys.stderr)
    insolation = insolationByDayOfYear()
    #insolation_by_day = insolationByActualDate(cfg.start_year,num_years)

    print('Running model over ' + str(num_years) + ' years', file=sys.stderr)

    for d in day_of_period:  # method - advanceOneDay
        num_year = d // 365 # floor divide
        day_of_year = d - (num_year * 365)

        # record the datetime for data comparisons
        date_string = str(cfg.start_year + num_year) + str(day_of_year + 1).zfill(3)
        data['yyyyddd'] = date_string
        date = pd.to_datetime(date_string, format='%Y%j')
        data['date'].append(date)

        # calculate melt factors
        #todays_solar_heat = solarHeat(d)
        todays_solar_heat = insolation[day_of_year] # insolation_by_day[d] 
        todays_solar_melt = solarMelt(todays_sie,todays_solar_heat,day_of_year) # NB: includes effect of shade
        todays_air_melt = airMelt(day_of_year)
        todays_wind_spread = windSpreadLoss(day_of_year)
        todays_ocean_melt = oceanHeatMelt(todays_sie)

        # record values
        data['solar_heat'].append(todays_solar_heat)
        data['solar_melt'].append(todays_solar_melt)
        data['ocean_melt'].append(todays_ocean_melt)
        data['air_melt'].append(todays_air_melt)
        data['wind_spread'].append(todays_wind_spread)

        # calculate provisional revised SIE 
        todays_sie_loss = todays_solar_melt + todays_air_melt + todays_wind_spread  + todays_ocean_melt
        provisional_sie = todays_sie - todays_sie_loss

        # use to calculate freeze component (to prevent oscillation at small SIE)
        todays_freeze = radiationFreeze(provisional_sie)
        data['freeze'].append(todays_freeze)

        # calculate revised SIE 
        todays_sie = todays_sie - todays_sie_loss + todays_freeze
        if todays_sie < cfg.min_sie:
            todays_sie = cfg.min_sie
        if todays_sie > cfg.max_sie:
            todays_sie = cfg.max_sie
        data['sie'].append(todays_sie)

    data['sea'] = np.subtract(1, data['sie'])

    
    print('Model finished', file=sys.stderr)

    return data

