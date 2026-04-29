# Optimise the model using Optuna
# Run with: python3 optimise.py --multirun

import hydra
from omegaconf import DictConfig
import pandas as pd
import myutils

@hydra.main(version_base=None, config_path="config", config_name="optimiser-config")

def optimiseModel(cfg: DictConfig) -> float:

    if cfg.get("error", False):
        raise RuntimeError("cfg.error is True")

    # Instantiate the SeaIceRecord object
    masieRecord = hydra.utils.instantiate(cfg.masie) # 2006 - 2023
    masie_df = masieRecord.readmasie()

    # Instantiate model object with optimiser config 
    # start model a couple of years before MAISE to let it settle down
    #model = hydra.utils.instantiate(cfg.Model, start_year = 2004, num_years = 19, shade_on = False)
    model = hydra.utils.instantiate(cfg.Model, shade_on = False)
    # run model
    model_data = model.runModel()

    # create data frame from model dictionary
    model_data_df = pd.DataFrame.from_dict(model_data) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html

    # calculate difference between masie data and model
    #meanDiff = myutils.meanAbsoluteDifference(masie_df,'yyyyddd','Marginal and Central Normalised',model_data_df,'yyyyddd','sie')
    ###meanDiff = myutils.meanTopBiasedAbsoluteDifference(masie_df,'yyyyddd','Marginal and Central Normalised',model_data_df,'yyyyddd','sie')
    #return meanDiff

    adjustedCost = myutils.adjustedCostFunction(masie_df,'yyyyddd','Marginal and Central Normalised',model_data_df,'yyyyddd','sie',cfg.Optimiser.start_year,cfg.Optimiser.end_year,cfg.Optimiser.ice_maximum_shortfall_cost)
    return adjustedCost
    

if __name__ == "__main__":
    optimiseModel()