#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

echo "#!/bin/bash" > /etc/rc.local
echo "/usr/bin/isticktoit_usb" >> /etc/rc.local
echo "sudo python3 $SCRIPTPATH/server.py &" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local
chmod +x /etc/rc.local
