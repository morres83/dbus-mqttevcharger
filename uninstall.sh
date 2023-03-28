#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SERVICE_NAME=$(basename $SCRIPT_DIR)

sed -i '/dbus-mqttevcharger/d' /data/rc.local

rm /service/$SERVICE_NAME
kill $(pgrep -f 'supervise dbus-mqttevcharger')
chmod a-x $SCRIPT_DIR/service/run
./restart.sh
