""" Calculators for different values. """

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
    }
}

# assume Dual Fuel systems consume 30% of state NG. That's probably low.
FUEL_2016["Dual Fuel"] = {
    "Power": (FUEL_2016["Petroleum"]["Power"] + (FUEL_2016["Natural Gas"]["Power"] * .3)),
    "CO2": (FUEL_2016["Petroleum"]["CO2"] + (FUEL_2016["Natural Gas"]["CO2"] * .3)),
}

# Calculate CO2 per kWh usage

def co2_for_fuel(fuel):
    if fuel in FUEL_2016:
        hpow = FUEL_2016[fuel]["Power"]
        hco2 = FUEL_2016[fuel]["CO2"]
        co2per = float(hco2) / float(hpow)
        return co2per
    else:
        return 0.0
