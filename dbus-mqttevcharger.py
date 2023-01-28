#!/usr/bin/env python

"""
Changed a lot of a Script originall created by Ralf Zimmermann (mail@ralfzimmermann.de) in 2020.
The orginal code and its documentation can be found on: https://github.com/RalfZim/venus.dbus-fronius-smartmeter
Used https://github.com/victronenergy/velib_python/blob/master/dbusdummyservice.py as basis for this service.
"""

"""
/data/Pathtothisscript/vedbus.py
/data/Pathtothisscript/ve_utils.py
python -m ensurepip --upgrade
pip install paho-mqtt
"""
try:
  import gobject  # Python 2.x
except:
  from gi.repository import GLib as gobject # Python 3.x
import platform
import logging
import time
import sys
import json
import os
import paho.mqtt.client as mqtt
try:
  import thread   # for daemon = True  / Python 2.x
except:
  import _thread as thread   # for daemon = True  / Python 3.x

# our own packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../ext/velib_python'))
from vedbus import VeDbusService

path_UpdateIndex = '/UpdateIndex'

# MQTT Setup
broker_address = "localhost"
MQTTNAME = "venusEvMQTT"
evChargerMQTTPath = "evcharger/data" #qq umfaktorieren

# Variblen setzen
mqttConnected = 0
powerL1, powerL2, powerL3 = 0, 0, 0
totalCurrent, actualPower = 0, 0
auto_start_charging = True
charger_state, charging_time = 0,0
globalCurrent = 32

def on_disconnect(client, userdata, rc):
    global mqttConnected
    print("Client Got Disconnected")
    if rc != 0:
        print('Unexpected MQTT disconnection. Will auto-reconnect')

    else:
        print('rc value:' + str(rc))

    try:
        print("Trying to Reconnect")
        client.connect(broker_address)
        mqttConnected = 1
    except Exception as e:
        logging.exception("Fehler beim reconnecten mit Broker")
        print("Error in Retrying to Connect with Broker")
        mqttConnected = 0
        print(e)

