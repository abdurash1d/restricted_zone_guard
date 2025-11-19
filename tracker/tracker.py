from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Track:
    track_id: int
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    conf: float
    misses: int = 0


def iou(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1, inter_y1 = max(ax1, bx1), max(ay1, by1)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, inter_x2 - inter_x1), max(0, inter_y2 - inter_y1)
    inter = iw * ih
    if inter == 0:
        return 0.0
    area_a = (ax2 - ax1) * (ay2 - ay1)
    area_b = (bx2 - bx1) * (by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


class IOUTracker:
    def __init__(self, max_misses: int = 10, iou_thresh: float = 0.3):
        self.next_id = 1
        self.tracks: Dict[int, Track] = {}
        self.max_misses = max_misses
        self.iou_thresh = iou_thresh

    def update(self, detections: List[Tuple[int, int, int, int, float]]) -> List[Tuple[int, Tuple[int, int, int, int], float]]:
        # detections: list of (x1,y1,x2,y2,conf)
        assigned = set()
        # Associate existing tracks
        for tid, tr in list(self.tracks.items()):
            best_idx, best_iou = -1, 0.0
            for idx, (x1, y1, x2, y2, conf) in enumerate(detections):
                if idx in assigned:
                    continue
                i = iou(tr.bbox, (x1, y1, x2, y2))
                if i > best_iou:
                    best_iou, best_idx = i, idx
            if best_idx >= 0 and best_iou >= self.iou_thresh:
                x1, y1, x2, y2, conf = detections[best_idx]
                tr.bbox = (x1, y1, x2, y2)
                tr.conf = conf
                tr.misses = 0
                assigned.add(best_idx)
            else:
                tr.misses += 1
                if tr.misses > self.max_misses:
                    del self.tracks[tid]
        # Create new tracks for unassigned detections
        for idx, (x1, y1, x2, y2, conf) in enumerate(detections):
            if idx in assigned:
                continue
            tid = self.next_id
            self.next_id += 1
            self.tracks[tid] = Track(tid, (x1, y1, x2, y2), conf)
        # Output active tracks
        return [(tid, tr.bbox, tr.conf) for tid, tr in self.tracks.items()]
