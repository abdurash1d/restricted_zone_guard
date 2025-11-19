from __future__ import annotations

import argparse
from typing import List, Tuple

import cv2
import numpy as np

from detector.model import PeopleDetector, Detection
from tracker.tracker import IOUTracker
from zones.zones import load_zones, draw_zones, bbox_center, point_in_polygon
from alarm.manager import AlarmManager


def draw_bbox(frame, bbox, tid: int, alarm_on: bool, conf: float):
    x1, y1, x2, y2 = bbox
    color = (0, 0, 255) if alarm_on else (0, 255, 0)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    label = f"ID {tid} {conf:.2f}"
    cv2.putText(frame, label, (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", type=str, default="test.mp4")
    ap.add_argument("--zones", type=str, default="restricted_zones.json")
    ap.add_argument("--output", type=str, default="output.mp4")
    ap.add_argument("--device", type=str, default="cpu", choices=["cpu", "gpu"])
    ap.add_argument("--use-tracker", action="store_true")
    ap.add_argument("--conf", type=float, default=0.4)
    args = ap.parse_args()

    zones, meta = load_zones(args.zones)

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open video: {args.video}")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))

    detector = PeopleDetector(device=args.device)
    tracker = IOUTracker() if args.use_tracker else None
    alarms = AlarmManager(grace_seconds=3.0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        dets = detector.detect(frame, conf=args.conf)
        det_tuples: List[Tuple[int, int, int, int, float]] = [(*d.bbox, d.conf) for d in dets]
        tracks: List[Tuple[int, Tuple[int, int, int, int], float]] = []
        if tracker is not None:
            tracks = tracker.update(det_tuples)
        else:
            # Without tracker, assign ephemeral IDs per detection index (not stable across frames)
            tracks = [(i + 1, d.bbox, d.conf) for i, d in enumerate(dets)]

        ids_in_zone = set()
        visible_ids = set()
        for tid, bbox, conf in tracks:
            visible_ids.add(tid)
            center = bbox_center(bbox)
            for z in zones:
                if point_in_polygon(center, z.polygon):
                    ids_in_zone.add(tid)
                    break

        alarms.update(ids_in_zone=ids_in_zone, visible_ids=visible_ids)

        # Draw overlays
        draw_zones(frame, zones)
        for tid, bbox, conf in tracks:
            on = alarms.is_on(tid)
            draw_bbox(frame, bbox, tid, on, conf)
        if alarms.any_on():
            cv2.putText(frame, "ALARM!", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)

        cv2.imshow("Restricted Zone Guard", frame)
        out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