def on_connect(client, userdata, flags, rc):
        global mqttConnected
        if rc == 0:
            print("Connected to MQTT Broker!")
            mqttConnected = 1
            client.subscribe(evChargerMQTTPath)
        else:
            print("Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):

    try:

        global powerL1, powerL2, powerL3, totalCurrent, actualPower, auto_start_charging, charger_state, charging_time, globalCurrent
        if msg.topic == evChargerMQTTPath:   # JSON String vom EVcharger
            if msg.payload != '{"value": null}' and msg.payload != b'{"value": null}':
                jsonpayload = json.loads(msg.payload)
                powerL1 = float(jsonpayload["powerL1"])
                powerL2 = float(jsonpayload["powerL2"])
                powerL3 = float(jsonpayload["powerL3"])
                totalCurrent = float(jsonpayload["totalCurrent"])
                actualPower = float(jsonpayload["actualPower"])
                auto_start_charging = bool(jsonpayload["auto_start_charging"])
                charger_state = int(jsonpayload["charger_state"])
                charging_time = int(jsonpayload["charging_time"]) / 1000
                globalCurrent = int(jsonpayload["global_current"]) / 1000
                
            else:
                print("Antwort vom MQTT war Null und wurde ignoriert")

    except Exception as e:
        logging.exception("Programm mqttToEVCharger ist abgestuerzt. (on message Funkion)")
        print(e)
        print("Im mqttToEVCharger Programm ist etwas beim auslesen der Nachrichten schief gegangen")


class DbusEvseChargerService:
    def __init__(self, servicename, paths, productname='WARP2-Charger', connection='WARP2_API'):

        deviceinstance = 43

        self._dbusservice = VeDbusService("{}.http_{:02d}".format(servicename, deviceinstance))
        self._paths = paths

        logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

        paths_wo_unit = [
            '/Status',
            # value 'state' EVSE State - 1 Not Connected - 2 Connected - 3 Charging - 4 Error, 254 - sleep, 255 - disabled
		# old_goecharger 1: charging station ready, no vehicle 2: vehicle loads 3: Waiting for vehicle 4: Charge finished, vehicle still connected
            '/Mode'
        ]

        # Create the management objects, as specified in the ccgx dbus-api document
        self._dbusservice.add_path('/Mgmt/ProcessName', __file__)
        self._dbusservice.add_path('/Mgmt/ProcessVersion',
                                   'Unkown version, and running on Python ' + platform.python_version())
        self._dbusservice.add_path('/Mgmt/Connection', connection)

        # Create the mandatory objects
        self._dbusservice.add_path('/DeviceInstance', deviceinstance)
        self._dbusservice.add_path('/ProductId', 0xFFFF)  #
        self._dbusservice.add_path('/ProductName', productname)
        self._dbusservice.add_path('/CustomName', productname)
        self._dbusservice.add_path('/FirmwareVersion', 0)
        self._dbusservice.add_path('/HardwareVersion', 2)
        self._dbusservice.add_path('/Serial', 0)
        self._dbusservice.add_path('/Connected', 1)
        self._dbusservice.add_path('/UpdateIndex', 0)

        # add paths without units
        for path in paths_wo_unit:
            self._dbusservice.add_path(path, None)

        # add path values to dbus
        for path, settings in self._paths.items():
            self._dbusservice.add_path(
                path, settings['initial'], gettextcallback=settings['textformat'], writeable=True,
                onchangecallback=self._handlechangedvalue)
      
        gobject.timeout_add(2000, self._update) # pause 2000ms before the next request

    def _update(self):
        self._dbusservice['/Ac/Energy/Forward'] = 0 #qq ??
        self._dbusservice['/Ac/L1/Power'] = round(powerL1, 2)
        self._dbusservice['/Ac/L2/Power'] = round(powerL2, 2)
        self._dbusservice['/Ac/L3/Power'] = round(powerL3, 2)
        self._dbusservice['/Ac/Power'] = round(actualPower, 2)
        self._dbusservice['/AutoStart'] = 1 if auto_start_charging else 0
        self._dbusservice['/ChargingTime'] = charging_time
        self._dbusservice['/Connected'] = mqttConnected
        self._dbusservice['/Current'] = totalCurrent
        if int(1) == 1: #qq ??
            self._dbusservice['/StartStop'] = 1
        else:
            self._dbusservice['/StartStop'] = 0
        self._dbusservice['/SetCurrent'] = globalCurrent
        self._dbusservice['/MaxCurrent'] = 32
        self._dbusservice['/Mode'] = 0  # Manual, no control
        
        status = 0
        if charger_state == 0:
            status = 0
        elif charger_state == 1 or charger_state == 2:
            status = 1
        elif charger_state == 3:
            status = 2
        
        self._dbusservice['/Status'] = status
      
        # increment UpdateIndex - to show that new data is available
        index = self._dbusservice[path_UpdateIndex] + 1  # increment index
        if index > 255:   # maximum value of the index
          index = 0       # overflow from 255 to 0
        self._dbusservice[path_UpdateIndex] = index
        return True
    
    def _setEvseChargerValue(self, parameter, value):
        #geänderte Werte schicken
        return True
        
    def _handlechangedvalue(self, path, value):##qq komplett
        logging.info("someone else updated %s to %s" % (path, value))

        if path == '/SetCurrent':
            return self._setEvseChargerValue('SC+', value)
        elif path == '/StartStop':
            return self._setEvseChargerValue('F', '1') #F1
        elif path == '/MaxCurrent':
            return self._setEvseChargerValue('ama', value)
        else:
            logging.info("mapping for evcharger path %s does not exist" % (path))
            return False

def main():
    # configure logging
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO,
                        handlers=[
                            logging.FileHandler("%s/current.log" % (os.path.dirname(os.path.realpath(__file__)))),
                            logging.StreamHandler()
                        ])

    try:
        logging.info("Start")

        from dbus.mainloop.glib import DBusGMainLoop
        # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
        DBusGMainLoop(set_as_default=True)

        # formatting
        _kwh = lambda p, v: (str(round(v, 2)) + 'kWh')
        _a = lambda p, v: (str(round(v, 1)) + 'A')
        _w = lambda p, v: (str(round(v, 1)) + 'W')
        _v = lambda p, v: (str(round(v, 1)) + 'V')
        _degC = lambda p, v: (str(v) + '°C')
        _s = lambda p, v: (str(v) + 's')

        # start our main-service
        pvac_output = DbusEvseChargerService(
            servicename='com.victronenergy.evcharger',
            paths={
                '/Ac/Power': {'initial': 0, 'textformat': _w},
                '/Ac/L1/Power': {'initial': 0, 'textformat': _w},
                '/Ac/L2/Power': {'initial': 0, 'textformat': _w},
                '/Ac/L3/Power': {'initial': 0, 'textformat': _w},
                '/Ac/Energy/Forward': {'initial': 0, 'textformat': _kwh},
                '/ChargingTime': {'initial': 0, 'textformat': _s},

                '/Ac/Voltage': {'initial': 0, 'textformat': _v},
                '/Current': {'initial': 0, 'textformat': _a},
                '/SetCurrent': {'initial': 0, 'textformat': _a},
                '/MaxCurrent': {'initial': 0, 'textformat': _a},
                '/MCU/Temperature': {'initial': 0, 'textformat': _degC},
                '/StartStop': {'initial': 0, 'textformat': lambda p, v: (str(v))}
            }
        )

        logging.info('Connected to dbus, and switching over to gobject.MainLoop() (= event based)')
        mainloop = gobject.MainLoop()
        mainloop.run()

    except Exception as e:
        logging.critical('Error at %s', 'main', exc_info=e)

# Konfiguration MQTT
client = mqtt.Client(MQTTNAME) # create new instance
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address)  # connect to broker

client.loop_start()


if __name__ == "__main__":
    main()
