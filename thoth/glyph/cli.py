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

"""Glyph's CLI Interface."""

import logging
from typing import Optional

import click
from thoth.common import init_logging

from thoth.glyph import __title__
from thoth.glyph import __version__ as glyph_version
from thoth.glyph import classify_message
from thoth.glyph import classify_by_date
from thoth.glyph import classify_by_tag
from thoth.glyph import MLModel

init_logging()
_LOGGER = logging.getLogger(__title__)


def _print_version(ctx: click.Context, _, value: str):
    """Print glyph version and exit."""
    if not value or ctx.resilient_parsing:
        return

    click.echo(glyph_version)
    ctx.exit()


@click.group()
@click.pass_context
@click.option(
    "-v", "--verbose", is_flag=True, envvar="THOTH_ADVISER_DEBUG", help="Be verbose about what's going on.",
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
    "--message", "-m", type=str, required=True, help="Commit message to be classified",
)
@click.option(
    "--model",
    default=MLModel.DEFAULT.name.lower(),
    type=click.Choice([e.name.lower() for e in MLModel]),
    help="Type of classifer",
)
def classify(message: str, model: str) -> None:
    """Generate CHANGELOG entries from the current Git project."""
    _LOGGER.info("Classifying commit")
    model = MLModel.by_name(model)
    print("Label : " + classify_message(message, model))


@cli.command("classify-repo")
@click.option("--path", "-p", type=str, required=True, help="Path to Git repository")
@click.option("--start", type=str, help="Starting date")
@click.option("--end", type=str, help="End date")
@click.option("--output", type=str, help="Generated output file")
@click.option(
    "--model",
    default=MLModel.DEFAULT.name.lower(),
    type=click.Choice([e.name.lower() for e in MLModel]),
    help="Type of classifer",
)
def classifybydate(path: str, start: str, end: str, output: str, model: str) -> None:
    _LOGGER.info("Classifying commits in the given date-range")
    model = MLModel.by_name(model)
    df = classify_by_date(path, start, end, model)
    if output is None:
        print(df)
    else:
        df.to_csv(output, sep="\t")


@cli.command("classify-repo-by-tag")
@click.option("--path", "-p", type=str, required=True, help="Path to Git repository")
@click.option("--start_tag", type=str, required=True, help="Start tag")
@click.option("--end_tag", type=str, help="End tag")
@click.option("--output", type=str, help="Generated output file")
@click.option(
    "--model",
    default=MLModel.DEFAULT.name.lower(),
    type=click.Choice([e.name.lower() for e in MLModel]),
    help="Type of classifer",
)
def classifybytag(path: str, start_tag: str, end_tag: str, output: str, model: str) -> None:
    _LOGGER.info("Classifying commits between given tags")
    model = MLModel.by_name(model)
    df = classify_by_tag(path, start_tag, end_tag, model)
    if output is None:
        print(df)
    else:
        df.to_csv(output, sep="\t")


__name__ == "__main__" and cli()
