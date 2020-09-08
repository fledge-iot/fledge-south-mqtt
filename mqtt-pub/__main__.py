#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import random
import sys
import json
import threading

import paho.mqtt.client as mqtt


# MQTT config
MQTT_BROKER = "localhost"
# MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
KEEP_ALIVE_INTERVAL = 45


def on_connect(client, userdata, rc):
    if rc != 0:
        print("Unable to connect to MQTT Broker...")
    else:
        print("Connected with MQTT Broker: ", str(MQTT_BROKER))


def on_publish(client, userdata, mid):
    pass


def on_disconnect(client, userdata, rc):
    pass


# faking
def prepare_data():
    h = float("{0:.2f}".format(random.uniform(50, 100)))
    t = float("{0:.2f}".format(random.uniform(10, 40)))
    data = dict()
    data['humidity'] = h
    data['temp'] = t
    jdoc = json.dumps(data)
    return jdoc


def publish_now(message):
    topic = "Room1/conditions"
    mqttc.publish(topic, message)
    print("Published: " + str(message) + " " + "on MQTT Topic: " + str(topic))


def publish_fake_data():
    threading.Timer(3.0, publish_fake_data).start()
    publish_now(prepare_data())

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish

try:
    mqttc.connect(MQTT_BROKER, int(MQTT_PORT), int(KEEP_ALIVE_INTERVAL))
except ConnectionRefusedError as e:
    print(e)
    sys.exit(1)
else:
    publish_fake_data()
