# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import hydra
from omegaconf import DictConfig
import pandas as pd
import myutils

@hydra.main(version_base=None, config_path="config", config_name="optimiser-config")

def optimiseModel(cfg: DictConfig) -> float:

    if cfg.get("error", False):
        raise RuntimeError("cfg.error is True")

    # Instantiate the SeaIceRecord object
    maisieRecord = hydra.utils.instantiate(cfg.Maisie) # 2006 - 2023
    maisie_df = maisieRecord.readMaisie()

    # Instantiate model object with optimiser config 
    # start model a couple of years before MAISE to let it settle down
    #model = hydra.utils.instantiate(cfg.Model, start_year = 2004, num_years = 19, shade_on = False)
    model = hydra.utils.instantiate(cfg.Model, shade_on = False)
    # run model
    model_data = model.runModel()

    # create data frame from model dictionary
    model_data_df = pd.DataFrame.from_dict(model_data) # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html

    # calculate difference between MAISIE data and model
    meanDiff = myutils.meanAbsoluteDifference(maisie_df,'yyyyddd','Marginal and Central Normalised',model_data_df,'yyyyddd','sie')
    return meanDiff


if __name__ == "__main__":
    optimiseModel()