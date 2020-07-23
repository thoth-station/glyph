#!/usr/bin/env python3
# thoth-glyph
# Copyright(C) 2020 Tushar Sharma <tussharm@redhat.com>
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
from typing import Optional

import click
import os
from os import path
from thoth.common import init_logging
from thoth.glyph import __version__ as glyph_version
from fasttext import load_model

import pandas as pd
from pygit2 import Repository
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE

import time
import datetime
import sys

init_logging()

_LOGGER = logging.getLogger("glyph")

DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data/model_commits_v2_quant.bin")

def _print_version(ctx: click.Context, _, value: str):
    """Print glyph version and exit."""
    if not value or ctx.resilient_parsing:
        return

    click.echo(glyph_version)
    ctx.exit()


@click.group()
@click.pass_context
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    envvar="THOTH_ADVISER_DEBUG",
    help="Be verbose about what's going on.",
)
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    callback=_print_version,
    expose_value=False,
    help="Print adviser version and exit.",
)
def cli(ctx: Optional[click.Context] = None, verbose: bool = False):
    """Glyph command line interface."""
    if ctx:
        ctx.auto_envvar_prefix = "GLYPH"

    if verbose:
        _LOGGER.setLevel(logging.DEBUG)

    _LOGGER.debug("Debug mode is on")
    _LOGGER.info("Version: %s", glyph_version)


@cli.command()
@click.option(
    "--output",
    "-o",
    type=str,
    envvar="GLYPH_OUTPUT",
    metavar="FILE",
    default="-",
    help="Output file where the generated output should be stored, defaults to stdout if not provided.",
)
def generate(output: str) -> None:
    """Generate CHANGELOG entries from the current Git project."""
    _LOGGER.info("Hello, glyph!")
    if output == "-":
        click.echo("generated output")
    else:
        with open(output, "w") as output_file:
            output_file.write("some output generated to file\n")
        _LOGGER.info("Generated output stored in %r", output)

@cli.command()
@click.option(
    "--message",
    "-m",
    type=str,
    required=True,
    help="Commit message to be classified",
)
def classify(message: str) -> None:
    """Generate CHANGELOG entries from the current Git project."""
    _LOGGER.info("Hello, glyph!")
    _LOGGER.info("Model Path : " + DEFAULT_MODEL_PATH)
    classifier = load_model(DEFAULT_MODEL_PATH) 
    label = classifier.predict(message.lower())
    click.echo("Label : " + str(label[0][0])[8:])

@cli.command("classify-repo")
@click.option(
    "--path",
    "-p",
    type=str,
    required=True,
    help="Path to Git repository"
)
@click.option(
    "--start",
    type=str,
    help="Starting date"
)
@click.option(
    "--end",
    type=str,
    help="End date"
)
@click.option(
    "--output",
    type=str,
    help="Generated output file"
)
@click.option(
    "--model",
    type=str,
    help="Path to model"
)
def classifybydate(path: str, start: str, end: str, output: str, model:str) -> None:
    _LOGGER.info("Classifying commits in the given date-range")
    classify_by_date(path, start, end, output, model)


@cli.command("classify-repo-by-tag")
@click.option(
    "--path",
    "-p",
    type=str,
    required=True,
    help="Path to Git repository"
)
@click.option(
    "--start_tag",
    type=str,
    help="Starting date"
)
@click.option(
    "--end_tag",
    type=str,
    help="End date"
)
@click.option(
    "--output",
    type=str,
    help="Generated output file"
)
@click.option(
    "--model",
    type=str,
    help="Path to model"
)
def classifybytag(path: str, start_tag: str, end_tag:str, output: str, model:str) -> None:
    _LOGGER.info("Classifying commits between given tags")
    classify_by_tag(path, start_tag, end_tag, output, model)


def classify_by_date(path, start, end, output, model):
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
        _LOGGER.error("Git repository not found")
        return

    orig_messages = []
    for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):
        if(commit.commit_time > start_time and commit.commit_time < end_time):
             orig_messages.append(commit.message.lower())

    classify_messages(orig_messages, model, output)


def classify_by_tag(path, start_tag, end_tag, output, model):
    repo_path = os.path.join(path, ".git")
    if os.path.exists(repo_path):
        repo = Repository(repo_path)
    else:
        _LOGGER.error("Git repository not found")
        return

    start_tag = repo.revparse_single('refs/tags/' + start_tag)
    end_tag = repo.revparse_single('refs/tags/' + end_tag)
    orig_messages = []
    for commit in repo.walk(end_tag.id, GIT_SORT_TOPOLOGICAL):
        if commit.id == start_tag.get_object().id:
            break
        else:
            orig_messages.append(commit.message.lower())
    
    classify_messages(orig_messages, model, output)


def classify_messages(messages, model, output):
    if(messages is None or len(messages) == 0):
        _LOGGER.error("No commits found!")
        return

    df = pd.DataFrame(messages, columns = ['message'])
    df = df.replace('\n','', regex=True)
    commits = list(df['message'].astype(str))
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
    df['labels_predicted'] = lst2
    if output is None:
        print(df)
    else:
        df.to_csv(output, sep='\t')

    print(str(len(messages)) + " commits classified")

__name__ == "__main__" and cli()