#!/usr/bin/env python3
# thoth-glyph
# Copyright(C) 2020 Red Hat, Inc.
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Module containing all supported Machine Learning models."""

from os import path
from typing import List
import logging

from fasttext import load_model
import pandas as pd

_LOGGER = logging.getLogger(__name__)
DEFAULT_FASTTEXT_MODEL_PATH = path.join(path.dirname(__file__), "data/model_commits_v2_quant.bin")


class FasttextModel:
    """A model that classifies messages using fasttext."""

    @staticmethod
    def classify_message(message: str) -> str:
        """Classify a single message."""
        _LOGGER.info("Model Path : " + DEFAULT_FASTTEXT_MODEL_PATH)
        classifier = load_model(DEFAULT_FASTTEXT_MODEL_PATH)
        label = classifier.predict(message.lower())
        label_string = str(label[0][0])[9:]
        return label_string

    @staticmethod
    def classify_messages(messages: List[str]) -> pd.DataFrame:
        """Classify multiple messages."""
        df = pd.DataFrame(messages, columns=["message"])
        df = df.replace("\n", "", regex=True)
        commits = list(df["message"].astype(str))
        _LOGGER.info("Model Path : " + DEFAULT_FASTTEXT_MODEL_PATH)
        classifier = load_model(DEFAULT_FASTTEXT_MODEL_PATH)
        labels = classifier.predict(commits)
        res = list(zip(*labels))
        res_list = [x[0] for x in res]
        lst2 = [item[0] for item in res_list]
        df["labels_predicted"] = lst2
        df["labels_predicted"] = df["labels_predicted"].map(lambda x: x[9:])
        _LOGGER.info(str(len(messages)) + " commits classified")
        return df
