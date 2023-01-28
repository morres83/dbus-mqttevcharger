# dbus-mqttevcharger
Integrate EV charger into Victron Energies Venus OS by MQTT

## Purpose
This script supports reading EV charger values from MQTT base charger. Writing values is supported for "Enable charging"and  "Charging current" 

## Install & Configuration
You have to run Paho Client on your GXDevice to make this script work

python -m ensurepip --upgrade
pip install paho-mqtt

Get two files from the [velib_python](https://github.com/victronenergy/velib_python) and install them on your venus:

        /data/data/dbus-mqttevcharger/vedbus.py
        /data/dbus-mqttevcharger/ve_utils.py


### Configuration

In the Python file, you should put the IP of your Broker

### Get the code
Just grap a copy of the main branche and copy them to a folder under `/data/` e.g. `/data/dbus-mqttevcharger`.
After that call the install.sh script.

The following script should do everything for you:
```
wget https://github.com/morres83/dbus-mqttevcharger/archive/refs/heads/main.zip
unzip main.zip -d /data
mv /data/dbus-mqttevcharger-main /data/dbus-mqttevcharger
chmod a+x /data/dbus-mqttevcharger/install.sh
/data/dbus-mqttevcharger/install.sh
rm main.zip
```
⚠️ Check configuration after that - because service is already installed an running and with wrong connection data (host) you will spam the log-file

### Debugging

You can check the status of the service with svstat:

`svstat /service/dbus-mqttevcharger`

It will show something like this:

`/service/dbus-mqttevcharger: up (pid 10078) 325 seconds`

If the number of seconds is always 0 or 1 or any other small number, it means that the service crashes and gets restarted all the time.

When you think that the script crashes, start it directly from the command line:

`python /data/dbus-mqttevcharger/dbus-mqttevcharger.py`

and see if it throws any error messages.


## Usefull links
Many thanks. @vikt0rm, @fabian-lauer, @trixing and @Marv2190 project:
- https://github.com/trixing/venus.dbus-twc3
- https://github.com/fabian-lauer/dbus-shelly-3em-smartmeter
- https://github.com/vikt0rm/dbus-goecharger
- https://github.com/Marv2190/venus.dbus-MqttToGridMeter
