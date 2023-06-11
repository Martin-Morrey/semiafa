# SEMIAFA
## Simple Empirical Model of Ice-Albedo Feedback in the Arctic

For testing the order-of-magnitude impact of targeted solar-geoengineering interventions, which take advantage of the amplifying effect ice-albedo feedback

Designed to model the SIE in the geographically bound area of Arctic sea, and interventions targeted in this area.

## Optuna Sweeper Optimisation
The Optuna optimiser works as a sweeper plugin for the Hydra config framework, see https://hydra.cc/docs/plugins/optuna_sweeper/.

To configure and run Optuna:
- Configure the Optuna sweeper in the Hydra config file, i.e. `config/optimiser-config.yaml`
- Run `python3 optimise.py --multirun`
- Best config parameters are recorded in `optimization_results.yaml`, in sub-folder `multirun/hh-mm-ss/`

## Insolation Cache

## Configuration Notes

To get consist frozen area in winter, select only the geographically bounded zones in the MAISIE-NH data, i.e.:

```regions: [' (1) Beaufort_Sea',' (2) Chukchi_Sea',' (3) East_Siberian_Sea',' (4) Laptev_Sea',' (5) Kara_Sea',' (11) Central_Arctic']``` 

See https://nsidc.org/data/masie/explore-region

## To Do List
 - check date range of specified insolation .pkl is compatible with current run
 - report insolation delta from shading for each year
 - add parameter to measure benefit from retaining multi-season ice?
