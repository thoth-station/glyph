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

"""Module containing all supported formatting options for the changelog file."""

from typing import Dict
from typing import List
from typing import Optional


class ClusterSimilar:
    """Cluster similar messages into a common groups."""

    @staticmethod
    def generate_log(message_dict: Dict[str, Optional[List[str]]]) -> List[str]:
        """Generate log out of messages stored in a dict."""
        changelog = []
        for key in message_dict:
            if message_dict[key] is not None and len(message_dict[key]) > 0:
                changelog.append("### " + key)
                for message in message_dict[key]:
                    changelog.append("* " + message)
        return changelog
