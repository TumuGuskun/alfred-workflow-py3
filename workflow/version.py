from itertools import zip_longest
import os
import re
import tempfile
from urllib import request

from workflow.util import atomic_writer


class Version(object):
    """Mostly semantic versioning.

    The main difference to proper :ref:`semantic versioning <semver>`
    is that this implementation doesn't require a minor or patch version.

    Version strings may also be prefixed with "v", e.g.:

    >>> v = Version('v1.1.1')
    >>> v.tuple
    (1, 1, 1, '')

    >>> v = Version('2.0')
    >>> v.tuple
    (2, 0, 0, '')

    >>> Version('3.1-beta').tuple
    (3, 1, 0, 'beta')

    >>> Version('1.0.1') > Version('0.0.1')
    True
    """

    #: Match version and pre-release/build information in version strings
    match_version = re.compile(r"([0-9][0-9\.]*)(.+)?").match

    def __init__(self, vstr):
        """Create new `Version` object.

        Args:
            vstr (basestring): Semantic version string.
        """
        if not vstr:
            raise ValueError("invalid version number: {!r}".format(vstr))

        self.vstr = vstr
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.suffix = ""
        self.build = ""
        self._parse(vstr)

    def _parse(self, vstr):
        vstr = str(vstr)
        if vstr.startswith("v"):
            m = self.match_version(vstr[1:])
        else:
            m = self.match_version(vstr)
        if not m:
            raise ValueError("invalid version number: " + vstr)

        version, suffix = m.groups()
        parts = self._parse_dotted_string(version)
        self.major = parts.pop(0)
        if len(parts):
            self.minor = parts.pop(0)
        if len(parts):
            self.patch = parts.pop(0)
        if not len(parts) == 0:
            raise ValueError("version number too long: " + vstr)

        if suffix:
            # Build info
            idx = suffix.find("+")
            if idx > -1:
                self.build = suffix[idx + 1:]
                suffix = suffix[:idx]
            if suffix:
                if not suffix.startswith("-"):
                    raise ValueError("suffix must start with - : " + suffix)
                self.suffix = suffix[1:]

    def _parse_dotted_string(self, s):
        """Parse string ``s`` into list of ints and strings."""
        parsed = []
        parts = s.split(".")
        for p in parts:
            if p.isdigit():
                p = int(p)
            parsed.append(p)
        return parsed

    @property
    def tuple(self):
        """Version number as a tuple of major, minor, patch, pre-release."""
        return (self.major, self.minor, self.patch, self.suffix)

    def __lt__(self, other):
        """Implement comparison."""
        if not isinstance(other, Version):
            raise ValueError("not a Version instance: {0!r}".format(other))
        t = self.tuple[:3]
        o = other.tuple[:3]
        if t < o:
            return True
        if t == o:  # We need to compare suffixes
            if self.suffix and not other.suffix:
                return True
            if other.suffix and not self.suffix:
                return False

            self_suffix = self._parse_dotted_string(self.suffix)
            other_suffix = self._parse_dotted_string(other.suffix)

            for s, o in zip_longest(self_suffix, other_suffix):
                if s is None:  # shorter value wins
                    return True
                elif o is None:  # longer value loses
                    return False
                elif type(s) != type(o):  # type coersion
                    s, o = str(s), str(o)
                if s == o:  # next if the same compare
                    continue
                return s < o  # finally compare
        # t > o
        return False

    def __eq__(self, other):
        """Implement comparison."""
        if not isinstance(other, Version):
            raise ValueError("not a Version instance: {0!r}".format(other))
        return self.tuple == other.tuple

    def __ne__(self, other):
        """Implement comparison."""
        return not self.__eq__(other)

    def __gt__(self, other):
        """Implement comparison."""
        if not isinstance(other, Version):
            raise ValueError("not a Version instance: {0!r}".format(other))
        return other.__lt__(self)

    def __le__(self, other):
        """Implement comparison."""
        if not isinstance(other, Version):
            raise ValueError("not a Version instance: {0!r}".format(other))
        return not other.__lt__(self)

    def __ge__(self, other):
        """Implement comparison."""
        return not self.__lt__(other)

    def __str__(self):
        """Return semantic version string."""
        vstr = "{0}.{1}.{2}".format(self.major, self.minor, self.patch)
        if self.suffix:
            vstr = "{0}-{1}".format(vstr, self.suffix)
        if self.build:
            vstr = "{0}+{1}".format(vstr, self.build)
        return vstr

    def __repr__(self):
        """Return 'code' representation of `Version`."""
        return "Version('{0}')".format(str(self))


