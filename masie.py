import pandas as pd

# set up Hydra conf
#from omegaconf import DictConfig, OmegaConf
#import hydra

import myutils

class SeaIceRecord:
    csv_file_path: str
    column_names: list
    start_year: int
    end_year: int

    def __init__(self, csv_file_path: str, regions: list, start_year: int = 2007, end_year:int = 2022):
        self.csv_file_path = csv_file_path
        self.column_names = regions
        self.start_year = start_year
        self.end_year = end_year

    def masieDateStringToDate(self,data):
        # https://blog.hubspot.com/website/pandas-split-string
        # days = data['yyyyddd'].str[-3:]
        # years = data['yyyyddd'].str[0:3] 
        # data['day']= days
        # data['year'] = years

        try:
            # Convert the date string to datetime using the specified format
            date = pd.to_datetime(data['yyyyddd'], format='%Y%j')
            data['date']=date   #.strftime('%Y-%m-%d')  # Format the date as desired
            return data 
        except ValueError:
            return None  # Return None if the date string is not in the expected format

# Quick and dirty approach, see https://stackoverflow.com/a/73813430
# hydra.core.global_hydra.GlobalHydra.instance().clear() # see https://www.sscardapane.it/tutorials/hydra-tutorial/
# hydra.initialize(version_base=None, config_path="config")
# cfg = hydra.compose(config_name="config") 
# ToDo - replace with hydra initialisation of masie object

    def readmasie(self):

        try:
            # Read the masie CSV file into a Pandas DataFrame
            masie_df = pd.read_csv(self.csv_file_path)
            #print(masie_df)

            # select data from the marginal seas and central arctic only
            #column_names = [' (1) Beaufort_Sea',' (2) Chukchi_Sea',' (3) East_Siberian_Sea',' (4) Laptev_Sea',' (5) Kara_Sea',' (6) Barents_Sea',' (11) Central_Arctic']
            
            # Arguably should include Greenland Sea and Baffin Bay, but masie takes these quite far south 
            # https://nsidc.org/data/masie/explore-region
            # https://en.wikipedia.org/wiki/Polar_circle#/media/File:Arctic_circle.svg

            # sum the sie values in the specified column-names in the masie CSV
            masie_df['Marginal and Central']=masie_df[self.column_names].sum(axis=1)

            df = self.masieDateStringToDate(masie_df)
            #df[' (0) Northern_Hemisphere'] = myutils.normaliseList(df[' (0) Northern_Hemisphere'])
            df['Marginal and Central Normalised'] = myutils.normaliseList(df['Marginal and Central'])

            return df
            
        except pd.errors.EmptyDataError:
            print("The CSV file is empty.")
        except FileNotFoundError:
            print("The specified CSV file does not exist.")
        except pd.errors.ParserError:
            print("An error occurred while parsing the CSV file.")