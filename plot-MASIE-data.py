import pandas as pd
import sys
import matplotlib.pyplot as plt
import semiafa
import masie
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
        masieRecord = hydra.utils.instantiate(cfg.masie)
    else:
        masieRecord = hydra.utils.instantiate(cfg.masie,csv_file_path=sys.argv[1])
   
    masie_df = masieRecord.readmasie()

    fig, ax = plt.subplots()

    # Plot Ice or Sea Extent

    # Uncomment the following to sea total of land bound seas
    # seas = []
    
    # Uncomment the following to see plots and stats for the individual seas
    seas = masieRecord.column_names # "regions" read from Hydra config

    # Extract data for the individual seas in the list
    sie_min_max = {}
    num_years = (masieRecord.end_year - masieRecord.start_year) + 1
    masie_df_n = masie_df.copy()
    # compare the seas
    for sea in seas:
        # masie_df_n[sea] = myutils.normaliseList(masie_df[sea])
        masie_df_n[sea] = myutils.rescaleList(masie_df[sea]) # comment out to peak at real values
        ax.plot(masie_df_n['date'], masie_df_n[sea], label=sea)       
        sie_min_max[sea] = myutils.maxAndMinsByYear(masie_df,sea,masieRecord.start_year,num_years)

    if len(seas) == 0:
        # OLD ax.plot(masie_df['date'], masie_df['Marginal and Central Normalised'], label='masie Central and Marginal Seas')
        ax.plot(masie_df['date'], masie_df['Marginal and Central Rescaled'], label='Marginal and Central Rescaled')
    
    if len(seas) > 0:
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
    plt.title('Rescaled Masie Data For Land-Bound Seas')
    plt.xlabel('month/year')
    plt.ylabel('rescaled value')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()
