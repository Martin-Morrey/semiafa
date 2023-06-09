import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import semiafa
import myutils

# set up Hydra conf
from omegaconf import DictConfig, OmegaConf
import hydra

def plotResults(model_with_shade,model_no_shade):
    # Plot the result 
    fig, ax = plt.subplots()
    data_with_shade = model_with_shade.data
    data_no_shade = model_no_shade.data
    # ice and sea extent
    ax.plot(data_no_shade['date'], data_no_shade['sie'], label='SIE original')
    ax.plot(data_with_shade['date'], data_with_shade['sie'], label='SIE with shade')
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
    plt.xlabel('date')
    plt.ylabel('normalised value')

    # calculate x-axis tick values
    #months = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

    #ax.set_xticks(np.arange(0, len(data_with_shade['sie'])+1, 365))
    #ax.set_xticklabels(range(model_with_shade.num_years+1))

    #ax.xaxis.set_minor_locator(MultipleLocator(365/12))     # For the minor ticks, use no labels; default NullFormatter.

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

    # sie_no_shade = myutils.maxAndMinsByDay(df_no_shade,'sie',model_no_shade.num_years)
    # sie_with_shade = myutils.maxAndMinsByDay(df_with_shade,'sie',model_with_shade.num_years)

    sie_no_shade = myutils.maxAndMinsByYear(df_no_shade,'sie',model_no_shade.start_year,model_no_shade.num_years)
    sie_with_shade = myutils.maxAndMinsByYear(df_with_shade,'sie',model_with_shade.start_year,model_with_shade.num_years)

    for y in range(model_with_shade.num_years):
        year = str(y + model_no_shade.start_year)
        print(year, sie_no_shade['min'][y], sie_no_shade['max'][y], sie_with_shade['min'][y], sie_with_shade['max'][y], sie_with_shade['min'][y] - sie_no_shade['min'][y] )

    # ToDo: clear cache file(s)
    plotResults(model_with_shade,model_no_shade)

