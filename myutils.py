# Utils module

import numpy as np
import sys
import pandas as pd

# ================== Normalisation Functions =========================
# see https://www.statology.org/numpy-normalize-between-0-and-1/

def denormaliseList(normalised_list,source_list):
    # reverse the normaliseList process (below) for a list of normalised values
    return (normalised_list *  (np.max(source_list) - np.min(source_list)) + - np.min(source_list))

def denormaliseValue(normalised_value,source_min,source_max):
    # reverse the normaliseValue process (below) based on the properties of a list
    return ((normalised_value * (source_max - source_min)) + source_min)

def normaliseList(my_list):
    # normalise a list of numbers
    return  (my_list - np.min(my_list)) / (np.max(my_list) - np.min(my_list))

def normaliseValue(my_value,source_min,source_max):
    # normalise a number based on properties of a list
    return  (my_value - source_min) / (source_max - source_min)


# ================== Rescaling Functions =========================
# see https://medium.com/geekculture/scaling-vs-normalization-are-they-the-same-348035afe5ca

def deRescaleList(rescaled_list,source_list):
    # reverse the normaliseList process (below) for a list of normalised values
    return (rescaled_list * np.max(source_list) )

def deRescaleValue(rescaled_value,source_max):
    # reverse the normaliseValue process (below) based on the properties of a list
    return (rescaled_value * source_max)

def rescaleList(my_list):
    # rescale a list of quantities, 
    return  ( my_list / np.max(my_list) )

def rescaleValue(my_value,source_max):
    # rescale a quantity based on properties of a list
    return  (my_value / source_max )

# ======================================================================

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
        #print(year_string, file=sys.stderr)
        df["yyyyddd"] = df["yyyyddd"].astype(str) # make sure its a string
        year_data = df[df["yyyyddd"].str.startswith(year_string)]
        output['max'].append(year_data[value_key].max())
        output['min'].append(year_data[value_key].min())
        output['year'].append(year_string)

    return output

def statsByYear(df, value_key, start_year, num_years, day_key='day'):
    output = dict()
    output['max'] = []
    output['min'] = []
    output['sum'] = []
    output['mean'] = []
    output['year'] = []

    for y in range(num_years):
        year_string = str(start_year + y)
        #print(year_string, file=sys.stderr)
        df["yyyyddd"] = df["yyyyddd"].astype(str) # make sure its a string
        year_data = df[df["yyyyddd"].str.startswith(year_string)]
        output['max'].append(year_data[value_key].max())
        output['min'].append(year_data[value_key].min())
        output['sum'].append(np.sum(year_data[value_key]))
        output['mean'].append(np.mean(year_data[value_key]))
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


def timeboundCostFunction(df1,value_key1,df2,value_key2,start_year,end_year):
    # calculate absolute diff only for the years are interested in
    # assumes index key is 'yyyyddd'
    #mean_abs_diff = meanAbsoluteDifference(df1,index_key1,value_key1,df2,index_key2,value_key2)

    num_years = (end_year - start_year) - 1

    # calculate a diff for each year separately
    diff = []
    for y in range(num_years):
        year_string = str(start_year + y)
        #print(year_string, file=sys.stderr)
        df1["yyyyddd"] = df1["yyyyddd"].astype(str) # make sure its a string
        df2["yyyyddd"] = df2["yyyyddd"].astype(str) # make sure its a string
        year_data_1 = df1[df1["yyyyddd"].str.startswith(year_string)]
        year_data_2 = df2[df2["yyyyddd"].str.startswith(year_string)]
        diff.append(meanAbsoluteDifference(year_data_1,'yyyyddd',value_key1,year_data_2,'yyyyddd',value_key2))

    return sum(diff) / len(diff) # return mean diff over all the years in the range