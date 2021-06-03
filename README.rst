==========================
fledge-south-mqtt-readings
==========================

Fledge South MQTT Subscriber Plugin, Default MQTT version is v3.1.1; Use either MQTTv31 or MQTTv311. 


The MQTT broker service should be running.
 
The example given here are tested using `mosquitto` http://test.mosquitto.org/

.. code-block:: console

    $ sudo apt install -y mosquitto
    $ sudo systemctl enable mosquitto.service


Install `paho-mqtt` pip package. 

.. code-block:: console
    
    python3 -m pip install -r python/requirements-mqtt.txt


Run publisher script,

.. code-block:: console

    $ python3 -m mqtt-pub
    Published: {"humidity": 64.54, "temp": 27.02} on MQTT Topic: Room1/conditions
    Published: {"humidity": 69.43, "temp": 24.95} on MQTT Topic: Room1/conditions

or

.. code-block:: console

    $ mosquitto_pub -h localhost -t "Room1/conditions" -m '{"humidity": 93.29, "temp": 16.82}'

The Fledge plugin once configured to subscribe the topic `Room1/conditions` will start
ingesting the published messages payload.
