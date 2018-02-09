# -*- coding: utf-8 -*-

"""Console script for nypower."""

import logging

import click

from nypower.archive import Archiver
from nypower.collector import get_fuel_mix

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG)


@click.command()
def main(args=None):
    """Catchup archiver."""
    influx = Archiver()

    for days in reversed(range(0, 7)):
        data = get_fuel_mix(ago=days)
        for timestamp, reading in data.items():
            for fuel, power in reading.fuels.items():
                influx.save_upstream(
                    "fuel-mix", fuel, reading.time, "MW", power)
            influx.save_computed("co2", reading.time,
                                 "g / kWh", reading.co2_g_per_kW)


if __name__ == "__main__":
    main()
