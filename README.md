# NY Power Site #

## Background ##

We recently bought a Chevy Bolt EV, which we use as our primary
vehicle. We charge at home with a Level 2 charger. When should we
charge the car?

Static time of use billing in our area marks peak at 2pm - 7pm
weekdays. While that's the only time the power company doesn't want
you to charge, the grid varies a lot over the course of the day to
match demand. The NY ISO has some near realtime views of this.

![NY Power Realtime Grid](web/images/screenshot_372.png)

The data that powers this website is public, but there is no public
API. There is instead a set of 5 minute resolution CSV files published
every 5 - 20 minutes at http://mis.nyiso.com/public/. This could be
turned into a user friendly API that could be consumed easily by
anyone.

We could also add over the top analysis, like what the estimated CO2
emissions are, right now, for a kWh of electricity used.

## System Components ##

The following is a rough idea of the ways

* Ingest system - pod running ingest of CSV data, polling regularly to
  pull in latest data
* Real time events - MQTT server running with real time events
  streaming to it, this provides a very light weight way for people to
  monitor the data.
* API server - query current and historic data, include API rate
  limiting (via Istio) to avoid DOS attacks.
