"""Calculators for different values.

In order to approximate the emissions for a single kWh of produced
energy, per power source we look at the following 2016 data sets.

* Detailed EIA-923 emissions survey data
  (https://www.eia.gov/electricity/data/state/emission_annual.xls)

* Net Generation by State by Type of Producer by Energy Source
  (EIA-906, EIA-920, and EIA-923)
  (https://www.eia.gov/electricity/data/state/annual_generation_state.xls)

The NY Numbers for 2016 on power generation are (power in MWh)

2016	NY	Total Electric Power Industry	Total	134,417,107
2016	NY	Total Electric Power Industry	Coal	1,770,238
2016	NY	Total Electric Power Industry	Pumped Storage	-470,932
2016	NY	Total Electric Power Industry	Hydroelectric Conventional	26,888,234
2016	NY	Total Electric Power Industry	Natural Gas	56,793,336
2016	NY	Total Electric Power Industry	Nuclear	41,570,990
2016	NY	Total Electric Power Industry	Other Gases	0
2016	NY	Total Electric Power Industry	Other	898,989
2016	NY	Total Electric Power Industry	Petroleum	642,952
2016	NY	Total Electric Power Industry	Solar Thermal and Photovoltaic	139,611
2016	NY	Total Electric Power Industry	Other Biomass	1,604,650
2016	NY	Total Electric Power Industry	Wind	3,940,180
2016	NY	Total Electric Power Industry	Wood and Wood Derived Fuels	638,859

The NY Numbers on Emissions are (metric tons of CO2, SO2, NOx)

2016	NY	Total Electric Power Industry	All Sources	31,295,191	18,372	32,161
2016	NY	Total Electric Power Industry	Coal	2,145,561	10,744	2,635
2016	NY	Total Electric Power Industry	Natural Gas	26,865,277	122	14,538
2016	NY	Total Electric Power Industry	Other Biomass	0	1	8,966
2016	NY	Total Electric Power Industry	Other	1,660,517	960	3,991
2016	NY	Total Electric Power Industry	Petroleum	623,836	1,688	930
2016	NY	Total Electric Power Industry	Wood and Wood Derived Fuels	0	4,857	1,101


Duel Fuel systems are interesting, they are designed to burn either
Natural Gas, or Petroleum when access to NG is limited by price or
capacity. (Under extreme cold conditions NG supply is prioritized for
heating)

We then make the following simplifying assumptions (given access to the data):

* All natural gas generation is the same from emissions perspective

* The duel fuel systems burned 30% of the total NG in the state, and
  all of the Petroleum. Based on eyeballing the Duel Fuel systems,
  they tend to be running slightly less than straight NG systems.

* The mix of NG / Oil burned in duel fuel plants is constant
  throughout the year. This is clearly not true, but there is no
  better time resolution information available.

* All other fossil fuels means Coal. All Coal is equivalent from
  emissions perspective.

"""

# PWR in MWh
# CO2 in Metric Tons
#
# TODO(sdague): add in

FUEL_2016 = {
    "Petroleum": {
        "Power": 642952,
        "CO2": 623836
    },
    "Natural Gas": {
        "Power": 56793336,
        "CO2": 26865277
    },
    "Other Fossil Fuels": {
        "Power": 1770238,
        "CO2": 2145561
    }
}

# assume Dual Fuel systems consume 30% of state NG. That's probably low.
FUEL_2016["Dual Fuel"] = {
    "Power": (FUEL_2016["Petroleum"]["Power"] +
              (FUEL_2016["Natural Gas"]["Power"] * .3)),
    "CO2": (FUEL_2016["Petroleum"]["CO2"] +
            (FUEL_2016["Natural Gas"]["CO2"] * .3)),
}

# Calculate CO2 per kWh usage


def co2_for_fuel(fuel):
    "Returns metric tons per / MWh, or kg / kWh"
    if fuel in FUEL_2016:
        hpow = FUEL_2016[fuel]["Power"]
        hco2 = FUEL_2016[fuel]["CO2"]
        co2per = float(hco2) / float(hpow)
        return co2per
    else:
        return 0.0


def co2_rollup(rows):
    total_kW = 0
    total_co2 = 0

    for row in rows:
        fuel_name = row[2]
        kW = int(float(row[3]))
        total_kW += kW
        total_co2 += kW * co2_for_fuel(fuel_name)
    co2_per_kW = total_co2 / total_kW
    return co2_per_kW
