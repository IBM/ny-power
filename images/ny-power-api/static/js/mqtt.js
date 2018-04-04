var client = new Paho.MQTT.Client(mqttHost, Number("80"), "client-" + Math.random());

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.reconnect = true;
client.connect({onSuccess: onConnect});

var fuels = ["Nuclear", "Hydro", "Natural Gas", "Dual Fuel", "Wind", "Other Renewables", "Other Fossil Fuels"];
var readings = {};

function fuel_mix_graph(message) {
    var topic = message.destinationName.split("/");
    var fuel_type = topic[3];
    var data = JSON.parse(message.payloadString);
    readings[fuel_type] = data.value;
    var current = [];
    for (var i in fuels) {
        var fuel = fuels[i];
        current.push(readings[fuel]);
    }
    var layout = {
        title: 'Current Fuel Mix on NY ISO Grid',
        yaxis: {
            title: 'Mega Watts'
        },
    };

    var plot = [
        {
            x: fuels,
            y: current,
            marker: {
                color: [ "#FFC000", "#4F81BD", "#FF0000", "#C00000", "#92D050", "#00B050", "#333333" ]
            },
            type: 'bar'
        }
    ];
    Plotly.newPlot('current_fuel', plot, layout);
}

// called when the client connects
function onConnect() {
    // Once a connection has been made, make a subscription and send a message.
    console.log("onConnect");
    client.subscribe("ny-power/computed/co2");
    client.subscribe("ny-power/archive/co2/24h");
    // this is used to single activities to the webapp
    client.subscribe("ny-power/application/webui");
    client.subscribe("ny-power/upstream/fuel-mix/#");
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost:"+responseObject.errorMessage);
    }
}

// called when a message arrives
function onMessageArrived(message) {
    console.log("onMessageArrived:"+message.destinationName + message.payloadString);
    if (message.destinationName == "ny-power/computed/co2") {
        var data = JSON.parse(message.payloadString);
        $("#co2-per-kwh").html(Math.round(data.value));
        $("#co2-units").html(data.units);
        $("#co2-updated").html(data.ts);
    }
    if (message.destinationName.startsWith("ny-power/upstream/fuel-mix")) {
        fuel_mix_graph(message);
    }
    if (message.destinationName == "ny-power/archive/co2/24h") {
        var data = JSON.parse(message.payloadString);
        var plot = [
            {
                x: data.ts,
                y: data.values,
                type: 'scatter'
            }
        ];
        Plotly.newPlot('co2_graph', plot);
    }
    if (message.destinationName == "ny-power/application/webui") {
        if (message.payloadString == "reload") {
            location.reload();
        }
    }
}
