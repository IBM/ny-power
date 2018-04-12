var client = new Paho.MQTT.Client(mqttHost, Number("80"), "client-" + Math.random());

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.reconnect = true;
client.connect({onSuccess: onConnect});

// called when the client connects
function onConnect() {
    // Once a connection has been made, make a subscription and send a message.
    console.log("onConnect");
    client.subscribe("ny-power/#");
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log("onConnectionLost:"+responseObject.errorMessage);
    }
}

// called when a message arrives
function onMessageArrived(message) {
    console.log("onMessageArrived: "+message.destinationName + " " + message.payloadString);
    var content = message.destinationName + " " + message.payloadString + "\n";
    var pre = $("#msglog");
    pre.append(content);
    pre.scrollTop( pre.prop("scrollHeight") );
}
