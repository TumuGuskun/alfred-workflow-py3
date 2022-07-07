from copy import deepcopy
import json
import os
from typing import Optional
from workflow.util import LockFile, atomic_writer, uninterruptible


class Settings(dict):
    """A dictionary that saves itself when changed.

    Dictionary keys & values will be saved as a JSON file
    at ``filepath``. If the file does not exist, the dictionary
    (and settings file) will be initialised with ``defaults``.

    :param filepath: where to save the settings
    :type filepath: :class:`str`
    :param defaults: dict of default settings
    :type defaults: :class:`dict`


    An appropriate instance is provided by :class:`Workflow` instances at
    :attr:`Workflow.settings`.

    """

    def __init__(self, filepath: str, defaults: dict[str, str] = lambda: {}) -> None:
        """Create new :class:`Settings` object."""
        super(Settings, self).__init__()
        self._filepath = filepath
        self._nosave = False
        self._original = {}
        if os.path.exists(self._filepath):
            self._load()
        elif defaults:
            for key, val in defaults.items():
                self[key] = val
            self.save()  # save default settings

    def _load(self) -> None:
        """Load cached settings from JSON file `self._filepath`."""
        data = {}
        with LockFile(self._filepath, 0.5):
            with open(self._filepath, 'rb') as fp:
                data.update(json.load(fp))

        self._original = deepcopy(data)

        self._nosave = True
        self.update(data)
        self._nosave = False

    @uninterruptible
    def save(self) -> None:
        """Save settings to JSON file specified in ``self._filepath``.

        If you're using this class via :attr:`Workflow.settings`, which
        you probably are, ``self._filepath`` will be ``settings.json``
        in your workflow's data directory (see :attr:`~Workflow.datadir`).
        """
        if self._nosave:
            return

        data = {}
        data.update(self)

        with LockFile(self._filepath, 0.5):
            with atomic_writer(self._filepath, 'wb') as fp:
                json.dump(data, fp, sort_keys=True, indent=2,
                          encoding='utf-8')

    # dict methods
    def __setitem__(self, key: str, value: str) -> None:
        """Implement :class:`dict` interface."""
        if self._original.get(key) != value:
            super(Settings, self).__setitem__(key, value)
            self.save()

    def __delitem__(self, key: str) -> None:
        """Implement :class:`dict` interface."""
        super(Settings, self).__delitem__(key)
        self.save()

    def update(self, *args, **kwargs) -> None:
        """Override :class:`dict` method to save on update."""
        super(Settings, self).update(*args, **kwargs)
        self.save()

    def setdefault(self, key: str, value: Optional[str] = None) -> Optional[str]:
        """Override :class:`dict` method to save on update."""
        ret = super(Settings, self).setdefault(key, value)
        self.save()
        return ret
