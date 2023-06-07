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

# import utility functions
import myutils

class Model:

    def __init__(self):
        # Quick and dirty approach, see https://stackoverflow.com/a/73813430
        hydra.core.global_hydra.GlobalHydra.instance().clear() # see https://www.sscardapane.it/tutorials/hydra-tutorial/
        hydra.initialize(version_base=None, config_path="config")
        self.cfg = hydra.compose(config_name="config") 
        # cfg = hydra.compose(config_name="config", overrides=["db=mysql", "db.user=me"])

        self.data = dict()
        self.data['day'] = []
        self.data['sie'] = []
        self.data['solar_heat'] = []
        self.data['solar_melt'] = []
        self.data['ocean_melt'] = []
        self.data['air_melt'] = []
        self.data['wind_spread'] = []
        self.data['freeze'] = []
        self.data['date'] = []
        self.data['yyyyddd'] = []

    # Read the config file
    #hydra.initialize(version_base=None, config_path="config")
    #cfg = hydra.compose(config_name="config") # https://stackoverflow.com/a/73813430

    def getConfig(self):
        return self.cfg

    # Define heat and melt calculation functions
    def solarHeat(self,dayOfYear):
        return ( np.sin( (2*np.pi * dayOfYear/365) - (np.pi/2) ) + 1)/2

    def solarMelt(self,sie,solarHeat,day_of_year):
        sea_area = 1 - (sie + self.shade(day_of_year))
        return self.cfg.sun_melt_multiplier * sea_area * solarHeat / 365
        # include albedo and sun-on-ice 
        #sea_melt = self.cfg.sun_melt_multiplier * sea_area * self.cfg.sea_albedo * solarHeat / 365  # ToDo - only apply when sea_melt > radiation_freeze
        #ice_melt = 0 # self.cfg.sun_melt_multiplier * sie * self.cfg.ice_albedo * solarHeat / 365
        #return sea_melt + ice_melt

    def airHeat(self,day_of_year):
        lag = self.cfg.air_heat_lag
        return self.solarHeat(day_of_year - lag)

    def airMelt(self,day_of_year):
        return self.cfg.air_melt_multiplier * self.airHeat(day_of_year) / 365

    def shade(self,d):
        if d >= self.cfg.shade_start and d < self.cfg.shade_stop:
            return self.cfg.shade_area
        else:
            return 0

    def windSpreadLoss(self,d):
        if d >= self.cfg.wind_spread_start and d < self.cfg.wind_spread_stop:
            return self.cfg.wind_spread_rate
        else:
            return 0

    def oceanHeatMelt(self,sie):
        return self.cfg.ocean_heat_melt_multiplier * sie * (1/365)

    def radiationFreeze(self,sie):
        sea_area = 1 - sie
        #return self.cfg.ice_freeze_multiplier * 1 / 365 # NOT influenced by area of open sea
        #return self.cfg.ice_freeze_multiplier * math.sqrt(sea_area) * 1 / 365 # partially influenced by area of open sea
        #return self.cfg.ice_freeze_multiplier * sea_area * 1 / 365 # directly influenced by area of open sea
        powered_sea_area = sea_area ** self.cfg.ice_power
        return self.cfg.ice_freeze_multiplier * (sea_area ** self.cfg.ice_power) * 1 / 365

    # def normaliseList(my_list):
    #     # normalise a list of numbers, see https://www.statology.org/numpy-normalize-between-0-and-1/
    #     return  (my_list - np.min(my_list)) / (np.max(my_list) - np.min(my_list))

    def insolationByDayOfYear(self):
        print('Calculating insolation', file=sys.stderr)
        lat = self.cfg.lat_for_insolation_calc
        insolation = []
        for day_num in range(365):

            # get data from day number, based on https://www.geeksforgeeks.org/python-convert-day-number-to-date-in-particular-year/
            day = str(day_num+1)
            day.rjust(3 + len(day), '0')
            date = datetime.strptime(str(self.cfg.insolation_year) + "-" + day, "%Y-%j") # .strftime("%m-%d-%Y") 

            # calc average insolation over 24 hours - see https://github.com/aqreed/solarpy/blob/master/examples/solar_irradiance.ipynb
            hours = [date + timedelta(hours=i) for i in range(0, 24)]
            G = [sp.beam_irradiance(0, time, lat) for time in hours]
            mean_G = sum(G) / len(G)
            insolation.append(mean_G)
        
        return myutils.normaliseList(insolation) #(insolation-np.min(insolation))/(np.max(insolation)-np.min(insolation))


    def insolationByActualDate(self,start_year,num_years):
        lat = self.cfg.lat_for_insolation_calc
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
        
        return myutils.normaliseList(insolation) #(insolation-np.min(insolation))/(np.max(insolation)-np.min(insolation))


    # =================================== Pass the configuration and run the model ======================================================

    # Decorator approach, won't work with a module that isn't defined in a folder with an __init__.py, see https://stackoverflow.com/a/70923074
    #@hydra.main(version_base=None, config_path="config", config_name="config")
    #def runModel(cfg: DictConfig):


    def runModel(self): # ,num_years = self.cfg.num_years
        # solar input
        #solarInput = ( np.sin( (2*np.pi * day/365) - (np.pi/2) ) + 1)/2
        #solarInput = solarHeat(day)

        num_years = self.cfg.num_years

        day_of_period = range(365 * num_years)

        # Iterate over time period to model ice melt
        todays_sie = self.cfg.max_sie
        insolation = self.insolationByDayOfYear()
        #insolation_by_day = insolationByActualDate(self.cfg.start_year,num_years)

        print('Running model over ' + str(num_years) + ' years', file=sys.stderr)

        for d in day_of_period:  # method - advanceOneDay
            num_year = d // 365 # floor divide
            day_of_year = d - (num_year * 365)

            # record the datetime for data comparisons
            date_string = str(self.cfg.start_year + num_year) + str(day_of_year + 1).zfill(3)
            self.data['yyyyddd'] = date_string
            date = pd.to_datetime(date_string, format='%Y%j')
            self.data['date'].append(date)

            # calculate melt factors
            #todays_solar_heat = solarHeat(d)
            todays_solar_heat = insolation[day_of_year] # insolation_by_day[d] 
            todays_solar_melt = self.solarMelt(todays_sie,todays_solar_heat,day_of_year) # NB: includes effect of shade
            todays_air_melt = self.airMelt(day_of_year)
            todays_wind_spread = self.windSpreadLoss(day_of_year)
            todays_ocean_melt = self.oceanHeatMelt(todays_sie)

            # record values
            self.data['day'].append(d)
            self.data['solar_heat'].append(todays_solar_heat)
            self.data['solar_melt'].append(todays_solar_melt)
            self.data['ocean_melt'].append(todays_ocean_melt)
            self.data['air_melt'].append(todays_air_melt)
            self.data['wind_spread'].append(todays_wind_spread)

            # calculate provisional revised SIE 
            todays_sie_loss = todays_solar_melt + todays_air_melt + todays_wind_spread  + todays_ocean_melt
            provisional_sie = todays_sie - todays_sie_loss

            # use to calculate freeze component (to prevent oscillation at small SIE)
            todays_freeze = self.radiationFreeze(provisional_sie)
            self.data['freeze'].append(todays_freeze)

            # calculate revised SIE 
            todays_sie = todays_sie - todays_sie_loss + todays_freeze
            if todays_sie < self.cfg.min_sie:
                todays_sie = self.cfg.min_sie
            if todays_sie > self.cfg.max_sie:
                todays_sie = self.cfg.max_sie
            self.data['sie'].append(todays_sie)

            # print(d,todays_sie, file=sys.stderr)
            # print(d,self.data['sie'][d], file=sys.stderr)

        self.data['sea'] = np.subtract(1, self.data['sie'])

        
        print('Model finished', file=sys.stderr)

        return self.data

