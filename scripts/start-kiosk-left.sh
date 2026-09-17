#!/bin/bash

export DISPLAY=:0
export XAUTHORITY=/home/ignite/.Xauthority

sleep 8

until curl -s http://127.0.0.1:5173/kiosk >/dev/null; do
    sleep 2
done

unclutter -idle 0 &

/usr/bin/chromium \
  --new-window \
  --kiosk \
  --window-position=0,0 \
  --window-size=1024,600 \
  --user-data-dir=/tmp/chromium-left \
  --password-store=basic \
  --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --disable-features=Translate \
  --disable-restore-session-state \
  --overscroll-history-navigation=0 \
  "http://127.0.0.1:5173/kiosk?screen=left"
