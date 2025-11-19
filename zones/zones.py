from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

import cv2
import numpy as np


@dataclass
class Zone:
    id: str
    label: str
    polygon: List[Tuple[int, int]]


def load_zones(path: str) -> Tuple[List[Zone], Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    zones: List[Zone] = []
    for z in data.get("zones", []):
        polygon = [(int(x), int(y)) for x, y in z["polygon"]]
        zones.append(Zone(id=z["id"], label=z.get("label", z["id"]), polygon=polygon))
    meta = data.get("meta", {})
    return zones, meta


def save_zones(path: str, zones: List[Zone], meta: Dict[str, Any]) -> None:
    data = {
        "zones": [
            {"id": z.id, "label": z.label, "polygon": [[int(x), int(y)] for x, y in z.polygon]}
            for z in zones
        ],
        "meta": meta,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def draw_zones(frame: np.ndarray, zones: List[Zone]) -> None:
    for z in zones:
        pts = np.array(z.polygon, dtype=np.int32)
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 255), thickness=2)
        # Put label near first vertex
        if len(z.polygon) > 0:
            x, y = z.polygon[0]
            cv2.putText(frame, z.label, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)


def point_in_polygon(point: Tuple[int, int], polygon: List[Tuple[int, int]]) -> bool:
    # Ray casting algorithm
    x, y = point
    n = len(polygon)
    inside = False
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        # Check if point is on vertex or edge
        if (y1 == y2) and (y == y1) and min(x1, x2) <= x <= max(x1, x2):
            return True
        # Check ray crossing
        intersects = ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1
        )
        if intersects:
            inside = not inside
    return inside


def bbox_center(bbox: Tuple[int, int, int, int]) -> Tuple[int, int]:
    x1, y1, x2, y2 = bbox
    return int((x1 + x2) / 2), int((y1 + y2) / 2)
