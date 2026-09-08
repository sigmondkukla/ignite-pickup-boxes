#!/bin/bash

export DISPLAY=:0
export XAUTHORITY=/home/ignite/.Xauthority

echo "Starting kiosk at $(date)" > /tmp/kiosk-debug.log

sleep 25

xrandr --output HDMI-A-2 --primary --mode 1024x600 --pos 0x0 \
       --output HDMI-A-1 --mode 1024x600 --pos 1024x0

sleep 2

pkill -9 chromium || true
pkill -9 chromium-browser || true
sleep 2

chromium \
  --user-data-dir=/home/ignite/.config/chromium-dual \
  --password-store=basic \
  --app="http://127.0.0.1:5173/kiosk-dual.html" \
  --window-position=0,0 \
  --window-size=2048,600 \
  --start-fullscreen \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-features=Translate,HttpsUpgrades,HttpsFirstBalancedModeAuto \
  --overscroll-history-navigation=0