def retrieve_download(dl):
    """Saves a download to a temporary file and returns path.

    .. versionadded: 1.37

    Args:
        url (str): URL to .alfredworkflow file in GitHub repo

    Returns:
        str: path to downloaded file

    """
    if not match_workflow(dl.filename):
        raise ValueError("attachment not a workflow: " + dl.filename)

    path = os.path.join(tempfile.gettempdir(), dl.filename)
    wf().logger.debug("downloading update from " "%r to %r ...", dl.url, path)

    r = request.urlopen(dl.url)

    with atomic_writer(path, "wb") as file_obj:
        file_obj.write(r.read())

    return path


def build_api_url(repo):
    """Generate releases URL from GitHub repo.

    Args:
        repo (str): Repo name in form ``username/repo``

    Returns:
        str: URL to the API endpoint for the repo's releases

    """
    if len(repo.split("/")) != 2:
        raise ValueError("invalid GitHub repo: {!r}".format(repo))

    return RELEASES_BASE.format(repo)


def get_downloads(repo):
    """Load available ``Download``s for GitHub repo.

    .. versionadded: 1.37

    Args:
        repo (str): GitHub repo to load releases for.

    Returns:
        list: Sequence of `Download` contained in GitHub releases.
    """
    url = build_api_url(repo)

    def _fetch():
        wf().logger.info("retrieving releases for %r ...", repo)
        r = request.urlopen(url)
        return r.read()

    key = "github-releases-" + repo.replace("/", "-")
    js = wf().cached_data(key, _fetch, max_age=60)

    return Download.from_releases(js)


def latest_download(dls, alfred_version=None, prereleases=False):
    """Return newest `Download`."""
    alfred_version = alfred_version or os.getenv("alfred_version")
    version = None
    if alfred_version:
        version = Version(alfred_version)

    dls.sort(reverse=True)
    for dl in dls:
        if dl.prerelease and not prereleases:
            wf().logger.debug("ignored prerelease: %s", dl.version)
            continue
        if version and dl.alfred_version > version:
            wf().logger.debug(
                "ignored incompatible (%s > %s): %s",
                dl.alfred_version,
                version,
                dl.filename,
            )
            continue

        wf().logger.debug("latest version: %s (%s)", dl.version, dl.filename)
        return dl

    return None


def check_update(repo, current_version, prereleases=False, alfred_version=None):
    """Check whether a newer release is available on GitHub.

    Args:
        repo (str): ``username/repo`` for workflow's GitHub repo
        current_version (str): the currently installed version of the
            workflow. :ref:`Semantic versioning <semver>` is required.
        prereleases (bool): Whether to include pre-releases.
        alfred_version (str): version of currently-running Alfred.
            if empty, defaults to ``$alfred_version`` environment variable.

    Returns:
        bool: ``True`` if an update is available, else ``False``

    If an update is available, its version number and download URL will
    be cached.

    """
    key = "__workflow_latest_version"
    # data stored when no update is available
    no_update = {"available": False, "download": None, "version": None}
    current = Version(current_version)

    dls = get_downloads(repo)
    if not len(dls):
        wf().logger.warning("no valid downloads for %s", repo)
        wf().cache_data(key, no_update)
        return False

    wf().logger.info("%d download(s) for %s", len(dls), repo)

    dl = latest_download(dls, alfred_version, prereleases)

    if not dl:
        wf().logger.warning("no compatible downloads for %s", repo)
        wf().cache_data(key, no_update)
        return False

    wf().logger.debug("latest=%r, installed=%r", dl.version, current)

    if dl.version > current:
        wf().cache_data(
            key, {"version": str(dl.version),
                  "download": dl.dict, "available": True}
        )
        return True

    wf().cache_data(key, no_update)
    return False


def install_update():
    """If a newer release is available, download and install it.

    :returns: ``True`` if an update is installed, else ``False``

    """
    key = "__workflow_latest_version"
    # data stored when no update is available
    no_update = {"available": False, "download": None, "version": None}
    status = wf().cached_data(key, max_age=0)

    if not status or not status.get("available"):
        wf().logger.info("no update available")
        return False

    dl = status.get("download")
    if not dl:
        wf().logger.info("no download information")
        return False

    path = retrieve_download(Download.from_dict(dl))

    wf().logger.info("installing updated workflow ...")
    subprocess.call(["open", path])  # nosec

    wf().cache_data(key, no_update)
    return True


if __name__ == "__main__":  # pragma: nocover
    import sys

    prereleases = False

    def show_help(status=0):
        """Print help message."""
        print(
            "usage: update.py (check|install) " "[--prereleases] <repo> <version>")
        sys.exit(status)

    argv = sys.argv[:]
    if "-h" in argv or "--help" in argv:
        show_help()

    if "--prereleases" in argv:
        argv.remove("--prereleases")
        prereleases = True

    if len(argv) != 4:
        show_help(1)

    action = argv[1]
    repo = argv[2]
    version = argv[3]

    try:

        if action == "check":
            check_update(repo, version, prereleases)
        elif action == "install":
            install_update()
        else:
            show_help(1)

    except Exception as err:  # ensure traceback is in log file
        wf().logger.exception(err)
        raise err
