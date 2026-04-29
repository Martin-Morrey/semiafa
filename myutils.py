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


# def meanTopBiasedAbsoluteDifference(df1,index_key1,value_key1,df2,index_key2,value_key2):
#     # Returns mean of absolute differences between two columns of different data frames
#     # Applied to the common subset in a shared index, e.g. 'yyyyddd' date string
#     # ToDo - defensive checks needed
#     # --- check contents of index_key1 and index_key2 columns have some shared values
#     # --- check value_key1 and value_key2 strings are different, and change one if not

#     # make sure both specified keys are of same type
#     df1[index_key1] = df1[index_key1].astype(str) # cast specified key to string
#     df2[index_key2] = df2[index_key2].astype(str) # cast specified key to string

#     # merge two data frames on shared index, giving the common subset https://datascience.stackexchange.com/a/53837
#     merged_df = pd.merge(df1, df2, how='inner', left_on=index_key1, right_on=index_key2) 
#     #print(merged_df, file=sys.stderr)

#     # subtract the two columns and find the absolute value 
#     result_df = pd.DataFrame()  
#     result_df['diff'] = merged_df[value_key1] - merged_df[value_key2] # https://www.geeksforgeeks.org/how-to-subtract-two-columns-in-pandas-dataframe/
#     result_df['abs'] = result_df['diff'].abs()

#     # multiply by the mean of the two columns to top-bias the result
#     result_df['mean'] = (merged_df[value_key1] - merged_df[value_key2])/2
#     result_df['top-biased'] = (result_df['abs'] * result_df['mean'])**(1/8)

#     #print(result_df, file=sys.stderr)
    
#     return result_df['top-biased'].mean()

  
def adjustedCostFunction(df1,index_key1,value_key1,df2,index_key2,value_key2,start_year,end_year,weight):
    # called with meanDiff = myutils.meanAbsoluteDifference(masie_df,'yyyyddd','Marginal and Central Normalised',model_data_df,'yyyyddd','sie')

    mean_abs_diff = meanAbsoluteDifference(df1,index_key1,value_key1,df2,index_key2,value_key2)

    num_years = (end_year - start_year) - 1

    # 'Marginal and Central Normalised'
    sie_minmax_masie = maxAndMinsByYear(df1,value_key1,start_year,num_years)
    sie_minmax_model = maxAndMinsByYear(df2,value_key2,start_year,num_years)

    total_model_shortfall = 0
    for y in range(num_years):
        max_masie = sie_minmax_masie['max'][y]
        max_model = sie_minmax_model['max'][y]
        shortfall = max_masie - max_model
        total_model_shortfall += (shortfall + abs(shortfall))/2 # 0 if model > masie

    mean_model_shortfall = total_model_shortfall / num_years
    adjustment = mean_model_shortfall * weight

    return mean_abs_diff + adjustment

