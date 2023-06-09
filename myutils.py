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

    # make sure both specified keys are of same type
    df1[index_key1] = df1[index_key1].astype(str) # cast specified key to string
    df2[index_key2] = df2[index_key2].astype(str) # cast specified key to string
    # print(df1, file=sys.stderr)
    # print(df2, file=sys.stderr)

    # # filter df2 by keys in df1 
    # keys1 = df1[index_key1].values.tolist() # https://datatofish.com/convert-pandas-dataframe-to-list/
    # keys2 = df2[index_key2].values.tolist()

    # #print(keys, file=sys.stderr)
    # #filter = df2[index_key2].isin(keys) # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.isin.html
    # #print (filter, file=sys.stderr)

    # df2_filtered = df2[df2[index_key2].isin(keys1)] # https://www.statology.org/pandas-filter-in-list/
    # df2_filtered = df2_filtered.reset_index()
    # print(df2_filtered, file=sys.stderr)

    merged_df = pd.merge(df1, df2, how='inner', left_on=index_key1, right_on=index_key2) # https://datascience.stackexchange.com/a/53837
    print(merged_df, file=sys.stderr)

    # calculate result
    result_df = pd.DataFrame()
    #result_df['diff'] = df1[value_key1] - df2_filtered[value_key2] # https://www.geeksforgeeks.org/how-to-subtract-two-columns-in-pandas-dataframe/

    result_df['diff'] = merged_df[value_key1] - merged_df[value_key2]
    result_df['abs'] = result_df['diff'].abs()
    print(result_df, file=sys.stderr)
    
    return result_df['abs'].mean()





