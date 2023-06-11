# SEMIAFA
## Simple Empirical Model of Ice-Albedo Feedback in the Arctic

For testing the order-of-magnitude impact of targeted solar-geoengineering interventions, which take advantage of the amplifying effect ice-albedo feedback

ToDo:
 - (option to) store calculated daily insolation, for re-use in multiple runs
 - report insolation delta from shading for each year
 - add parameter to measure benefit from retaining multi-season ice?
 - optimise parameterisation using Optuna or similar

## Optuna Sweeper Optimisation
- Configure Optuna sweeper in Hydra config file, i.e. `config/optimiser-config.yaml`
- Run `python3 optimise.py --multirun`
- Best config parameters are recorded in `optimization_results.yaml`, in sub-folder `multirun/hh-mm-ss/`

## Insolation Cache
