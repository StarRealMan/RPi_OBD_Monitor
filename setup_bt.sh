bluetoothctl

power on
agent on

pair $1
trust $1

quit

sudo rfcomm bind rfcomm0 $1