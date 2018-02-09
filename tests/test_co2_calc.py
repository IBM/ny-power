#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `nypower` package."""

import pytest

from click.testing import CliRunner

from nypower import nypower
from nypower import mqtt
from nypower import calc
from nypower import collector
from nypower.cmd import pump

FUELS = {
    "Dual Fuel": 2282,
    "Natural Gas": 3310,
    "Nuclear": 5413,
    "Other Fossil Fuels": 0,
    "Other Renewables": 237,
    "Wind": 258,
    "Hydro": 2814
}

@pytest.fixture
def fuel_sample():
    reading = collector.FuelMixReading("02/09/2018 06:05:00")
    for k, v in FUELS.items():
        reading.add_fuel(k, v)
    return reading

def test_fuel_mix_reading(fuel_sample):
    assert fuel_sample.total_kW == 14314

    assert int(fuel_sample.total_co2) == 2686

    assert int(fuel_sample.co2_g_per_kW) == 187
