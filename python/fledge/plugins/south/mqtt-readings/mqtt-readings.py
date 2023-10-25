# -*- coding: utf-8 -*-

# FLEDGE_BEGIN
# See: http://fledge-iot.readthedocs.io/
# FLEDGE_END

""" MQTT Subscriber 

TODO:

# MQTT v5 support using paho-mqtt v1.5.0 
    https://github.com/eclipse/paho.mqtt.python/blob/master/ChangeLog.txt

# broker bind_address
    The IP address of a local network interface to bind this client to, assuming multiple interfaces exist

# Subscriber
    topics
        This can either be a string or a list of strings if multiple topics should be subscribed to.
    msg_count
        the number of messages to retrieve from the broker. Defaults to 1. If >1, a list of MQTTMessages will be returned.
    retained
        set to True to consider retained messages, set to False to ignore messages with the retained flag set.
    client_id
        the MQTT client id to use. If “” or None, the Paho library will generate a client id automatically.
    will
        a dict containing will parameters for the client:
        
        will = {‘topic’: “<topic>”, ‘payload’:”<payload”>, ‘qos’:<qos>, ‘retain’:<retain>}.
        Topic is required, all other parameters are optional and will default to None, 0 and False respectively.

        Defaults to None, which indicates no will should be used.
    tls
        a dict containing TLS configuration parameters for the cient:

        dict = {‘ca_certs’:”<ca_certs>”, ‘certfile’:”<certfile>”, ‘keyfile’:”<keyfile>”, ‘tls_version’:”<tls_version>”, ‘ciphers’:”<ciphers”>}

        ca_certs is required, all other parameters are optional and will default to None if not provided, which results in the client using the default behaviour - see the paho.mqtt.client documentation.

        Defaults to None, which indicates that TLS should not be used.

    protocol
        choose the version of the MQTT protocol to use. Use either MQTTv31 or MQTTv311. 
"""

import asyncio
import copy
import json
import logging
import uuid

import paho.mqtt.client as mqtt

from fledge.common import logger
from fledge.plugins.common import utils
from fledge.services.south import exceptions
from fledge.services.south.ingest import Ingest
import async_ingest

__author__ = "Praveen Garg"
__copyright__ = "Copyright (c) 2020 Dianomic Systems, Inc."
__license__ = "Apache 2.0"
__version__ = "${VERSION}"

_LOGGER = logger.setup(__name__, level=logging.INFO)

c_callback = None
c_ingest_ref = None
loop = None

_DEFAULT_CONFIG = {
    'plugin': {
        'description': 'MQTT Subscriber South Plugin',
        'type': 'string',
        'default': 'mqtt-readings',
        'readonly': 'true'
    },
    'brokerHost': {
        'description': 'Hostname or IP address of the broker to connect to',
        'type': 'string',
        'default': 'localhost',
        'order': '1',
        'displayName': 'MQTT Broker host',
        'mandatory': 'true'
    },
    'brokerPort': {
        'description': 'The network port of the broker to connect to',
        'type': 'integer',
        'default': '1883',
        'order': '2',
        'displayName': 'MQTT Broker Port',
        'mandatory': 'true'
    },
    'username': {
        'description': 'Username for broker authentication',
        'type': 'string',
        'default': '',
        'order': '3',
        'displayName': 'Username'
    },
    'password': {
        'description': 'Password for broker authentication',
        'type': 'string',
        'default': '',
        'order': '4',
        'displayName': 'Password'
    },
    'keepAliveInterval': {
        'description': 'Maximum period in seconds allowed between communications with the broker. If no other messages are being exchanged, '
                        'this controls the rate at which the client will send ping messages to the broker.',
        'type': 'integer',
        'default': '60',
        'order': '5',
        'displayName': 'Keep Alive Interval'
    },
    'topic': {
        'description': 'The subscription topic to subscribe to receive messages',
        'type': 'string',
        'default': 'Room1/conditions',
        'order': '6',
        'displayName': 'Topic To Subscribe',
        'mandatory': 'true'
    },
    'qos': {
        'description': 'The desired quality of service level for the subscription',
        'type': 'integer',
        'default': '0',
        'order': '7',
        'displayName': 'QoS Level',
        'minimum': '0',
        'maximum': '2'
    },
    'assetName': {
        'description': 'Name of Asset',
        'type': 'string',
        'default': 'mqtt-',
        'order': '8',
        'displayName': 'Asset Name',
        'mandatory': 'true'
    }
}


def plugin_info():
    return {
        'name': 'MQTT Subscriber',
        'version': '2.2.0',
        'mode': 'async',
        'type': 'south',
        'interface': '1.0',
        'config': _DEFAULT_CONFIG
    }


