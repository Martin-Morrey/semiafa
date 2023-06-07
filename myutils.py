# Utils module

import numpy as np

def normaliseList(my_list):
    # normalise a list of numbers, see https://www.statology.org/numpy-normalize-between-0-and-1/
    return  (my_list - np.min(my_list)) / (np.max(my_list) - np.min(my_list))
