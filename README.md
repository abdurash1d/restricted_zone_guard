# Restricted Zone Guard

A simple system I built for detecting people entering restricted areas using YOLO and some tracking logic. It shows alarms when someone crosses into a zone and gives them a 3-second grace period.

## Install

Requires Python 3.11+. I used a virtual environment to keep things clean.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The YOLO model downloads automatically on first run. If you want it pre-downloaded:

```bash
python - <<'PY'
from ultralytics import YOLO
YOLO('yolov8n.pt')
PY
```

For GPU, get CUDA set up with PyTorch. Then use `--device gpu`.

## Run

Grab `test.mp4` from the task description, and make sure `restricted_zones.json` has your polygons.

```bash
python runner.py --video test.mp4 --zones restricted_zones.json --output output.mp4 --device cpu --use-tracker
```

Hit `q` to stop.

## File structure

- detector/model.py — Wraps YOLO to detect people
- tracker/tracker.py — Basic IOU tracker for IDs
- zones/zones.py — Handles loading zones from JSON, drawing them, and checking if points are inside
- alarm/manager.py — Manages alarms per person with timers
- runner.py — Main script that ties everything together, adds overlays, and saves video
- tests/ — Some unit tests for zones and alarms

## How it works (short)

Frame by frame: YOLO finds people, tracker assigns IDs, check if centers are in zones using ray casting. Alarm goes on right away inside, starts a 3s timer on exit or if person disappears. Display and save with overlays.

### DeepSORT

You could swap in DeepSORT from PyPI for better tracking. Just replace the tracker calls in runner.py, keep the alarm logic.

## Tests

```bash
PYTHONPATH=/home/abv/Project/restricted_zone_guard pytest -q
```
