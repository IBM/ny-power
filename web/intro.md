# Learn more about running non cloud native applications on Kubernetes
with Helm

Kubernetes is a great environment for running containerized
applications. There are all kinds of best practices and patterns for
creating cloud native applications for the platform. But some times
you need to integrate existing established services into this
environment. What does the pattern look like for that?

I decided to explore that by creating a project that publishes a real
time data feed via MQTT. MQTT an open standard publish / subscribe
protocol that is used extensively in the Internet of Things space. The
ny-power application consumes the regularly published data from the
New York power grid, and publishes that with an MQTT service. It also
computes the real time CO2 per kWh in the grid. The most commonly used
open source MQTT service is mosquitto, which is not cloud native, and
requires persistent storage to provide message guaruntees. The entire
application ends up being a medium complexity Kubernetes app, which
demonstrates how legacy services can be used with persistent volumes
alongside more cloud native or custom written components.

MQTT also can be consumed directly over websockets. As a demonstration
there is an included web dashboard to visualize the data. This
requires getting the external IP address of the MQTT pod handed to the
Web site pods before they start. You can accomplish this with the
Kubernetes API, but only after explicitly allowing those API calls
using Roles and RoleAssignments. This is done with a ServiceAccount as
part of security best practices of not giving too many permissions.

The entire application is wrapped up in Helm, which really shows its
strength once you get beyond trivial applications in Kubernetes. The
ny-power application also demonstrates that your application doesn't
have to be perfectly cloud native to benefit from being deployed in
Kubernetes. The built in service monitoring and restart in Kubernetes,
and the lifecycle management of Helm have made this application much
easier to maintain than if it had been done as a traditional set of
colocated services on a Linux server.
