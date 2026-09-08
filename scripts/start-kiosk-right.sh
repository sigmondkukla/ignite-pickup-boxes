#!/bin/bash

export DISPLAY=:0
export XAUTHORITY=/home/ignite/.Xauthority

sleep 8

until curl -s http://127.0.0.1:5173/kiosk >/dev/null; do
    sleep 2
done

/usr/bin/chromium \
  --new-window \
  --kiosk \
  --window-position=1024,0 \
  --window-size=1024,600 \
  --user-data-dir=/tmp/chromium-right \
  --password-store=basic \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-features=Translate \
  --disable-restore-session-state \
  --overscroll-history-navigation=0 \
  "http://127.0.0.1:5173/kiosk?screen=right"
