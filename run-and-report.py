import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import semiafa

def plotResults(model):
    # Plot the result 
    fig, ax = plt.subplots()
    data = model.data
    # ice and sea extent
    ax.plot(data['day'], data['sie'], label='sea ice extent')
    #ax.plot(data['day'], data['sea'], label='area of open sea')

    # insolation
    #ax.plot(data['day'], data['solar_heat'], label='solar heat')

    # ice deltas
    # ax.plot(data['day'], data['solar_melt'], label='solar melt')
    # ax.plot(data['day'], data['air_melt'], label='air heat melt')
    # ax.plot(data['day'], data['wind_spread'], label='wind spread')
    # ax.plot(data['day'], data['freeze'], label='freeze')
    # ax.plot(data['day'], data['ocean_melt'], label='ocean melt')


    # Set plot title and labels
    plt.title('Ice Melt Model')
    plt.xlabel('month/year')
    plt.ylabel('normalised value')

    # calculate x-axis tick values
    months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

    #https://matplotlib.org/3.4.3/gallery/ticks_and_spines/major_minor_demo.html
    #ax.xaxis.set_major_locator(MultipleLocator(365))
    #ax.xaxis.set_ticks(year_tick_values,year_tick_labels)

    ax.set_xticks(np.arange(0, len(data['sie'])+1, 365))
    ax.set_xticklabels(range(model.cfg.num_years+1))

    # Failing attempt to label the month ticks
    # m_day = 0.0
    # months_labels = ['D']
    # for y in range(cfg.num_years):
    #     months_labels += months
    #     for d in range(12):
    #         m_day += 365/12
    #ax.set_xticks(np.arange(0, len(data['sie'])+1, 365/12), minor=True)
    #ax.set_xticklabels(months_labels, minor=True)

    ax.xaxis.set_minor_locator(MultipleLocator(365/12))     # For the minor ticks, use no labels; default NullFormatter.

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()


if __name__ == "__main__":

    model = semiafa.Model()

    data = model.runModel()

    # create data frame from dictionary
    df = pd.DataFrame.from_dict(data) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html
    #df.set_index('day')

    for y in range(model.cfg.num_years):
        start = y * 365
        end = start + 364
        year_data = df[df['day'].between(start, end)]
        min_sie = year_data['sie'].min()
        max_sie = year_data['sie'].max()
        print(y,min_sie,max_sie)

    plotResults(model)

