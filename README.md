# dbus-mqttevcharger
Integrate EV charger into Victron Energies Venus OS by MQTT

## Purpose
This script supports reading EV charger values from MQTT base charger. Writing values is supported for "Enable charging"and  "Charging current" 

## Install & Configuration
### Get the code
Just grap a copy of the main branche and copy them to a folder under `/data/` e.g. `/data/dbus-mqttevcharger`.
After that call the install.sh script.

The following script should do everything for you:
```
wget https://github.com/morres83/dbus-mqttevcharger/archive/refs/heads/main.zip
unzip main.zip "dbus-mqttevsharger-main/*" -d /data
mv /data/dbus-mqttevcharger-main /data/dbus-mqttevcharger
chmod a+x /data/dbus-mqttevcharger/install.sh
/data/dbus-mqttevcharger/install.sh
rm main.zip
```
⚠️ Check configuration after that - because service is already installed an running and with wrong connection data (host) you will spam the log-file

## Usefull links
Many thanks. @vikt0rm, @fabian-lauer, @trixing and @Marv2190 project:
- https://github.com/trixing/venus.dbus-twc3
- https://github.com/fabian-lauer/dbus-shelly-3em-smartmeter
- https://github.com/vikt0rm/dbus-goecharger
- https://github.com/Marv2190/venus.dbus-MqttToGridMeter
