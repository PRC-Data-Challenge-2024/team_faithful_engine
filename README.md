# ATOW-Prediction
https://ansperformance.eu/study/data-challenge


# TODOs:
Add features to improve the prediction.
All multiplications and divisions should be features.

Feature ideas:
- zero fuel weight
- estimated engine type by knowing (Austrian, Swiss, Vueling)
- take off speed
- take off climb rate
- taxi out fuel consumption
- landing speed
- weather at destination
- weather at departure airport
- estimated fuel burn for route (need to account for flight phases)
- airline specific differences => cluster similar data per airline
- route schedule (daily, weekly etc.)
- month of year?

further improvements
- feature importance
- normalize features
- bayesian hyperparameter search
- use neural network as predictor (learn JAX?) 
- incorporate uncertainty?!


clean data remove quasi duplicates with same tow

https://www.transtats.bts.gov/AverageFare/
https://www.transtats.bts.gov/Data_Elements.aspx?Data=4
https://data.europa.eu/data/datasets/43c6ugqwp92dx7vlgnzja?locale=en
Diversion Airports: https://www.bts.gov/topics/airlines-and-airports/domestic-flights-tarmac-times-more-3-hours-and-international-flights-9 
Taxi out time: https://www.transtats.bts.gov/ONTIME/OriginDestination.aspx
https://www.transtats.bts.gov/ONTIME/Departures.aspx

https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr=b0-gvzr
https://www.bts.gov/browse-statistical-products-and-data/bts-publications/data-bank-28ds-t-100-domestic-segment-data


How to split into regional, buisness, cargo,...
https://www.eurocontrol.int/sites/default/files/2022-05/eurocontrol-market-segment-update-2022-05.pdf

https://www.easa.europa.eu/eco/eaer/appendix

fuel flow per engine etc.
https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank

fuel prices 2022
https://www.kaggle.com/datasets/zusmani/petrolgas-prices-worldwide/data
CC0 license - obtained with google


Idea from Lukas: Add tax dataset?