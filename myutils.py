# Utils module

import numpy as np

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
