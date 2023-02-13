.. Images
.. |mqtt-sub| image:: images/mqtt-sub.png


South MQTT
==========

The *fledge-south-mqtt-readings* plugin allows to create an MQTT subscriber service. MQTT Subscriber reads messages from topics on the MQTT broker.

To create a south service you, as with any other south plugin

  - Select *South* from the left hand menu bar

  - Click on the + icon in the top right

  - Choose mqtt-readings from the plugin selection list

  - Name your service

  - Click on *Next*

  - Configure the plugin

    +------------+
    | |mqtt-sub| |
    +------------+

    - **MQTT Broker host**: Hostname or IP address of the broker to connect to.

    - **MQTT Broker Port**: The network port of the broker.

    - **Username**: Username for broker authentication.

    - **Password**: Password for broker authentication.

    - **Keep Alive Interval**: Maximum period in seconds allowed between communications with the broker. If no other messages are being exchanged, this controls the rate at which the client will send ping messages to the broker.

    - **Topic To Subscribe**: The subscription topic to subscribe to receive messages.

    - **QoS Level**: The desired quality of service level for the subscription.

    - **Asset Name**: Name of Asset.

  - Click *Next*

  - Enable your service and click *Done*


Message Payload
---------------

The content of the message payload published to the topic, to which the service is configured to subscribe, 
should be parsable to a JSON object.

e.g. `'{"humidity": 93.29, "temp": 16.82}'`

.. code-block:: console

  $ mosquitto_pub -h localhost -t "Room1/conditions" -m '{"humidity": 93.29, "temp": 16.82}'

The mosquitto_pub client utility comes with the mosquitto package, and a great tool for conducting quick tests and troubleshooting.
https://mosquitto.org/man/mosquitto_pub-1.html
