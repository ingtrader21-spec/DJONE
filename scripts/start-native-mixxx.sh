#!/usr/bin/env bash
set -euo pipefail
ENVFILE=/home/codestra/Desktop/DJONE/.env
TOKEN=$(sed -n 's/^DJONE_MIXXX_TOKEN=//p' "$ENVFILE")
test -n "$TOKEN"
export DJONE_MIXXX_TOKEN="$TOKEN"
export HOME=/home/codestra
export XDG_RUNTIME_DIR=/run/user/1000
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
PID=$(pgrep -u codestra -n gnome-shell || true)
if [ -n "$PID" ]; then
 export DBUS_SESSION_BUS_ADDRESS=$(tr '\0' '\n' </proc/$PID/environ | sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p')
 export XAUTHORITY=$(tr '\0' '\n' </proc/$PID/environ | sed -n 's/^XAUTHORITY=//p')
fi
exec /home/codestra/Desktop/DJONE-Mixxx/mixxx-2.5.6/build-djone/mixxx
