# SEMIAFA
# Simple Empirical Model of Ice Albedo Feedback in the Arctic

# ToDo:
# - (option to) calculate insolation in a separate step, for re-use in multiple runs?
# - report insolation delta from shading for each year
# - add parameter to measure benefit from retaining multi-season ice 

# Load dependencies
import math
import numpy as np
import pandas as pd
import sys
import os.path
import pickle

# for insolation calculation in solarIrradiance()
import solarpy as sp
from datetime import datetime, timedelta

# import utility functions
import myutils

class Model:

    # declare types, to support checking with mypy etc https://www.kite.com/blog/python/type-hinting/
    num_years: int
    air_heat_lag: int
    air_melt_multiplier: float # useful range 3 - 5
    ice_power: float # 0 - 1
    ice_freeze_multiplier: float # useful range 4.5 -  , when ice_power is 0.5, 
    sun_melt_multiplier: float #10 # useful range 18 - 25
    lat_for_insolation_calc: float # representative latitude for approximate insolation
    max_sie: float 
    min_sie: float
    ocean_heat_melt_multiplier: float
    insolation_year: int
    insolation_file: str
    start_year: int
    wind_spread_start: int #  - first of each month J:1, F:32, M:60, A:91, M:121 
    wind_spread_stop: int # ~ 50,000 km2 by day 150, but highly variable
    wind_spread_rate: float # proportion of ice area exposed by wind daily, 5000km2 is ~0.00033
    real_area: float
    shade_on: bool
    shade_start: int
    shade_stop: int
    shade_area: float  # total area of ice cap approx 15,000,000 km2, shading 2000km2 is 0.000133r,
    data: dict

    def __init__(self,num_years: int, air_heat_lag: int, air_melt_multiplier: float, ice_power: float, ice_freeze_multiplier: float, sun_melt_multiplier: float, lat_for_insolation_calc: float, max_sie: float , min_sie: float, ocean_heat_melt_multiplier: float, insolation_year: int, insolation_file: str, start_year: int, wind_spread_start: int, wind_spread_stop: int, wind_spread_rate: float, real_area: float, shade_on: bool, shade_start: int, shade_stop: int, shade_area: float) -> None:

        # initialisation from Hydra config, see https://hydra.cc/docs/1.2/advanced/instantiate_objects/overview/
        self.num_years = num_years
        self.air_heat_lag = air_heat_lag
        self.air_melt_multiplier = air_melt_multiplier
        self.ice_power = ice_power
        self.ice_freeze_multiplier = ice_freeze_multiplier
        self.sun_melt_multiplier = sun_melt_multiplier
        self.lat_for_insolation_calc = lat_for_insolation_calc
        self.max_sie = max_sie
        self.min_sie = min_sie
        self.ocean_heat_melt_multiplier = ocean_heat_melt_multiplier
        self.insolation_year = insolation_year
        self.insolation_file = insolation_file
        self.start_year = start_year
        self.wind_spread_start = wind_spread_start 
        self.wind_spread_stop = wind_spread_stop
        self.wind_spread_rate = wind_spread_rate
        self.shade_on = shade_on
        self.shade_start = shade_start
        self.shade_stop = shade_stop
        self.shade_area = shade_area
   
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

    # Define heat and melt calculation functions
    # def solarHeat(self,dayOfYear):
    #      return ( np.sin( (2*np.pi * dayOfYear/365) - (np.pi/2) ) + 1)/2

    def solarMelt(self,sie,solarHeat,day_of_year):
        if self.shade_on:
            sea_area = 1 - (sie + self.shade(day_of_year))
            sea_area = (abs(sea_area) + sea_area)/2 # ensure sea area always a positive or zero
        else:
            sea_area = 1 - sie

        return self.sun_melt_multiplier * sea_area * solarHeat / 365

        # include albedo and sun-on-ice 
        #sea_melt = self.sun_melt_multiplier * sea_area * self.sea_albedo * solarHeat / 365  # ToDo - only apply when sea_melt > radiation_freeze
        #ice_melt = 0 # self.sun_melt_multiplier * sie * self.ice_albedo * solarHeat / 365
        #return sea_melt + ice_melt

    # def airHeat(self,day_of_year):
    #     lag = self.air_heat_lag
    #     return self.solarHeat(day_of_year - lag)

    # def airMelt(self,day_of_year):
    #     return self.air_melt_multiplier * self.airHeat(day_of_year) / 365

    def airHeatNew(self,insolation_df,current_date):
        lagged_date = current_date + timedelta(days=self.air_heat_lag) 
        date_string = lagged_date.strftime('%Y%j')  # .strftime("%m-%d-%Y")
        return self.getValueByDateString(insolation_df,date_string,'normalised-insolation')
         #return self.solarHeat(day_of_year - lag)

    def airMeltNew(self,insolation_df,current_date):
        return self.air_melt_multiplier * self.airHeatNew(insolation_df,current_date) / 365


    def shade(self,d):
        if d >= self.shade_start and d < self.shade_stop:
            return self.shade_area
        else:
            return 0

    def windSpreadLoss(self,d):
        if d >= self.wind_spread_start and d < self.wind_spread_stop:
            return self.wind_spread_rate
        else:
            return 0

    def oceanHeatMelt(self,sie):
        return self.ocean_heat_melt_multiplier * sie * (1/365)

    def radiationFreeze(self,sie):
        sea_area = 1 - sie
        #return self.ice_freeze_multiplier * 1 / 365 # NOT influenced by area of open sea
        #return self.ice_freeze_multiplier * math.sqrt(sea_area) * 1 / 365 # partially influenced by area of open sea
        #return self.ice_freeze_multiplier * sea_area * 1 / 365 # directly influenced by area of open sea
        powered_sea_area = sea_area ** self.ice_power
        return self.ice_freeze_multiplier * (sea_area ** self.ice_power) * 1 / 365

    # def normaliseList(my_list):
    #     # normalise a list of numbers, see https://www.statology.org/numpy-normalize-between-0-and-1/
    #     return  (my_list - np.min(my_list)) / (np.max(my_list) - np.min(my_list))

    def insolationByDayOfYear(self):
        print('Calculating insolation', file=sys.stderr)
        lat = self.lat_for_insolation_calc
        insolation = []
        for day_num in range(365):

            # get data from day number, based on https://www.geeksforgeeks.org/python-convert-day-number-to-date-in-particular-year/
            day = str(day_num+1)
            day.rjust(3 + len(day), '0')
            date = datetime.strptime(str(self.insolation_year) + "-" + day, "%Y-%j") # .strftime("%m-%d-%Y") 

            # calc average insolation over 24 hours - see https://github.com/aqreed/solarpy/blob/master/examples/solar_irradiance.ipynb
            hours = [date + timedelta(hours=i) for i in range(0, 24)]
            G = [sp.beam_irradiance(0, time, lat) for time in hours]
            mean_G = sum(G) / len(G)
            insolation.append(mean_G)
        
        return myutils.normaliseList(insolation) #(insolation-np.min(insolation))/(np.max(insolation)-np.min(insolation))


    def insolationByDatesInRange(self,start_date,end_date):
        # Calculate insolation over a date range,
        # Cache result in a .pkl file - see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_pickle.html
        # NB: Remove cached .pkl before changing any dataframe keys

        max_air_heat_lag = 43

        if (self.insolation_file != '' and os.path.exists(self.insolation_file)):
            insolation_df = pd.read_pickle(self.insolation_file)
            # ToDo: check if df covers required date range (inc possible lag settings), e.g. if (start_date_string in df['yyyyddd'].values
            return insolation_df 
        else:
            lat = self.lat_for_insolation_calc
            insolation = []
            insolation_df = pd.DataFrame()
            current_date = start_date - timedelta(days = max_air_heat_lag)
            lagged_end_date = end_date + timedelta(days = max_air_heat_lag)

            while current_date <= lagged_end_date:
                #print(current_date, file=sys.stderr)
                date_string = current_date.strftime('%Y%j')  # .strftime("%m-%d-%Y")
                # calc mean insolation over 24 hours - see https://github.com/aqreed/solarpy/blob/master/examples/solar_irradiance.ipynb
                hours = [current_date + timedelta(hours=i) for i in range(0, 24)]
                G = [sp.beam_irradiance(0, time, lat) for time in hours]
                mean_G = sum(G) / len(G)
                #print(current_date,mean_G, file=sys.stderr)
                insolation.append(mean_G)
                new_row = {'yyyyddd': date_string,'insolation':mean_G}
                insolation_df = insolation_df._append(new_row, ignore_index=True)

                current_date += timedelta(days=1)

            insolation_df['normalised-insolation'] = myutils.normaliseList(insolation_df['insolation'].values.tolist())
            if (self.insolation_file != ''):
                insolation_df.to_pickle(self.insolation_file)
            #return myutils.normaliseList(insolation) #(insolation-np.min(insolation))/(np.max(insolation)-np.min(insolation))
            return insolation_df
        
    def getValueByDateString(self,df,date_string,value_string):
        # value on date, see https://sparkbyexamples.com/pandas/pandas-extract-column-value-based-on-another-column
        #print('valueByDateString called for:' + date_string, file=sys.stderr)
        return df[df['yyyyddd']==date_string][value_string].values[0]

    # =================================== Pass the configuration and run the model ======================================================

    # Decorator approach, won't work with a module that isn't defined in a folder with an __init__.py, see https://stackoverflow.com/a/70923074
    #@hydra.main(version_base=None, config_path="config", config_name="config")
    #def runModel(cfg: DictConfig):


    def runModel(self): # ,num_years = self.num_years
        # solar input
        #solarInput = ( np.sin( (2*np.pi * day/365) - (np.pi/2) ) + 1)/2
        #solarInput = solarHeat(day)

        num_years = self.num_years

        # set up time period
        start_date = datetime(self.start_year,1,1)
        end_date   = datetime(year=(self.start_year + self.num_years -1) , month=12,  day=31)

        # Iterate over time period to model ice melt
        todays_sie = self.max_sie
        #insolation = self.insolationByDayOfYear()
        insolation_df = self.insolationByDatesInRange(start_date,end_date)

        print('Running model over ' + str(num_years) + ' years', file=sys.stderr)

        # Iterate over date range, see https://stackoverflow.com/a/63568640
        current_date = start_date
        d = 0

        while current_date <= end_date:

            year=current_date.year
            day_of_year = current_date.timetuple().tm_yday # integer 0 -364/5, see https://www.geeksforgeeks.org/timetuple-function-of-datetime-date-class-in-python/

            # record the datetime for data comparisons
            #date_string = str(self.start_year + num_year) + str(day_of_year + 1).zfill(3)
            date_string = str(year) + current_date.strftime('%j') # https://www.programiz.com/python-programming/datetime/strftime
            self.data['yyyyddd'].append(date_string)
            #date = pd.to_datetime(date_string, format='%Y%j')
            self.data['date'].append(current_date)

            # calculate melt factors
            #todays_solar_heat =  insolation_df[insolation_df['yyyyddd']==date_string]['normalised-insolation'].values[0] # insolation on date, see https://sparkbyexamples.com/pandas/pandas-extract-column-value-based-on-another-column
            todays_solar_heat = self.getValueByDateString(insolation_df,date_string,'normalised-insolation')
            todays_solar_melt = self.solarMelt(todays_sie,todays_solar_heat,day_of_year) # NB: includes effect of shade

            #todays_air_melt = self.airMelt(day_of_year)
            todays_air_melt = self.airMeltNew(insolation_df,current_date)

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
            if todays_sie < self.min_sie:
                todays_sie = self.min_sie
            if todays_sie > self.max_sie:
                todays_sie = self.max_sie
            self.data['sie'].append(todays_sie)

            # print(d,todays_sie, file=sys.stderr)
            # print(d,self.data['sie'][d], file=sys.stderr)

            d+=1
            current_date += timedelta(days=1)


        self.data['sea'] = np.subtract(1, self.data['sie'])

        
        print('Model finished', file=sys.stderr)

        return self.data

