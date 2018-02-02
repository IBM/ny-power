# Grand TODO List #

This is a set of things that should be done in no particular order to
make this a more interesting system.

## DNS ##

* Persistent DNS for MQTT socket
* Update DNS entry whenever MQTT service is rebuilt

## MQTT Pod ##

* Put MQTT stateful content in persistent volume so that rebuilds
  don't loose retain messages

## Data Pump Pod ##

* Basic flake8 / testing for python content

## API Pod ##

* Create API server to query current and historic values

## DB Pod ##

* Store data coming in from Data pump somewhere for API query
