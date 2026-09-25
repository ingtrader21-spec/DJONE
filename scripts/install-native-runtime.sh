#!/usr/bin/env bash
set -euo pipefail
install -Dm755 scripts/start-native-mixxx.sh /home/codestra/DJONE-Mixxx/runtime/start-mixxx.sh
install -Dm644 infra/systemd/djone-mixxx.service /home/codestra/.config/systemd/user/djone-mixxx.service
sudo install -Dm644 infra/systemd/djone-mixxx-relay.service /etc/systemd/system/djone-mixxx-relay.service
systemctl --user daemon-reload
systemctl --user enable --now djone-mixxx.service
sudo systemctl daemon-reload
sudo systemctl enable --now djone-mixxx-relay.service