def plugin_init(config):
    """Registers MQTT Subscriber Client

    Args:
        config: JSON configuration document for the South plugin configuration category
    Returns:
        handle: JSON object to be used in future calls to the plugin
    Raises:
    """
    handle = copy.deepcopy(config)
    handle["_mqtt"] = MqttSubscriberClient(handle)
    return handle


def plugin_start(handle):
    global loop
    loop = asyncio.new_event_loop()

    _LOGGER.info('Starting MQTT south plugin...')
    try:
        _mqtt = handle["_mqtt"]
        _mqtt.loop = loop
        _mqtt.start()
    except Exception as e:
        _LOGGER.exception(str(e))
    else:
        _LOGGER.info('MQTT south plugin started.')

def plugin_reconfigure(handle, new_config):
    """ Reconfigures the plugin

    it should be called when the configuration of the plugin is changed during the operation of the South service;
    The new configuration category should be passed.

    Args:
        handle: handle returned by the plugin initialisation call
        new_config: JSON object representing the new configuration category for the category
    Returns:
        new_handle: new handle to be used in the future calls
    Raises:
    """
    _LOGGER.info('Reconfiguring MQTT south plugin...')
    plugin_shutdown(handle)

    new_handle = plugin_init(new_config)
    plugin_start(new_handle)

    _LOGGER.info('MQTT south plugin reconfigured.')
    return new_handle


def plugin_shutdown(handle):
    """ Shut down the plugin

    To be called prior to the South service being shut down.

    Args:
        handle: handle returned by the plugin initialisation call
    Returns:
    Raises:
    """
    global loop
    try:
        _LOGGER.info('Shutting down MQTT south plugin...')
        _mqtt = handle["_mqtt"]
        _mqtt.stop()
        
        loop.stop()
        loop = None
    except Exception as e:
        _LOGGER.exception(str(e))
    else:
        _LOGGER.info('MQTT south plugin shut down.')


def plugin_register_ingest(handle, callback, ingest_ref):
    """ Required plugin interface component to communicate to South C server
    Args:
        handle: handle returned by the plugin initialisation call
        callback: C opaque object required to passed back to C->ingest method
        ingest_ref: C opaque object required to passed back to C->ingest method
    """
    global c_callback, c_ingest_ref
    c_callback = callback
    c_ingest_ref = ingest_ref


class MqttSubscriberClient(object):
    """ mqtt listener class"""

    __slots__ = ['mqtt_client', 'broker_host', 'broker_port', 'username', 'password', 'topic', 'qos', 'keep_alive_interval', 'asset', 'loop']

    def __init__(self, config):
        self.mqtt_client = mqtt.Client()
        self.broker_host = config['brokerHost']['value']
        self.broker_port = int(config['brokerPort']['value'])
        self.username = config['username']['value']
        self.password = config['password']['value']
        self.topic = config['topic']['value']
        self.qos = int(config['qos']['value'])
        self.keep_alive_interval = int(config['keepAliveInterval']['value'])
        self.asset = config['assetName']['value']

    def on_connect(self, client, userdata, flags, rc):
        """ The callback for when the client receives a CONNACK response from the server
        """
        client.connected_flag = True
        # subscribe at given Topic on connect
        client.subscribe(self.topic, self.qos)
        _LOGGER.info("MQTT connected. Subscribed the topic: %s", self.topic)

    def on_disconnect(self, client, userdata, rc):
        pass

    def on_message(self, client, userdata, msg):
        """ The callback for when a PUBLISH message is received from the server
        """
        _LOGGER.info("MQTT Received message; Topic: %s, Payload: %s  with QoS: %s", str(msg.topic), str(msg.payload),
                     str(msg.qos))

        self.loop.run_until_complete(self.save(msg))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        pass

    def on_unsubscribe(self, client, userdata, mid):
        pass

    def start(self):
        if self.username and len(self.username.strip()) and self.password and len(self.password):
            # no strip on pwd len check, as it can be all spaces?!
            self.mqtt_client.username_pw_set(self.username, password=self.password)
        # event callbacks
        self.mqtt_client.on_connect = self.on_connect

        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_message = self.on_message

        self.mqtt_client.on_disconnect = self.on_disconnect

        self.mqtt_client.connect(self.broker_host, self.broker_port, self.keep_alive_interval)
        _LOGGER.info("MQTT connecting..., Broker Host: %s, Port: %s", self.broker_host, self.broker_port)

        self.mqtt_client.loop_start()

    def stop(self):
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()

    async def save(self, msg):
        """Store msg content to Fledge """
        # TODO: string and other types?
        payload_json = json.loads(msg.payload.decode('utf-8'))
        _LOGGER.debug("Ingesting %s on topic %s", payload_json, str(msg.topic)) 
        data = {
            'asset': self.asset,
            'timestamp': utils.local_timestamp(),
            'readings': payload_json
        }
        async_ingest.ingest_callback(c_callback, c_ingest_ref, data)
