#!/bin/sh
python api/app.py &
python scripts/mqtt_to_baesapi.py &


wait
