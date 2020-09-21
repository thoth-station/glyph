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

"""Helper functions for the library."""

import logging
import os
from typing import Dict
from typing import List
from typing import Optional

from pygit2 import Repository
from pygit2 import GIT_SORT_TOPOLOGICAL

import datetime
import sys
import time

from .constants import Format
from .constants import MLModel
from .exceptions import NoMessageEnteredException
from .exceptions import ModelNotFoundException
from .exceptions import RepositoryNotFoundException
from .formatter import ClusterSimilar
from .models import FasttextModel

_LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "data/model_commits_v2_quant.bin")
CHECK_PHRASES = {"Automatic Updates": ["Automatic Update of dependency"]}


def classify_by_date(
    path: str, start: Optional[str] = None, end: Optional[str] = None, model: Optional[MLModel] = None
) -> List[str]:
    """Classify commits by date."""
    start_time = 0
    end_time = sys.maxsize

    if start is not None:
        start_time = int(time.mktime(datetime.datetime.strptime(start, "%Y-%m-%d").timetuple()))

    if end is not None:
        end_time = int(time.mktime(datetime.datetime.strptime(end, "%Y-%m-%d").timetuple()))

    repo_path = os.path.join(path, ".git")
    if os.path.exists(repo_path):
        repo = Repository(repo_path)
    else:
        raise RepositoryNotFoundException

    orig_messages = []
    for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
        if start_time < commit.commit_time < end_time:
            orig_messages.append(commit.message.lower())

    return classify_messages(orig_messages, model)


def classify_by_tag(
    path: str, start_tag: str, end_tag: Optional[str] = None, model: Optional[MLModel] = None
) -> List[str]:
    """Classify messages for the given repo based on tags."""
    repo_path = os.path.join(path, ".git")
    if os.path.exists(repo_path):
        repo = Repository(repo_path)
    else:
        raise RepositoryNotFoundException

    start_tag = repo.revparse_single("refs/tags/" + start_tag)

    if end_tag is None:
        end_tag = repo.revparse_single("refs/heads/master")
    else:
        end_tag = repo.revparse_single("refs/tags/" + end_tag)

    orig_messages = []
    walker = repo.walk(end_tag.id, GIT_SORT_TOPOLOGICAL)
    walker.hide(start_tag.id)

    for commit in walker:
        orig_messages.append(commit.message.lower())

    return classify_messages(orig_messages, model)


def classify_messages(messages: List[str], model: Optional[MLModel] = None) -> List[str]:
    """Classify messages."""
    if messages is None or len(messages) == 0:
        _LOGGER.error("No commits found!")
        return []

    if model is None:
        _LOGGER.info("Using default model")
        model = MLModel.DEFAULT

    if model == MLModel.FASTTEXT:
        return FasttextModel.classify_messages(messages)


def classify_message(message: str, model: Optional[MLModel] = None) -> str:
    """Classify a single message."""
    if message is None or message.strip() == "":
        raise NoMessageEnteredException

    if model is None:
        _LOGGER.info("Using default model")
        model = MLModel.DEFAULT

    if model == MLModel.FASTTEXT:
        return FasttextModel.classify_message(message)

    raise ModelNotFoundException(f"Unknown model: {model}")


def generate_log(messages: List[str], fmt: Format, model: Optional[str] = None) -> List[str]:
    """Classify changes based on messages."""
    if not messages:
        return []

    check_phrase_dict = {}
    filter_indices = []

    for phrase_heading in CHECK_PHRASES:
        for phrase in CHECK_PHRASES[phrase_heading]:
            for i in range(len(messages)):
                if phrase.lower() in messages[i].lower():
                    filter_indices.append(i)
                    if phrase_heading in check_phrase_dict:
                        temp = check_phrase_dict[phrase_heading]
                        temp.append(messages[i])
                        check_phrase_dict[phrase_heading] = temp
                    else:
                        check_phrase_dict[phrase_heading] = [messages[i]]

    messages = [v for i, v in enumerate(messages) if i not in filter_indices]
    df = classify_messages(messages, model)

    keys = ["features", "corrective", "perfective", "nonfunctional", "unknown"]
    message_dict = {}

    for key in keys:
        message_dict[key] = []

    predicted_labels = list(df["labels_predicted"].astype(str)) if len(df["labels_predicted"]) else []

    for i in range(len(messages)):
        label = predicted_labels[i]
        temp = message_dict[label]
        temp.append(messages[i])
        message_dict[label] = temp

    # TODO: This tranlational logic is only needed for this specific Fasttext model
    message_dict["Features"] = message_dict.pop("features")
    message_dict["Bug Fixes"] = message_dict.pop("corrective")
    message_dict["Improvements"] = message_dict.pop("perfective")
    message_dict["Non-functional"] = message_dict.pop("nonfunctional")
    message_dict["Other"] = message_dict.pop("unknown")
    for key in check_phrase_dict:
        message_dict[key] = check_phrase_dict[key]

    if model is None:
        _LOGGER.info("Using default format")
        model = Format.DEFAULT

    if fmt == Format.CLUSTER_SIMILAR:
        return ClusterSimilar.generate_log(message_dict)
