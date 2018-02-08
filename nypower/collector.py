# This file represents the collectors for NY ISO content from
# http://mis.nyiso.com/public/. These are typically CSV files with 5
# minute resolution data that are updated every 5 - 20 minutes.

import collections
import csv
import datetime
import io
import urllib


FUEL_MIX = "http://mis.nyiso.com/public/csv/rtfuelmix/{0}rtfuelmix.csv"


def timestamp2epoch(ts):
    return int(datetime.datetime.strptime(
        ts, "%m/%d/%Y %H:%M:%S").strftime("%s"))


def tzoffset():
    """UTC to America/New_York offset."""
    return datetime.timedelta(hours=5)


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
            timestamp = timestamp2epoch(row[0])
            if timestamp in data:
                data[timestamp].append(row)
            else:
                data[timestamp] = [row]
        except ValueError:
            # skip a parse error on epoch, as it's table headers.
            pass

    return data
