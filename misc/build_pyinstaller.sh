#!/bin/bash
set -euxo pipefail

pip install --verbose .

pyinstaller --log-level=DEBUG --name sms-doorman --onefile src/sms_doorman/main.py
pyinstaller --log-level=DEBUG --name door-ctl --onefile src/sms_doorman/door_controller.py
