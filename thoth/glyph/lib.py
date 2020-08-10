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
from os import path

from pygit2 import Repository
from pygit2 import GIT_SORT_TOPOLOGICAL

import time
import datetime
import sys

from thoth.glyph import __name__
from .exceptions import RepositoryNotFoundException
from .exceptions import NoMessageEnteredException
from .constants import MLModel
from .constants import Format
from .models import FasttextModel
from .formatter import ClusterSimilar

_LOGGER = logging.getLogger(__name__)
DEFAULT_MODEL_PATH = path.join(path.dirname(__file__), "data/model_commits_v2_quant.bin")


def classify_by_date(path: str, start: str, end: str, model: str):
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
        if commit.commit_time > start_time and commit.commit_time < end_time:
            orig_messages.append(commit.message.lower())

    return classify_messages(orig_messages, model)


def classify_by_tag(path: str, start_tag: str, end_tag: str, model: str):
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


def classify_messages(messages: list, model: str):
    if messages is None or len(messages) == 0:
        _LOGGER.error("No commits found!")
        return

    if model is None:
        _LOGGER.info("Using default model")
        model = MLModel.DEFAULT

    if model == MLModel.FASTTEXT:
        return FasttextModel.classify_messages(messages)


def classify_message(message: str, model: str) -> str:
    if message is None or message.strip() == "":
        raise NoMessageEnteredException

    if model is None:
        _LOGGER.info("Using default model")
        model = MLModel.DEFAULT

    if model == MLModel.FASTTEXT:
        return FasttextModel.classify_message(message)


def generate_log(messages: list, format: str, model: str):
    df = classify_messages(messages, model)

    keys = ["features", "corrective", "perfective", "nonfunctional", "unknown"]
    message_dict = {}

    for key in keys:
        message_dict[key] = []

    predicted_labels = list(df["labels_predicted"].astype(str))

    for i in range(len(messages)):
        label = predicted_labels[i]
        temp = message_dict[label]
        temp.append(messages[i])
        message_dict[label] = temp

    # TODO: This tranlational logic is only needed for this specific Fasttext model
    message_dict["Features"] = message_dict.pop('features')
    message_dict["Bug Fixes"] = message_dict.pop('corrective')
    message_dict["Improvements"] = message_dict.pop('perfective')
    message_dict["Non-functional"] = message_dict.pop('nonfunctional')
    message_dict["Other"] = message_dict.pop('unknown')

    if model is None:
        _LOGGER.info("Using default format")
        return Format.DEFAULT

    if format == Format.CLUSTER_SIMILAR:
        return ClusterSimilar.generate_log(message_dict)
