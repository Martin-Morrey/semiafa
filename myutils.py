# Utils module

import numpy as np
import sys
import pandas as pd

def normaliseList(my_list):
    # normalise a list of numbers, see https://www.statology.org/numpy-normalize-between-0-and-1/
    return  (my_list - np.min(my_list)) / (np.max(my_list) - np.min(my_list))

def maxAndMinsByDay(df, value_key, num_years, day_key='day'):
    output = dict()
    output['max'] = []
    output['min'] = []

    for y in range(num_years):
        start = y * 365
        end = start + 364
        year_data = df[df[day_key].between(start, end)]
        output['max'].append(year_data[value_key].max())
        output['min'].append(year_data[value_key].min())

    return output

def maxAndMinsByYear(df, value_key, start_year, num_years, day_key='day'):
    output = dict()
    output['max'] = []
    output['min'] = []
    output['year'] = []

    for y in range(num_years):
        year_string = str(start_year + y)
        print(year_string, file=sys.stderr)
        #year_data = df[df[day_key].between(start, end)]
        year_data = df[df["yyyyddd"].str.startswith(year_string)]
        output['max'].append(year_data[value_key].max())
        output['min'].append(year_data[value_key].min())
        output['year'].append(year_string)

    return output

def meanAbsoluteDifference(df1,index_key1,value_key1,df2,index_key2,value_key2):
    # Returns mean of absolute differences between two columns of different data frames
    # Applied to the common subset in a shared index, e.g. 'yyyyddd' date string
    # ToDo - defensive checks needed
    # --- check contents of index_key1 and index_key2 columns have some shared values
    # --- check value_key1 and value_key2 strings are different, and change one if not

    # make sure both specified keys are of same type
    df1[index_key1] = df1[index_key1].astype(str) # cast specified key to string
    df2[index_key2] = df2[index_key2].astype(str) # cast specified key to string

    # merge two data frames on shared index, giving the common subset https://datascience.stackexchange.com/a/53837
    merged_df = pd.merge(df1, df2, how='inner', left_on=index_key1, right_on=index_key2) 
    #print(merged_df, file=sys.stderr)

    # subtract the two columns and find the mean absolute value 
    result_df = pd.DataFrame()  
    result_df['diff'] = merged_df[value_key1] - merged_df[value_key2] # https://www.geeksforgeeks.org/how-to-subtract-two-columns-in-pandas-dataframe/
    result_df['abs'] = result_df['diff'].abs()
    #print(result_df, file=sys.stderr)
    
    return result_df['abs'].mean()





