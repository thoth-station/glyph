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

"""Enums used in Glyph."""

from enum import auto
from enum import Enum

class _ExtendedEnum(Enum):
    """A custom enum with extended functionality."""

    @classmethod
    def by_name(cls, name: str) -> "Enum":
        """Retrieve enum based on its name."""
        try:
            return cls.__members__[name.upper()]
        except KeyError as exc:
            raise ValueError("Unknown value for type {}, available: {}", cls, list(cls.__members__.values()),) from exc


# Supported ML Classifiers
class MLModel(_ExtendedEnum):
    FASTTEXT = 0
    DEFAULT = FASTTEXT

# Supported changelog formats
class Format(_ExtendedEnum):
    CLUSTER_SIMILAR = 0
    DEFAULT = CLUSTER_SIMILAR
