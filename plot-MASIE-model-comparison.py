import pandas as pd
import sys
import matplotlib.pyplot as plt
import semiafa
import masie
import myutils

# set up Hydra conf
#from omegaconf import DictConfig, OmegaConf
import hydra

if __name__ == "__main__":

    # read the config
    hydra.core.global_hydra.GlobalHydra.instance().clear() # see https://www.sscardapane.it/tutorials/hydra-tutorial/
    hydra.initialize(version_base=None, config_path="config")
    #cfg = hydra.compose(config_name="object-config")
    #cfg = hydra.compose(config_name="2023-06-11_optimised-config_run2")
    #cfg = hydra.compose(config_name="2023-06-20_optimised-config_run2")
    #cfg = hydra.compose(config_name="2023-06-24_optimised-config")
    #cfg = hydra.compose(config_name="2023-07-06_optimised-config")
    #cfg_file = "optimised-config_imsc-40p0"
    # cfg_file = "optimised-config_rescaled1_2026-05-01.yaml"
    #cfg_file = "optimised-config_rescaled1_2026-06-09.yaml"
    cfg_file = "optimised-config_rescaled1_2026-06-13.yaml"
    cfg = hydra.compose(config_name=cfg_file)
    print('Applying config: ' + cfg_file, file=sys.stderr)

    # Instantiate the SeaIceRecord object
    if len(sys.argv) < 2:
        masieRecord = hydra.utils.instantiate(cfg.masie)
    else:
        masieRecord = hydra.utils.instantiate(cfg.masie,csv_file_path=sys.argv[1])
   
     # get file path from config or command line argument
    # if len(sys.argv) < 2:
    #     masie_df = masie.readmasie() # config
    # else:
    #     csv_file_path = sys.argv[1] # command line
    #     masie_df = masie.readmasie(csv_file_path)
    masie_df = masieRecord.readmasie()

    fig, ax = plt.subplots()

    # Instantiate model object with Hydra config, see https://hydra.cc/docs/1.2/advanced/instantiate_objects/overview/ 
    #model = hydra.utils.instantiate(cfg.Model, start_year = 2004, num_years = 20, shade_on = False) # override config
    model = hydra.utils.instantiate(cfg.Model, shade_on = False) # override config

    # run model
    model_data = model.runModel()

    # create data frame from dictionary
    model_data_df = pd.DataFrame.from_dict(model_data) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html

    # calculate difference between masie data and model
    #meanDiff = myutils.meanAbsoluteDifference(masie_df,'yyyyddd','Marginal and Central Normalised',model_data_df,'yyyyddd','sie')
    meanDiff = myutils.meanAbsoluteDifference(masie_df,'yyyyddd','Specified Regions Rescaled',model_data_df,'yyyyddd','sie')
    print(meanDiff)

    # ice and sea extent
    # ax.plot(masie_df['date'], masie_df['Specified Regions Normalised'], label='masie Central and Marginal Seas')
    ax.plot(masie_df['date'], masie_df['Specified Regions Rescaled'], label='Rescaled MASIE SIE in the Marginal Seas')

    ax.plot(model_data['date'],model_data['sie'], label='Modelled SIE')
    #ax.plot(model_data['date'],model_data['solar_heat'], label='model Solar Heat')

    # Set plot title and labels

    # set the font sizes
    plot_params = {
        'legend.fontsize': 10,
        #  'figure.figsize': (15, 5),
         'axes.labelsize': 12,
         'axes.titlesize': 12,
         'xtick.labelsize': 12,
         'ytick.labelsize': 12}

    plt.title('MASIE SIE vs SEMIAFA Model')
    plt.rcParams.update(plot_params) # ,{'font.size': 22}) # https://stackoverflow.com/a/38251497, 
    plt.xlabel('year') #,fontsize=12)
    plt.ylabel('rescaled value') #,fontsize=12)

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()

    # To Do
    # normalise masie data based on mean yearly-maximum, or by dropping outliers
    # - Return mean square difference between masie and model results for optimiser
    # - - get yyyyddd keys out of masie_df, and use to filter model_data
    # - - put SIE from both into a single dataframe, diff values, and square
    # - - calc mean value of the column
