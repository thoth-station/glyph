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

"""Generate CHANGELOG entries out of commit messages using AI/ML techniques."""

import logging
import os
from os import path
from fasttext import load_model

import pandas as pd
from pygit2 import Repository
from pygit2 import GIT_SORT_TOPOLOGICAL

import time
import datetime
import sys

from thoth.glyph import __name__
from .exceptions import RepositoryNotFoundException
from .exceptions import ModelNotFoundException
from .exceptions import NoMessageEnteredException

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

    df = pd.DataFrame(messages, columns=["message"])
    df = df.replace("\n", "", regex=True)
    commits = list(df["message"].astype(str))
    if model is None:
        _LOGGER.info("Using default model")
        model = DEFAULT_MODEL_PATH
    elif not os.path.exists(model):
        _LOGGER.error("Model not found, using default model instead")
        model = DEFAULT_MODEL_PATH

    _LOGGER.info("Model Path : " + model)
    classifier = load_model(model)
    labels = classifier.predict(commits)
    res = list(zip(*labels))
    res_list = [x[0] for x in res]
    lst2 = [item[0] for item in res_list]
    df["labels_predicted"] = lst2
    _LOGGER.info(str(len(messages)) + " commits classified")
    return df


def classify_message(message: str, model: str) -> str:
    if message is None or message.strip() == "":
        raise NoMessageEnteredException
    if model is None:
        _LOGGER.info("Using default model")
        model = DEFAULT_MODEL_PATH
    elif not os.path.exists(model):
        raise ModelNotFoundException

    _LOGGER.info("Model Path : " + model)
    classifier = load_model(model)
    label = classifier.predict(message.lower())
    label_string = str(label[0][0])[9:]
    _LOGGER.info("Label : " + label_string)
    return label_string
