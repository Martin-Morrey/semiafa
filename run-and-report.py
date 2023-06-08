import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import semiafa

# set up Hydra conf
from omegaconf import DictConfig, OmegaConf
import hydra

def plotResults(model_with_shade,model_no_shade):
    # Plot the result 
    fig, ax = plt.subplots()
    data_with_shade = model_with_shade.data
    data_no_shade = model_no_shade.data
    # ice and sea extent
    ax.plot(data_no_shade['day'], data_no_shade['sie'], label='SIE original')
    ax.plot(data_with_shade['day'], data_with_shade['sie'], label='SIE with shade')
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

    ax.set_xticks(np.arange(0, len(data_with_shade['sie'])+1, 365))
    ax.set_xticklabels(range(model_with_shade.num_years+1))

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


    # Quick and dirty approach, see https://stackoverflow.com/a/73813430
    hydra.core.global_hydra.GlobalHydra.instance().clear() # see https://www.sscardapane.it/tutorials/hydra-tutorial/
    hydra.initialize(version_base=None, config_path="config")
    cfg = hydra.compose(config_name="object-config")

    # Hydra object instantiation, see https://hydra.cc/docs/1.2/advanced/instantiate_objects/overview/ 
    model_with_shade = hydra.utils.instantiate(cfg.Model, shade_on = True)
    model_no_shade = hydra.utils.instantiate(cfg.Model, shade_on = False)

    #model = semiafa.Model(cfg)
    #model = semiafa.Model()

    data_with_shade = model_with_shade.runModel()
    data_no_shade = model_no_shade.runModel()

    # create data frame from dictionary
    df_with_shade = pd.DataFrame.from_dict(data_with_shade) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html
    df_no_shade = pd.DataFrame.from_dict(data_no_shade) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html
    #df.set_index('day')

    for y in range(model_with_shade.num_years):
        start = y * 365
        end = start + 364
        year_data_with_shade = df_with_shade[df_with_shade['day'].between(start, end)]
        year_data_no_shade = df_no_shade[df_no_shade['day'].between(start, end)]
        min_sie_with_shade = year_data_with_shade['sie'].min()
        max_sie_with_shade = year_data_with_shade['sie'].max()
        min_sie_no_shade = year_data_no_shade['sie'].min()
        max_sie_no_shade = year_data_no_shade['sie'].max()
        print(y,min_sie_no_shade,max_sie_no_shade,min_sie_with_shade,max_sie_with_shade,min_sie_with_shade-min_sie_no_shade )

    plotResults(model_with_shade,model_no_shade)

