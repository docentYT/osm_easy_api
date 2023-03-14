from __future__ import annotations
from enum import Enum
import gzip
from typing import Generator

import requests

from .diff_parser import OsmChange_parser, OsmChange_parser_generator
from ..data_classes import Tags, Node, Way, Relation, OsmChange, Action
from ..data_classes.OsmChange import Meta

from ..utils import join_url, write_gzip_to_file

class Frequency(Enum):
    MINUTE = 0
    HOUR = 1
    DAY = 2

def frequency_to_str(frequency: Frequency) -> str:
    match frequency:
        case Frequency.MINUTE:  return "minute"
        case Frequency.HOUR:    return "hour"
        case Frequency.DAY:     return "day"

class Diff():
    def __init__(self, frequency: Frequency, url: str = "https://planet.openstreetmap.org/replication", standard_url_frequency_format: bool = True, user_agent: str | None = None):
        self.url = url
        self.frequency = frequency
        self.standard_url_frequency_format = standard_url_frequency_format

        if user_agent:
            self._user_agent = user_agent

    @staticmethod
    def _get_sequence_number_from_state(state_txt: str) -> str:
        """Extracts sequenceNumber from state.txt file.

        Args:
            state_txt (str): Raw state.txt file from diff server.

        Returns:
            str: sequence number
        """
        sequence_number = ""

        sequence_number_index = state_txt.find("sequenceNumber")
        sequence_number = state_txt[sequence_number_index+15:]  # 15 = numbers of letters in "sequenceNumber" & '='

        timestamp_index = sequence_number.find("timestamp")
        sequence_number = sequence_number[:timestamp_index]

        return sequence_number.removesuffix('\n')

    def _get_state(self) -> str:
        """Downloads state.txt file content from diff server."""
        if (self.standard_url_frequency_format): url = join_url(self.url, frequency_to_str(self.frequency), "state.txt")
        else: url = join_url(self.url, "state.txt")
        headers = {}
        if hasattr(self, "_user_agent"):
            headers.update({"User-Agent": self._user_agent})
        response = requests.get(url, headers=headers)
        if response.status_code != 200: raise ValueError(f"[ERROR::DIFF::_GET_STATE] API RESPONSE STATUS CODE: {response.status_code}")
        return response.text

    def get_sequence_number(self) -> str:
        """Gets newest sequence number from server.

        Returns:
            str: sequence number
        """
        return self._get_sequence_number_from_state(self._get_state())

    @staticmethod
    def _build_url(url: str, frequency: Frequency | None, sequence_number: str) -> str:
        """Builds diff url.

        Args:
            url (str): Url to diff server.
            frequency (Frequency): Frequency to download from.
            sequence_number (str): Sequence number to download.

        Returns:
            str: Url to .osc.gz file.
        """
        sequence_number = sequence_number.zfill(9)
        if (frequency):
            return join_url(url, frequency_to_str(frequency), sequence_number[:3], sequence_number[3:6], sequence_number[6:9] + ".osc.gz")
        else:
            return join_url(url, sequence_number[:3], sequence_number[3:6], sequence_number[6:9] + ".osc.gz")
    @staticmethod
    def _return_generator_or_OsmChange(file: gzip.GzipFile, tags: Tags | str, sequence_number: str | None, generator: bool) -> tuple[Meta, Generator[tuple[Action, Node | Way | Relation], None, None]] | OsmChange:
        """Returns tuple(Meta, generator) or OsmChange class depending on generator boolean."""
        if not generator: return OsmChange_parser(file, sequence_number, tags)

        gen_to_return = OsmChange_parser_generator(file, sequence_number, tags)
        meta = next(gen_to_return)
        # FIXME type problem below
        return (meta, gen_to_return) # type: ignore (First generator return will be Meta data. Idk why this is not working for typing.) 

    def get(self, sequence_number: str | None = None, file_to: str | None = None, file_from: str | None = None, tags: Tags | str = Tags(), generator: bool = True) -> tuple[Meta, Generator[tuple[Action, Node | Way | Relation], None, None]] | OsmChange:
        """Gets compressed diff file from server.

        Args:
            sequence_number (str, optional): Sequence number to download from. If no provided the newest diff will be downloaded.
            file_to (str, optional): Path to .xml.gz file where downloaded compressed data will be saved. Defaults get() method will no save file.
            file_from (str, optional): Path to .xml.gz file to parse data from.
            tags (Tags, optional): Useful if you want to prefetch specific tags. Other tags will be ignored.
            generator (bool, optional): Method should return generator or OsmChange class?. Defaults to True = generator.

        Returns:
            tuple[Meta, Generator[Node | Way | Relation, None, None]] | OsmChange: Returns Generator or OsmChange type depending on generator argument.
        """
    
        if file_from: 
            with gzip.open(file_from, "r") as f:
                return self._return_generator_or_OsmChange(f, tags, sequence_number, generator)

        if not sequence_number: sequence_number = self.get_sequence_number()

        if (self.standard_url_frequency_format): url = self._build_url(self.url, self.frequency, sequence_number)
        else: url = self._build_url(self.url, None, sequence_number)
        headers = {}
        if hasattr(self, "_user_agent"):
            headers.update({"User-Agent": self._user_agent})
        response = requests.get(url, stream=True, headers=headers)

        file = gzip.GzipFile(fileobj=response.raw)

        if file_to:
            write_gzip_to_file(file, file_to)
            with gzip.open(file_to, "r") as f:
                return self._return_generator_or_OsmChange(f, tags, sequence_number, generator)
                
        return self._return_generator_or_OsmChange(file, tags, sequence_number, generator)