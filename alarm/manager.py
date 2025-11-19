from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Set
import time


@dataclass
class AlarmState:
    on: bool = False
    deadline: Optional[float] = None  # monotonic time when alarm should turn off


class AlarmManager:
    def __init__(self, grace_seconds: float = 3.0):
        self.grace = grace_seconds
        self.state: Dict[int, AlarmState] = {}

    def set_on(self, tid: int):
        st = self.state.setdefault(tid, AlarmState())
        st.on = True
        st.deadline = None

    def start_countdown(self, tid: int, now: Optional[float] = None):
        st = self.state.setdefault(tid, AlarmState())
        if st.on and st.deadline is None:
            st.deadline = (now if now is not None else time.monotonic()) + self.grace

    def clear_if_elapsed(self, tid: int, now: Optional[float] = None):
        st = self.state.get(tid)
        if not st:
            return
        tnow = now if now is not None else time.monotonic()
        if st.deadline is not None and tnow >= st.deadline:
            st.on = False
            st.deadline = None

    def update(self, ids_in_zone: Set[int], visible_ids: Set[int], now: Optional[float] = None):
        tnow = now if now is not None else time.monotonic()
        # First, process ids in zone -> force ON and cancel timers
        for tid in ids_in_zone:
            st = self.state.setdefault(tid, AlarmState())
            st.on = True
            st.deadline = None
        # For any tracked id that is visible but not in zone, if alarm ON, start countdown
        for tid, st in self.state.items():
            if tid not in ids_in_zone:
                if st.on:
                    if tid in visible_ids:
                        if st.deadline is None:
                            st.deadline = tnow + self.grace
                    else:
                        if st.deadline is None:
                            st.deadline = tnow + self.grace
        # Clear alarms whose deadlines elapsed
        for tid in list(self.state.keys()):
            self.clear_if_elapsed(tid, now=tnow)

    def is_on(self, tid: int) -> bool:
        st = self.state.get(tid)
        return bool(st and st.on)

    def any_on(self) -> bool:
        return any(st.on for st in self.state.values())
