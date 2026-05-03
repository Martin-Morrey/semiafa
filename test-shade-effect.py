import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import matplotlib.dates as mdates
import semiafa
import myutils
import sys
import csv

# set up Hydra conf
from omegaconf import DictConfig, OmegaConf
import hydra

def plotResults(model_with_shade,model_no_shade):
    # Plot the result 
    fig, ax = plt.subplots()
    data_with_shade = model_with_shade.data
    data_no_shade = model_no_shade.data

    # ice and sea extent
    ax.plot(data_no_shade['date'], data_no_shade['sie'], label='SIE no shade')
    ax.plot(data_with_shade['date'], data_with_shade['sie'], label='SIE with shade')

    # shade area
    shade_area = np.array(data_with_shade['shade_area'])
    shade_area_masked = np.ma.masked_where(shade_area == 0, shade_area) # https://matplotlib.org/stable/gallery/lines_bars_and_markers/masked_demo.html
    ax.plot(data_with_shade['date'], shade_area_masked, label='Shade applied')

    # open sea
    #ax.plot(data['day'], data['sea'], label='area of open sea')

    # insolation
    #ax.plot(data['day'], data['solar_heat'], label='solar heat')

    # ice deltas
    # ax.plot(data['day'], data['solar_melt'], label='solar melt')
    # ax.plot(data['day'], data['air_melt'], label='air heat melt')
    # ax.plot(data['day'], data['wind_spread'], label='wind spread')
    # ax.plot(data['day'], data['freeze'], label='freeze')
    # ax.plot(data['day'], data['ocean_melt'], label='ocean melt')

    # Label with month ticks, see https://stackoverflow.com/a/46556504
    #months = mdates.MonthLocator()  # every month
    months = mdates.MonthLocator(range(1, 13), bymonthday=1, interval=2) # https://www.programcreek.com/python/example/71849/matplotlib.dates.MonthLocator

    fmt = mdates.DateFormatter('%b') # Specify the format - %b gives us Jan, Feb...
    X = plt.gca().xaxis
    X.set_major_locator(months)
    X.set_major_formatter(fmt) # Specify formatter

    # Set plot title and labels
    plt.title('Empirical Model of Sea-Ice Extent (SIE)')
    #plt.xlabel('date')
    plt.ylabel('Rescaled SIE')

    # Y axis
    plt.ylim(0, 1.05)

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

    # ======================= Define the Shade Scenario =======================================
    # ToDo - replace masie_min, masie_max with values directly derived from MASIE data specified in config
    # (masie_min, masie_max) = (2933846,8204782) # all geographically bound, inc central arctic
    (masie_min, masie_max) = (312153, 4956787) # marginal seas only, min of 312153 was in 2012

    sunshade_area = 2
    num_sunshades = 2000
    total_shade_area = sunshade_area * num_sunshades

    # ========================= Rescale Sunshade Area Just Like Total Area =============
    # normalised_shade_area = (sunshade_area * num_sunshades) / total_area # WRONG!!! this is rescaling, MASIE data was normalised
    # normalised_shade_area = myutils.normaliseValue(total_shade_area, masie_min, masie_max) # ALSO WRONG !!!  Area is out of range of the normalised MASIE data
    #shade_area: 0.002  # For 2.0km2 sunshade, 0.0002 is 1,640 km2 (~800 sunshades) 0.002 is 16,400 km2 (~8000 sunshades)
    rescaled_shade_area = myutils.rescaleValue(total_shade_area, masie_max)


    # ======================= Set-Up the Config =======================================

    # Quick and dirty approach, see https://stackoverflow.com/a/73813430
    hydra.core.global_hydra.GlobalHydra.instance().clear() # see https://www.sscardapane.it/tutorials/hydra-tutorial/
    hydra.initialize(version_base=None, config_path="config")

    #cfg = hydra.compose(config_name="2023-06-11_optimised-config_run2") # max SIE 0.997, significant multiplier effect
    #cfg = hydra.compose(config_name="2023-06-20_optimised-config") # best_value: 0.04107893468035606
    #cfg = hydra.compose(config_name="2023-07-06_optimised-config_run2") 
    #cfg = hydra.compose(config_name="2023-07-07_optimised-config_run1")
    # cfg_file = "optimised-config_imsc-40p0"
    cfg_file = "optimised-config_rescaled1_2026-05-01.yaml"

    cfg = hydra.compose(config_name=cfg_file)
    print('Applying config: ' + cfg_file, file=sys.stderr)

    # ======================= Run the Scenarios =======================================

    # Hydra object instantiation, see https://hydra.cc/docs/1.2/advanced/instantiate_objects/overview/ 
    num_years = 2
    start_year = 2022 # start_year = 2004

    model_no_shade = hydra.utils.instantiate(cfg.Model, num_years = num_years, shade_on = False, start_year = start_year)
    model_with_shade = hydra.utils.instantiate(cfg.Model, num_years = num_years, shade_on = True, start_year = start_year, shade_area = rescaled_shade_area) 
    #model = semiafa.Model(cfg) # OLD APPROACH

    data_with_shade = model_with_shade.runModel()
    data_no_shade = model_no_shade.runModel()

    # ============================ Analyse the Results ============================================

    # Create Pandas Data Frame from Model Dictionary
    df_no_shade = pd.DataFrame.from_dict(data_no_shade) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html
    df_with_shade = pd.DataFrame.from_dict(data_with_shade) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html

    # SIE Analysis Dictionaries
    sie_no_shade = myutils.statsByYear(df_no_shade,'sie',model_no_shade.start_year,model_no_shade.num_years) 
    sie_with_shade = myutils.statsByYear(df_with_shade,'sie',model_with_shade.start_year,model_with_shade.num_years)

    # Solar Heat Analysis Dictionaries
    solar_heat_no_shade = myutils.statsByYear(df_no_shade,'total-insolation',model_no_shade.start_year,model_no_shade.num_years)
    solar_heat_with_shade = myutils.statsByYear(df_with_shade,'total-insolation',model_with_shade.start_year,model_with_shade.num_years)

    # ===================== Write Summary of Results to STDOUT ==============================

    writer = csv.writer(sys.stdout)

    header = ['year', 'min SIE no shade', 'max SIE no shade', 'min SIE with shade', 'max SIE with shade' ,'shade area','solar heat no shade (MJ)', 'solar heat with shade(MJ)','solar heat delta (MJ)']
    writer.writerow(header)

    for y in range(model_with_shade.num_years):
        year = str(y + model_no_shade.start_year)
        #diff = sie_with_shade['min'][y] - sie_no_shade['min'][y]
        #shade_multiplier = diff / model_with_shade.shade_area
        full_solar_heat = solar_heat_no_shade['sum'][y]
        reduced_solar_heat = solar_heat_with_shade['sum'][y]
        solar_heat_delta = full_solar_heat - reduced_solar_heat

        # put output data into a list
        data = [year]
        # put areas into integer units of km2, by denormalising using properties of MASIE source data
        # data.append(round(sie_no_shade['min'][y] * total_area)) # this was stupid and wrong
        # data.append(round(sie_no_shade['max'][y] * total_area))
        # data.append(round(sie_with_shade['min'][y] * total_area))
        # data.append(round(sie_with_shade['max'][y] * total_area))
        # data.append(round(model_with_shade.shade_area * total_area))

        # data.append( round( myutils.denormaliseValue(sie_no_shade['min'][y],masie_min,masie_max) ) )
        # data.append( round( myutils.denormaliseValue(sie_no_shade['max'][y],masie_min,masie_max) ) )
        # data.append( round( myutils.denormaliseValue(sie_with_shade['min'][y],masie_min,masie_max) ) )
        # data.append( round( myutils.denormaliseValue(sie_with_shade['max'][y],masie_min,masie_max) ) )

        data.append( round( myutils.deRescaleValue(sie_no_shade['min'][y],masie_max) ) )
        data.append( round( myutils.deRescaleValue(sie_no_shade['max'][y],masie_max) ) )
        data.append( round( myutils.deRescaleValue(sie_with_shade['min'][y],masie_max) ) )
        data.append( round( myutils.deRescaleValue(sie_with_shade['max'][y],masie_max) ) )

        data.append( total_shade_area )
        # append other values
        data = data + [full_solar_heat, reduced_solar_heat, solar_heat_delta]
        #data = [year, sie_no_shade['min'][y], sie_no_shade['max'][y], sie_with_shade['min'][y], sie_with_shade['max'][y], diff, shade_multiplier, full_solar_heat, reduced_solar_heat ,solar_heat_delta ]
        
        writer.writerow(data)

    # ===================== Plot the Scenarios ==============================

    # ToDo: clear cache file(s)
    plotResults(model_with_shade,model_no_shade)

