from __future__ import annotations

import os
from typing import List, Tuple

import numpy as np

try:
    from ultralytics import YOLO  # type: ignore
except Exception:  # pragma: no cover
    YOLO = None  # type: ignore


class Detection:
    def __init__(self, bbox: Tuple[int, int, int, int], conf: float, cls_id: int):
        self.bbox = bbox  # x1, y1, x2, y2
        self.conf = conf
        self.cls_id = cls_id

    def to_tuple(self):
        return self.bbox + (self.conf, self.cls_id)


class PeopleDetector:
    def __init__(self, weights: str = "yolov8n.pt", device: str = "cpu"):
        if YOLO is None:
            raise RuntimeError(
                "ultralytics is not installed. Please pip install ultralytics to use the detector."
            )
        self.model = YOLO(weights)
        self.device = device

    def detect(self, frame: np.ndarray, conf: float = 0.4) -> List[Detection]:
        results = self.model.predict(
            source=frame, verbose=False, device=0 if self.device == "gpu" else "cpu", conf=conf
        )
        dets: List[Detection] = []
        for r in results:
            if r.boxes is None:
                continue
            boxes = r.boxes
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            clss = boxes.cls.cpu().numpy().astype(int)
            for (x1, y1, x2, y2), c, cls in zip(xyxy, confs, clss):
                if cls != 0:  # class 0 is 'person'
                    continue
                dets.append(
                    Detection(
                        (int(x1), int(y1), int(x2), int(y2)), float(c), int(cls)
                    )
                )
        return dets
