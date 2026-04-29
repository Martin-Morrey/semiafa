# SEMIAFA - Simple Empirical Model of Ice-Albedo Feedback in the Arctic

## Description
SEMIAFA is a simple parameterised empirical model of Arctic sea-ice extent (SIE) over the annual cycle, best used on the geographically bound area of Arctic Sea, and testing interventions targeted in this area.

It was designed to be used to for testing the order-of-magnitude impact of targeted solar-geoengineering interventions, which take advantage of the amplifying effect of the ice-albedo feedback.

The pseudo-physical parameters used for modelling the physical processes affecting Arctic SIE, including the ice-albedo feedback, are set-out in the table below.

[MASIE-NH data on SIE from the NSIDC](https://nsidc.org/data/masie/about-masie) is currently used as the training data set, but in theory any similar data on sea-ice extent could be used.

## Limitations of the Model
Far from an exhaustive list, but here goes:
- It's **not** a dynamic physical model
    - No physics occurs in the model, it's all parameterised at a very high level
    - The pseudo physical parameters relate only to their effect on SIE, nothing else
- It does not consider ice thickness, volume or age
    - SIE is the only output of the model
    - It is optimised against SIE data only
- It doesn't model the physical geography at all
- It doesn't include the weather or any effects of clouds etc
- There are no inter-annual effects in the model
    - It does not consider inter-annual trends in sea-ice extent
    - Any benefit of an intervention that preserves sea-ice is just in-year only
    - So although interventions which preserve SIE during the summer, will increase ice thickness over winter, the amount of multi-year ice, and tend to slow the loss of SIE in the following year, these effects **will not** be reflected in the model results
- It assumes that a shading intervention is well-targeted
    - i.e. the area with the lowest albedo (e.g. open sea with no ice), is always shaded first

## Scripts for Running and Using the Model

<table>
<tr><th>Script</th><th>Action</th><th>Notes</th></tr>
<tr><td><i>test-shade-effect.py</i></td><td>Run the model twice, with and without shade, and compare the results</td><td>This fulfils the ultimate purpose of the model, to estimate the impact of a shading intervention on Arctic sea-ice extent</td></tr>
<tr><td><i>plot-masie-model-comparison.py</i></td><td>Compare the masie input data with the model output</td><td>To review how well the simple empirical model predicts SIE, compared to the input data it is optimised on.</td></tr>
<tr><td><i>plot-masie-data.py</i></td><td>View the input data on sea-ice extent</td><td></td></tr>
<tr><td><i>optimise.py</i></td><td>Used with Hydra framework to optimse the parameters of the model</td><td>More info in "Optuna Sweeper Optimisation" below</td></tr>
<tr><td><i>semiafa.py</i></td><td>the model code itself</td><td>normally called by one of the above scripts</td></tr>
</table>

## Pseudo Physical Parameters of the Model

The simple empirical model is configured with a limited set of parameters set-out in the table below.  These parameters are optimised by minimising a cost function based on the delta between the model output and the input data from masie.

<table>
<tr><th>Name</th><th>Description</th><th>Optimised value</th></tr>
<tr><td>solar heat multiplier</td><td>relative melting rate from a date-dependent normalised insolation</td><td>23.8</td></tr>
<tr><td>ocean heat multiplier</td><td>relative melting rate from a constant ocean heat input</td><td>0.5</td><tr>
<tr><td>air melt multiplier</td><td>relative melting rate from date-dependent normalised air heat </td><td>1.0</td><tr>
<tr><td>air heat lag</td><td>time days of lag between air heat and solar heat</td><td>7</td><tr>
<tr><td>ice freeze multiplier</td><td>relative freezing rate of open sea</td><td>7.7</td><tr>
<tr><td>ice power</td><td>power relation between extent of open sea and freezing rate</td><td>0.5</td><tr>
</table>

## Optuna Sweeper Optimisation
The Optuna optimiser works as a sweeper plugin for the Hydra config framework, see https://hydra.cc/docs/plugins/optuna_sweeper/.

To configure and run Optuna:
- Configure the Optuna sweeper in the Hydra config file, i.e. `config/optimiser-config.yaml`
    - this involves setting the range and increment of each parameter
- Run `python3 optimise.py --multirun`
- Best config parameters are recorded in `optimization_results.yaml`, in sub-folder `multirun/hh-mm-ss/`

## Insolation Cache

- The insolation values calculated for each latitude and date are always the same.
- By default, to reduce run-time, the model caches the calculated insolation values using <a href="https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_pickle.html">Pandas DataFrame_to_pickle</a>, in the following *.pkl* file
    - *cache/insolation.pkl*
- **IMPORTANT**:  If the overall time period or latitude range is changed, the above .pkl file must be removed the next time the model is run
    - It won't detect a discrepancy automatically.   To fix this is on the to-do list (below)

## Configuration Notes

To get a consist total frozen area in winter, select only the geographically bounded zones in the masie-NH data, i.e.:

```regions: [' (1) Beaufort_Sea',' (2) Chukchi_Sea',' (3) East_Siberian_Sea',' (4) Laptev_Sea',' (5) Kara_Sea',' (11) Central_Arctic']``` 

See https://nsidc.org/data/masie/explore-region

## To Do List
 - include an automatic check that date range of specified insolation .pkl is compatible with current run
 - report insolation delta from shading for each year
 - average insolation from multiple latitudes (currenty 75N only) 
 - add parameter to measure benefit from retaining multi-season ice?
 - take account of sunlight reaching southerly latitudes first
 - albedos as config parameters
