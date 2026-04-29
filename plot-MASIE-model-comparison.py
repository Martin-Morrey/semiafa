import pandas as pd
import sys
import matplotlib.pyplot as plt
import semiafa
import maisie
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
    cfg_file = "optimised-config_imsc-40p0"
    cfg = hydra.compose(config_name=cfg_file)
    print('Applying config: ' + cfg_file, file=sys.stderr)

    # Instantiate the SeaIceRecord object
    if len(sys.argv) < 2:
        maisieRecord = hydra.utils.instantiate(cfg.Maisie)
    else:
        maisieRecord = hydra.utils.instantiate(cfg.Maisie,csv_file_path=sys.argv[1])
   
     # get file path from config or command line argument
    # if len(sys.argv) < 2:
    #     maisie_df = maisie.readMaisie() # config
    # else:
    #     csv_file_path = sys.argv[1] # command line
    #     maisie_df = maisie.readMaisie(csv_file_path)
    maisie_df = maisieRecord.readMaisie()

    fig, ax = plt.subplots()

    # ice and sea extent
    ax.plot(maisie_df['date'], maisie_df['Marginal and Central Normalised'], label='MAISIE Central and Marginal Seas')

    # Instantiate model object with Hydra config, see https://hydra.cc/docs/1.2/advanced/instantiate_objects/overview/ 
    #model = hydra.utils.instantiate(cfg.Model, start_year = 2004, num_years = 20, shade_on = False) # override config
    model = hydra.utils.instantiate(cfg.Model, shade_on = False) # override config

    # run model
    model_data = model.runModel()

    # create data frame from dictionary
    model_data_df = pd.DataFrame.from_dict(model_data) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html

    # calculate difference between MAISIE data and model
    meanDiff = myutils.meanAbsoluteDifference(maisie_df,'yyyyddd','Marginal and Central Normalised',model_data_df,'yyyyddd','sie')
    print(meanDiff)

    ax.plot(model_data['date'],model_data['sie'], label='Modelled SIE')
    #ax.plot(model_data['date'],model_data['solar_heat'], label='model Solar Heat')

    # To Do
    # normalise MAISIE data based on mean yearly-maximum, or by dropping outliers
    # - Return mean square difference between MAISIE and model results for optimiser
    # - - get yyyyddd keys out of maisie_df, and use to filter model_data
    # - - put SIE from both into a single dataframe, diff values, and square
    # - - calc mean value of the column

    # Set plot title and labels
    plt.title('MAISIE Data vs Ice Melt Model')
    plt.xlabel('year')
    plt.ylabel('normalised value')

    # Add a legend
    plt.legend()

    # Show the plot
    plt.show()
