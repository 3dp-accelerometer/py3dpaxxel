from typing import Optional

from py3dpaxxel.controller.constants import OutputDataRateDelay, OutputDataRate, Range, Scale
from py3dpaxxel.controller.transfer_types import FirmwareVersion


class Samples:
    def __init__(self) -> None:
        self.separation_s: Optional[float] = None
        "time separation in-between samples (`1/sample_rate`)"
        self.rate: OutputDataRate = OutputDataRateDelay[OutputDataRate.ODR3200]
        "sample rate, ODR (output data rate)"
        self.range: Optional[Range] = None
        "sensor range in `g`"
        self.scale: Optional[Scale] = None
        "sensor scale: 10bit or full scale (each LSB is 3.9mg)"
        self.firmware_version: Optional[FirmwareVersion] = None
        "device firmware version"

        self.run = []
        "series number"
        self.index = []
        "index of sample in stream (this series)"
        self.timestamp_ms = []
        "recomputed `time_stamp` (offset) from first sample (`time_stamp=0`)"

        self.x = []
        "measured x-acceleration in mg"
        self.y = []
        "measured y-acceleration in mg"
        self.z = []
        "measured z-acceleration in mg"

    def __len__(self):
        return len(self.index)

    def is_empty(self) -> bool:
        return 0 == len(self.timestamp_ms)

    def has_meta(self) -> bool:
        return (self.separation_s is not None
                and self.rate is not None
                and self.range is not None
                and self.scale is not None)
