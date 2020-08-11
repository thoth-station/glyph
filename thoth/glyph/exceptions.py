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

"""Custom Glyph Exceptions."""


class ThothGlyphException(Exception):
    """A base class for implementing thoth-glyph exceptions."""


class RepositoryNotFoundException(ThothGlyphException):
    """An exception raised when Git repository cannot be found."""


class ModelNotFoundException(ThothGlyphException):
    """An exception raised when classification model cannot be found."""


class NoMessageEnteredException(ThothGlyphException):
    """An exception raised when an empty string is requested to be classified.."""
