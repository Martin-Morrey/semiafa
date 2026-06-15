# SEMIAFA - Simple Empirical Model of Ice-Albedo Feedback in the Arctic

## Description
SEMIAFA is a simple parameterised empirical model of Arctic sea-ice extent (SIE) over the annual cycle, best used on the geographically bound area of Arctic Sea, and specifically the marginal seas.

It was designed to be used to for testing the order-of-magnitude impact of shading interventions, which could take advantage of the amplifying effect of the ice-albedo feedback.

The pseudo-physical parameters used for modelling the physical processes affecting Arctic SIE, including the ice-albedo feedback, are set-out in the table below.

Training data on SIE:
- [MASIE-NH data on SIE from the NSIDC](https://nsidc.org/data/masie/about-masie)
    - MASIE NSIDC/NIC Sea Ice Product G02186 - Daily Ice Extent by Region in Square Kilometers
- In theory any similar data on sea-ice extent could be used.

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
<tr><th>Name</th><th>Description</th><th>Example Value*</th></tr>
<tr><td>sun_melt_multiplier</td><td>relative melting rate from a date-dependent rescaled insolation</td><td>24.0</td></tr>
<tr><td>ocean_heat_multiplier</td><td>relative melting rate from a constant ocean heat input</td><td>0.2</td><tr>
<tr><td>air_heat_lag</td><td>time in days between notional solar-driven air heat and direct solar heat</td><td>-49</td><tr>
<tr><td>air_melt_multiplier</td><td>relative melting rate from date-dependent notional air heat</td><td>1.7</td><tr>
<tr><td>ice_freeze_multiplier</td><td>relative freezing rate of open sea</td><td>10.0</td><tr>
<tr><td>ice_power</td><td>power relation between extent of open sea and freezing rate</td><td>0.7</td><tr>
<tr><td>final_freeze_multiplier</td><td>degree of accelerated final freeze, needed to reach full SIE in winter</td><td>0.00002</td></tr>
</table>

*Example values are after being optimised against the marginal seas only - see configuration notes.

## Other Configuration Parameters

### Model - General
<table>
<tr><th>Name</th><th>Typical Value(s) Used</th><th>Description</th></tr>

<tr><td>lat_for_insolation_calc</td><td>75</td><td>representative latitude for approximate insolation</td></tr>
<tr><td>max_sie</td><td>0.99999</td><td>used to prevent infinities, should be close to 1</td></tr>
<tr><td>min_sie</td><td>0.00001</td><td>used to prevent infinities, should be close to 0</td></tr>
<tr><td>insolation_year</td><td>2010</td><td>doesn't really matter, pick a year</td></tr>
<tr><td>insolation_file</td><td>cache/insolation.pkl</td><td>.pkl file for caching insolation data</td></tr>
<tr><td>start_year</td><td>2004 - 2026</td><td>start year for model run, typically 2 years before start of MASIE data for parameter optimisation runs</td></tr>
<tr><td>num_years</td><td>2-22</td><td>number of years to run model over - long for parameter optimisation runs, short for shading tests</td></tr>
<tr><td>wind_spread_start</td><td>136</td><td>day we assume wind starts exposing open sea (first of month April:91, May:121)</td></tr>
<tr><td>wind_spread_stop</td><td>156</td><td>day we stop wind exposure of open sea # data indicates ~50,000 km2 by day 150, but highly variable</td></tr>
<tr><td>wind_spread_rate</td><td>0.0002, 0.0003</td><td>proportion of total area exposed by wind daily,0.0002 (marginal seas,5M km2) 0.0003 (whole of central arctic 8M km2) represent ~2,500km2 (x 20 days give 50,000)</td></tr>
</table>

### Model - Shade Experiments
<table>
<tr><th>Name</th><th>Typical Value(s) Used</th><th>Description</th></tr>

<tr><td>shade_on</td><td>No/Yes</td><td>apply a shade intervention (always "No" in parameter optimisation runs)</td></tr>
<tr><td>shade_start</td><td>137</td><td>day we start shade intervention (if any)</td></tr>
<tr><td>shade_stop</td><td>201</td><td>day we stop shade intervention (if any)</td></tr>
<tr><td>shade_area</td><td>0.002</td><td>relative area to which to apply shade</td></tr>
<tr><td>shade_targeting_factor</td><td>1 or 0</td><td>0: shade is distributed over whole area, 1: shade is targeted at open sea 100% of the time</td></tr>
</table>

### Use of MASIE Data on Sea-Ice Extent

### Configuration Notes

To get a consist total frozen area in winter, select only the geographically bounded zones in the masie-NH data, i.e.:

```regions: [' (1) Beaufort_Sea',' (2) Chukchi_Sea',' (3) East_Siberian_Sea',' (4) Laptev_Sea',' (5) Kara_Sea',' (11) Central_Arctic']``` 

The SIE Central Arctic does not change in the early part of the melt season, so to get the best approximation of the albedo feedback, select only the marginal seas, i.e.:

```regions: [' (1) Beaufort_Sea',' (2) Chukchi_Sea',' (3) East_Siberian_Sea',' (4) Laptev_Sea',' (5) Kara_Sea']```

See https://nsidc.org/data/masie/explore-region


## Optuna Sweeper Optimisation
The Optuna optimiser works as a sweeper plugin for the Hydra config framework, see https://hydra.cc/docs/plugins/optuna_sweeper/.

To configure and run Optuna:
- Configure the Optuna sweeper in the Hydra config file, i.e. `config/optimiser-config.yaml`
    - this involves setting the range and increment of each parameter
- Run `python3 optimise.py --multirun`
- Best config parameters are recorded in `optimization_results.yaml`, in sub-folder `multirun/yyyy-mm-dd/hh-mm-ss/`

## Insolation Cache

- The insolation values calculated for each latitude and date are always the same.
- By default, to reduce run-time, the model caches the calculated insolation values using <a href="https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_pickle.html">Pandas DataFrame_to_pickle</a>, in the following *.pkl* file
    - *cache/insolation.pkl*
- **IMPORTANT**:  If the overall time period or latitude range is changed, the above .pkl file must be removed the next time the model is run
    - It won't detect a discrepancy automatically.   To fix this is on the to-do list (below)

## To Do List
 - include an automatic check that date range of specified insolation .pkl is compatible with current run
 - report insolation delta from shading for each year
 - average insolation from multiple latitudes (currenty 75N only) 
 - add parameter to measure benefit from retaining multi-season ice?
 - take account of sunlight reaching southerly latitudes first
 - albedos as config parameters
