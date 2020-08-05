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

# Supported changelog formats
DEFAULT_FORMAT = "FORMAT_1"
FORMAT_1 = "FORMAT_1"
FORMAT_2 = "FORMAT_2"
FORMAT_3 = "FORMAT_3"

# Supported ML Classifiers
DEFAULT_MODEL = "fasttext"
FASTTEXT_MODEL = "fasttext"
RANDOM_FOREST_MODEL = "rf"
BERT_MODEL = "bert"
