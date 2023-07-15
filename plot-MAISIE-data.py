import pandas as pd
import sys
import matplotlib.pyplot as plt
import semiafa
import maisie
import myutils
import csv

# set up Hydra conf
#from omegaconf import DictConfig, OmegaConf
import hydra

if __name__ == "__main__":

    # read the config
    hydra.core.global_hydra.GlobalHydra.instance().clear() # see https://www.sscardapane.it/tutorials/hydra-tutorial/
    hydra.initialize(version_base=None, config_path="config")
    cfg = hydra.compose(config_name="object-config")
    #cfg = hydra.compose(config_name="best-config_2023-06-10")

    # Instantiate the SeaIceRecord object
    if len(sys.argv) < 2:
        maisieRecord = hydra.utils.instantiate(cfg.Maisie)
    else:
        maisieRecord = hydra.utils.instantiate(cfg.Maisie,csv_file_path=sys.argv[1])
   
    maisie_df = maisieRecord.readMaisie()

    fig, ax = plt.subplots()

    # ice and sea extent
    #ax.plot(maisie_df['date'], maisie_df['Marginal and Central Normalised'], label='MAISIE Central and Marginal Seas')
    seas = maisieRecord.column_names

    sie_min_max = {}
    num_years = (maisieRecord.end_year - maisieRecord.start_year) + 1
    maisie_df_n = maisie_df.copy()
    # compare the seas
    for sea in seas:
        maisie_df_n[sea] = myutils.normaliseList(maisie_df[sea])
        ax.plot(maisie_df_n['date'], maisie_df_n[sea], label=sea)       
        sie_min_max[sea] = myutils.maxAndMinsByYear(maisie_df,sea,maisieRecord.start_year,num_years)


    headers = ['year'] + seas
    writer = csv.writer(sys.stdout)
    writer.writerow(headers)
    for y in range(num_years):
        value_list = [y]
        for sea in seas:
            value_list.append(sie_min_max[sea]['max'][y])
        writer.writerow(value_list)


    # for y in range(model_with_shade.num_years):
    #     year = str(y + model_no_shade.start_year)
    #     diff = sie_with_shade['min'][y] - sie_no_shade['min'][y]
    #     shade_multiplier = diff / model_with_shade.shade_area
    #     data = [year, sie_no_shade['min'][y], sie_no_shade['max'][y], sie_with_shade['min'][y], sie_with_shade['max'][y], diff, shade_multiplier ]
    #     writer.writerow(data)



    # Set plot title and labels
    plt.title('MAISIE Data vs Ice Melt Model')
    plt.xlabel('month/year')
    plt.ylabel('normalised value')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()
