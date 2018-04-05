# Making public data available as an event stream #

We recently bought a Chevy Bolt EV, which we use as our primary
vehicle. We charge at home with a Level 2 charger. When should we
charge the car?

Static time of use billing in our area marks peak at 2pm - 7pm
weekdays. While that's the only time the power company doesn't want
you to charge, the grid varies a lot over the course of the day to
match demand. The New York State Indepdendent System Operator (NYISO)
is responsible for managing the power grid in NY State. They provide
near real time data about what fuels are being consumed in NY State to
provide residents electricity.

![NY Power Realtime Grid](web/images/screenshot_372.png)

The data that powers this website is public, but there is no public
API. There are instead a set of 5 minute resolution CSV files
published every 5 - 20 minutes at http://mis.nyiso.com/public/. This
is turned into a public MQTT service which create a very low resource
way of consuming this data. After injesting this data it also
publishes an estimated value of the CO2 per kWh over the course of the
day.

A web page which connects directly to the MQTT service over a
websocket shows how you can provide a dyanmic web site with no server
polling, only updating when relevant data is provided.

The entire application is deployed in Kubernetes using Helm. This
makes it possible to bring up new copies of the application with very
few user steps, and work on a development version of the application
while a production version is running.

When the user has completed this Code Pattern they will understand how
to:

* Use an MQTT server to provide real time event stream
* Consume an MQTT stream directly from a web browser
* Deploy an application on Kubernetes with Helm

## Flow

## Included components

## Featured technologies

# Watch the video

# Steps

## Prerequisites

# Sample output

# Links

# Learn more

* **Container Orchestration Code Patterns**: Enjoyed this Code Pattern? Check out our other [Container Orchestration Code Patterns](https://developer.ibm.com/code/technologies/container-orchestration/).
* **Kubernetes on IBM Cloud**: Deliver your apps with the combined power of [Kubernetes and Docker on IBM Cloud](https://www.ibm.com/cloud-computing/bluemix/containers)

# License
[Apache 2.0](LICENSE)
