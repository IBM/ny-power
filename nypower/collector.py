# This file represents the collectors for NY ISO content from
# http://mis.nyiso.com/public/. These are typically CSV files with 5
# minute resolution data that are updated every 5 - 20 minutes.

import collections
import csv
import datetime
import io
import urllib.request

from nypower.calc import co2_for_fuel

FUEL_MIX = "http://mis.nyiso.com/public/csv/rtfuelmix/{0}rtfuelmix.csv"


def timestamp2epoch(ts):
    return int(datetime.datetime.strptime(
        ts, "%m/%d/%Y %H:%M:%S").strftime("%s"))


def tzoffset():
    """UTC to America/New_York offset."""
    return datetime.timedelta(hours=5)


class FuelMixReading(object):

    def __init__(self, time):
        self.time = time
        self.fuels = dict()

    def add_fuel(self, fuel, power):
        """ fuel is by name, power is current MW """
        self.fuels[fuel] = power

    @property
    def epoch(self):
        return timestamp2epoch(self.time)

    @property
    def total_MW(self):
        return sum(self.fuels.values())

    @property
    def total_co2(self):
        co2 = 0
        for fuel, power in self.fuels.items():
            # co2_for_fuel is metrictons / MWh * MW
            # co2 is metric tons / hr
            co2 += (co2_for_fuel(fuel) * power)
        return co2

    @property
    def co2_g_per_kW(self):
        # total_co2 is metric tons / hr
        # power is / MW
        # results is metric tons / MHh, or kg / kWh
        # we multiply by 1000 to get to g / kWh
        return self.total_co2 * 1000 / self.total_MW


def get_fuel_mix(daysago=0):
    # TODO(sdague): the containers run in UTC, the data thinks about
    # thing in NY time.
    now = datetime.datetime.now() - \
        datetime.timedelta(days=daysago) - tzoffset()
    url = FUEL_MIX.format(now.strftime("%Y%m%d"))

    # unfortunately we can't quite connect urllib to csv
    with urllib.request.urlopen(url) as response:
        out = io.StringIO()
        out.write(response.read().decode('utf-8'))

    # We have to rewind the output stream so it can be read by
    # csv.reader
    out.seek(0)
    reader = csv.reader(out, quoting=csv.QUOTE_NONE)
    data = collections.OrderedDict()

    # this folds up the data as a hash area keyed by timestamp for
    # easy sorting
    for row in reader:
        try:
            ts = row[0]
            fuel = row[2]
            power = int(float(row[3]))
            if ts not in data:
                data[ts] = FuelMixReading(ts)
            data[ts].add_fuel(fuel, power)

        except ValueError:
            # skip a parse error on epoch, as it's table headers.
            pass

    return data
