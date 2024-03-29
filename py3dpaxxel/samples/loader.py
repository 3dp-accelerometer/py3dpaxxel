import csv
import logging
import re
from typing import Dict, Union

from py3dpaxxel.controller.constants import OutputDataRateDelay, OutputDataRate, Range, Scale
from py3dpaxxel.controller.transfer_types import FirmwareVersion
from py3dpaxxel.samples.samples import Samples


class SamplesLoader:
    """
    Class to load samples from a file.
    """

    TABULAR_DELIMITER_CHARACTER = " "
    "delimiter for .tsv file"
    LINE_COMMENT_CHARACTER = "#"
    "comments must start at beginning of line with LINE_COMMENT_CHARACTER"

    def __init__(self, in_filename: str) -> None:
        self.filename = in_filename

    def _try_read_metadata_if_any(self, samples: Samples) -> bool:
        # read metadata (if any): ODR, rate, scale
        found_meta = False
        with open(self.filename, "r") as f:
            for line in reversed(f.readlines()):
                if line[0] == "#":
                    sampling_args = eval(re.search("^# .*({.*})$", line).group(1))
                    samples.rate = OutputDataRate[sampling_args["sensor"]["rate"]]
                    samples.range = Range[sampling_args["sensor"]["range"]]
                    samples.scale = Scale[sampling_args["sensor"]["scale"]]
                    samples.firmware_version = FirmwareVersion.from_string(sampling_args["firmware"]["version"])
                    samples.separation_s = OutputDataRateDelay[samples.rate]
                    found_meta = True
                    break
        return found_meta

    def load(self) -> Samples:
        """
        Loads stores stream file.

        - ignores 1.st line which shall be the header (column names, i.e. `run sample x y z`)
        - interprets sample data, i.e.: `00 06399 +0538.200 +0187.200 +0600.600`
        - interpret last line (metadata), i.e.: `# { ..., sensor: {'rate': 'ODR3200', 'range': 'G4', 'scale': 'FULL_RES_4MG_LSB', 'version': '0.1.1'}}`

        :return: Samples
        """
        samples = Samples()
        if not self._try_read_metadata_if_any(samples):
            logging.warning(f"failed to read meta data: skipping file {self.filename}")
            return samples

        # read samples: requires pre-loaded metadata for timestamp reconstruction
        with open(self.filename, "r") as f:
            reader = csv.DictReader(filter(lambda line: line[0] != self.LINE_COMMENT_CHARACTER, f), delimiter=self.TABULAR_DELIMITER_CHARACTER)
            row: Dict[str, Union[int, float]]
            for row in reader:
                samples.run.append(int(row["seq"]))
                index = int(row["sample"])
                samples.index.append(index)
                samples.timestamp_ms.append(index * samples.separation_s * 1000)
                samples.x.append(float(row["x"]))
                samples.y.append(float(row["y"]))
                samples.z.append(float(row["z"]))

        return samples
