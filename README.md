# Restricted Zone Guard

Simple intrusion detection pipeline using YOLO to detect people and a minimal IOU tracker, with per-ID alarm and 3s grace timer.

## Install

- Python 3.11+
- Create venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

YOLO weights will auto-download on first run (default `yolov8n.pt`). If you need to pre-download:

```bash
python - <<'PY'
from ultralytics import YOLO
YOLO('yolov8n.pt')
PY
```

GPU (optional): install CUDA toolkit/driver compatible with PyTorch used by Ultralytics. Then run with `--device gpu`.

## Run

Make sure `test.mp4` is present (obtain from TZ source or example video) and `restricted_zones.json` contains your polygon(s).

```bash
python runner.py --video test.mp4 --zones restricted_zones.json --output output.mp4 --device cpu --use-tracker
```

Press `q` to quit.

## File structure

- detector/model.py — YOLO wrapper (people only)
- tracker/tracker.py — simple IOU tracker
- zones/zones.py — load/save zones JSON, draw, point-in-polygon
- alarm/manager.py — per-ID alarm/timers
- runner.py — main loop, overlays, I/O
- tests/ — unit tests for zones and alarm

## How it works (short)

Each frame, YOLO detects people; IOU tracker assigns persistent IDs. We compute each track center and check containment in any restricted polygon via ray casting. The AlarmManager turns alarm ON immediately when inside, and starts a per-ID 3s countdown on exit or disappearance; re-entry cancels the timer. Frames are displayed and written to `output.mp4` with overlays.

### DeepSORT

You can replace the IOU tracker by integrating `deep-sort-realtime` (PyPI). Swap `IOUTracker` calls in `runner.py` with the library's tracker update, and pass detection bboxes/confs. Keep per-ID logic unchanged.

## Tests

```bash
PYTHONPATH=/home/abv/Project/restricted_zone_guard pytest -q
```
