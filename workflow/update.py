#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2014 Fabio Niephaus <fabio.niephaus@gmail.com>,
#       Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-08-16
#

"""Self-updating from GitHub.

.. versionadded:: 1.9

.. note::

   This module is not intended to be used directly. Automatic updates
   are controlled by the ``update_settings`` :class:`dict` passed to
   :class:`~workflow.workflow.Workflow` objects.

"""


import json
import os
from collections import defaultdict
from functools import total_ordering

from util import match_workflow
from workflow.workflow import Workflow
from workflow.version import Version


RELEASES_BASE = "https://api.github.com/repos/{}/releases"

_wf = None


def wf() -> Workflow:
    """Lazy `Workflow` object."""
    global _wf
    if _wf is None:
        _wf = Workflow()
    return _wf


@total_ordering
class Download:
    """A workflow file that is available for download.


    Attributes:
        url (str): URL of workflow file.
        filename (str): Filename of workflow file.
        version (Version): Semantic version of workflow.
        prerelease (bool): Whether version is a pre-release.
        alfred_version (Version): Minimum compatible version
            of Alfred.

    """

    @classmethod
    def from_dict(cls, d):
        """Create a `Download` from a `dict`."""
        return cls(
            url=d["url"],
            filename=d["filename"],
            version=Version(d["version"]),
            prerelease=d["prerelease"],
        )

    @classmethod
    def from_releases(cls, js):
        """Extract downloads from GitHub releases.

        Searches releases with semantic tags for assets with
        file extension .alfredworkflow or .alfredXworkflow where
        X is a number.

        Files are returned sorted by latest version first. Any
        releases containing multiple files with the same (workflow)
        extension are rejected as ambiguous.

        Args:
            js (str): JSON response from GitHub's releases endpoint.

        Returns:
            list: Sequence of `Download`.
        """
        releases = json.loads(js)
        downloads = []
        for release in releases:
            tag = release["tag_name"]
            dupes = defaultdict(int)
            try:
                version = Version(tag)
            except ValueError as err:
                wf().logger.debug('ignored release: bad version "%s": %s', tag, err)
                continue

            dls = []
            for asset in release.get("assets", []):
                url = asset.get("browser_download_url")
                filename = os.path.basename(url)
                m = match_workflow(filename)
                if not m:
                    wf().logger.debug("unwanted file: %s", filename)
                    continue

                ext = m.group(0)
                dupes[ext] = dupes[ext] + 1
                dls.append(
                    Download(url, filename, version, release["prerelease"]))

            valid = True
            for ext, n in list(dupes.items()):
                if n > 1:
                    wf().logger.debug(
                        'ignored release "%s": multiple assets ' 'with extension "%s"',
                        tag,
                        ext,
                    )
                    valid = False
                    break

            if valid:
                downloads.extend(dls)

        downloads.sort(reverse=True)
        return downloads

    def __init__(self, url, filename, version, prerelease=False):
        """Create a new Download.

        Args:
            url (str): URL of workflow file.
            filename (str): Filename of workflow file.
            version (Version): Version of workflow.
            prerelease (bool, optional): Whether version is
                pre-release. Defaults to False.

        """
        if isinstance(version, str):
            version = Version(version)

        self.url = url
        self.filename = filename
        self.version = version
        self.prerelease = prerelease

    @property
    def alfred_version(self):
        """Minimum Alfred version based on filename extension."""
        m = match_workflow(self.filename)
        if not m or not m.group(1):
            return Version("0")
        return Version(m.group(1))

    @property
    def dict(self):
        """Convert `Download` to `dict`."""
        return dict(
            url=self.url,
            filename=self.filename,
            version=str(self.version),
            prerelease=self.prerelease,
        )

    def __str__(self):
        """Format `Download` for printing."""
        return (
            "Download("
            "url={dl.url!r}, "
            "filename={dl.filename!r}, "
            "version={dl.version!r}, "
            "prerelease={dl.prerelease!r}"
            ")"
        ).format(dl=self)

    def __repr__(self):
        """Code-like representation of `Download`."""
        return str(self)

    def __eq__(self, other):
        """Compare Downloads based on version numbers."""
        if (
            self.url != other.url
            or self.filename != other.filename
            or self.version != other.version
            or self.prerelease != other.prerelease
        ):
            return False
        return True

    def __ne__(self, other):
        """Compare Downloads based on version numbers."""
        return not self.__eq__(other)

    def __lt__(self, other):
        """Compare Downloads based on version numbers."""
        if self.version != other.version:
            return self.version < other.version
        return self.alfred_version < other.alfred_version
