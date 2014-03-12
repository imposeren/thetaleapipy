#!/bin/sh

. $HOME/.Xdbus # should contain something like export DBUS_SESSION_BUS_ADDRESS=unix:abstract=/tmp/dbus-ca9xMGXf41,guid=2xf56c9x2abcxb5128
DISPLAY=:0 /usr/bin/python2.7 $HOME/repos/the-tale-api/demo_bot.py $1
