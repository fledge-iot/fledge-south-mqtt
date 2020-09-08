==================
fledge-south-mqtt
==================

Fledge South MQTT subscriber Plugin


The MQTT broker service should be running. 
The example here and test are done using `mosquitto` http://test.mosquitto.org/

.. code-block:: console

    $ sudo apt install -y mosquitto
    $ sudo systemctl enable mosquitto.service


Install `python/requirements-mqtt.txt`


Run publisher script,

.. code-block:: console

    $ python3 -m mqtt-pub
    Published: {"humidity": 60.51} on MQTT Topic: Room1/conditions
    Published: {"humidity": 86.14} on MQTT Topic: Room1/conditions
