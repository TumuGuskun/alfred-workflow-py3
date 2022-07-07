# encoding: utf-8
#
# Copyright (c) 2016 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2016-06-25
#

"""An Alfred 3+ version of :class:`~workflow.Workflow`.

:class:`~workflow.Workflow` supports new features, such as
setting :ref:`workflow-variables` and
:class:`the more advanced modifiers <Modifier>` supported by Alfred 3+.

In order for the feedback mechanism to work correctly, it's important
to create :class:`Item3` and :class:`Modifier` objects via the
:meth:`Workflow3.add_item()` and :meth:`Item3.add_modifier()` methods
respectively. If you instantiate :class:`Item3` or :class:`Modifier`
objects directly, the current :class:`Workflow3` object won't be aware
of them, and they won't be sent to Alfred when you call
:meth:`Workflow3.send_feedback()`.

"""


from dataclasses import dataclass
import json
import os
import sys
from typing import Any


@dataclass
class Workflow:
    """Workflow class that generates Alfred 3+ feedback.

    Attributes:
        item_class (class): Class used to generate feedback items.
        variables (dict): Top level workflow variables.

    """

    def __init__(self, **kwargs):
        """Create a new :class:`Workflow3` object.

        See :class:`~workflow.Workflow` for documentation.

        """
        self.variables = {}
        self._rerun = 0
        self._bundleid: str
        # Get session ID from environment if present
        self._session_id = os.getenv("_WF_SESSION_ID") or None
        if self._session_id:
            self.setvar("_WF_SESSION_ID", self._session_id)

    @property
    def alfred_env(self):
        """Dict of Alfred's environmental variables minus ``alfred_`` prefix.

        ============================  =========================================
        Variable                      Description
        ============================  =========================================
        debug                         Set to ``1`` if Alfred's debugger is
                                      open, otherwise unset.
        preferences                   Path to Alfred.alfredpreferences
                                      (where your workflows and settings are
                                      stored).
        preferences_localhash         Machine-specific preferences are stored
                                      in ``Alfred.alfredpreferences/preferences/local/<hash>``
                                      (see ``preferences`` above for
                                      the path to ``Alfred.alfredpreferences``)
        theme                         ID of selected theme
        theme_background              Background colour of selected theme in
                                      format ``rgba(r,g,b,a)``
        theme_subtext                 Show result subtext.
                                      ``0`` = Always,
                                      ``1`` = Alternative actions only,
                                      ``2`` = Selected result only,
                                      ``3`` = Never
        version                       Alfred version number, e.g. ``'2.4'``
        version_build                 Alfred build number, e.g. ``277``
        workflow_bundleid             Bundle ID, e.g.
                                      ``net.deanishe.alfred-mailto``
        workflow_cache                Path to workflow's cache directory
        workflow_data                 Path to workflow's data directory
        workflow_name                 Name of current workflow
        workflow_uid                  UID of workflow
        workflow_version              The version number specified in the
                                      workflow configuration sheet/info.plist
        ============================  =========================================

        **Note:** all values are str strings except ``version_build`` and
        ``theme_subtext``, which are integers.

        :returns: ``dict`` of Alfred's environmental variables without the
            ``alfred_`` prefix, e.g. ``preferences``, ``workflow_data``.

        """
        if self._alfred_env is not None:
            return self._alfred_env

        data = {}

        for key in (
                'debug',
                'preferences',
                'preferences_localhash',
                'theme',
                'theme_background',
                'theme_subtext',
                'version',
                'version_build',
                'workflow_bundleid',
                'workflow_cache',
                'workflow_data',
                'workflow_name',
                'workflow_uid',
                'workflow_version'):

            value = os.getenv('alfred_' + key, '')

            if value:
                if key in ('debug', 'version_build', 'theme_subtext'):
                    value = int(value)
                else:
                    value = self.decode(value)

            data[key] = value

        self._alfred_env = data

        return self._alfred_env

    @property
    def bundleid(self) -> str:
        """Workflow bundle ID from environmental vars or ``info.plist``.

        :returns: bundle ID
        :rtype: ``str``

        """
        if not self._bundleid:
            if self.alfred_env.get('workflow_bundleid'):
                self._bundleid = self.alfred_env.get('workflow_bundleid')
            else:
                self._bundleid = self.info['bundleid']

        return self._bundleid

    @property
    def _default_cachedir(self) -> str:
        """Alfred 4's default cache directory."""
        return os.path.join(
            os.path.expanduser(
                "~/Library/Caches/com.runningwithcrayons.Alfred/" "Workflow Data/"
            ),
            self.bundleid,
        )

    @property
    def _default_datadir(self) -> str:
        """Alfred 4's default data directory."""
        return os.path.join(
            os.path.expanduser(
                "~/Library/Application Support/Alfred/Workflow Data/"),
            self.bundleid,
        )

    @property
    def rerun(self) -> int:
        """How often (in seconds) Alfred should re-run the Script Filter."""
        return self._rerun

    @rerun.setter
    def rerun(self, seconds: int) -> None:
        """Interval at which Alfred should re-run the Script Filter.

        Args:
            seconds (int): Interval between runs.
        """
        self._rerun = seconds

    @property
    def session_id(self):
        """A unique session ID every time the user uses the workflow.

        .. versionadded:: 1.25

        The session ID persists while the user is using this workflow.
        It expires when the user runs a different workflow or closes
        Alfred.

        """
        if not self._session_id:
            from uuid import uuid4

            self._session_id = uuid4().hex
            self.setvar("_WF_SESSION_ID", self._session_id)

        return self._session_id

    def setvar(self, name, value, persist=False):
        """Set a "global" workflow variable.

        .. versionchanged:: 1.33

        These variables are always passed to downstream workflow objects.

        If you have set :attr:`rerun`, these variables are also passed
        back to the script when Alfred runs it again.

        Args:
            name (str): Name of variable.
            value (str): Value of variable.
            persist (bool, optional): Also save variable to ``info.plist``?

        """
        self.variables[name] = value
        if persist:
            from .util import set_config

            set_config(name, value, self.bundleid)
            self.logger.debug(
                "saved variable %r with value %r to info.plist", name, value
            )

    def getvar(self, name, default=None):
        """Return value of workflow variable for ``name`` or ``default``.

        Args:
            name (str): Variable name.
            default (None, optional): Value to return if variable is unset.

        Returns:
            str or ``default``: Value of variable if set or ``default``.

        """
        return self.variables.get(name, default)

    def add_item(
        self,
        title,
        subtitle="",
        arg=None,
        autocomplete=None,
        valid=False,
        uid=None,
        icon=None,
        icontype=None,
        type=None,
        largetext=None,
        copytext=None,
        quicklookurl=None,
        match=None,
    ):
        """Add an item to be output to Alfred.

        Args:
            match (str, optional): If you have "Alfred filters results"
                turned on for your Script Filter, Alfred (version 3.5 and
                above) will filter against this field, not ``title``.

        In Alfred 4.1+ and Alfred-Workflow 1.40+, ``arg`` may also be a
        :class:`list` or :class:`tuple`.

        See :meth:`Workflow.add_item() <workflow.Workflow.add_item>` for
        the main documentation and other parameters.

        The key difference is that this method does not support the
        ``modifier_subtitles`` argument. Use the :meth:`~Item3.add_modifier()`
        method instead on the returned item instead.

        Returns:
            Item3: Alfred feedback item.

        """
        item = self.item_class(
            title,
            subtitle,
            arg,
            autocomplete,
            match,
            valid,
            uid,
            icon,
            icontype,
            type,
            largetext,
            copytext,
            quicklookurl,
        )

        # Add variables to child item
        item.variables.update(self.variables)

        self._items.append(item)
        return item

    @property
    def _session_prefix(self):
        """Filename prefix for current session."""
        return "_wfsess-{0}-".format(self.session_id)

    def _mk_session_name(self, name):
        """New cache name/key based on session ID."""
        return self._session_prefix + name

    def cache_data(self, name, data, session=False):
        """Cache API with session-scoped expiry.

        .. versionadded:: 1.25

        Args:
            name (str): Cache key
            data (object): Data to cache
            session (bool, optional): Whether to scope the cache
                to the current session.

        ``name`` and ``data`` are the same as for the
        :meth:`~workflow.Workflow.cache_data` method on
        :class:`~workflow.Workflow`.

        If ``session`` is ``True``, then ``name`` is prefixed
        with :attr:`session_id`.

        """
        if session:
            name = self._mk_session_name(name)

        return super(Workflow3, self).cache_data(name, data)

    def cached_data(self, name, data_func=None, max_age=60, session=False):
        """Cache API with session-scoped expiry.

        .. versionadded:: 1.25

        Args:
            name (str): Cache key
            data_func (callable): Callable that returns fresh data. It
                is called if the cache has expired or doesn't exist.
            max_age (int): Maximum allowable age of cache in seconds.
            session (bool, optional): Whether to scope the cache
                to the current session.

        ``name``, ``data_func`` and ``max_age`` are the same as for the
        :meth:`~workflow.Workflow.cached_data` method on
        :class:`~workflow.Workflow`.

        If ``session`` is ``True``, then ``name`` is prefixed
        with :attr:`session_id`.

        """
        if session:
            name = self._mk_session_name(name)

        return super(Workflow3, self).cached_data(name, data_func, max_age)

    def clear_session_cache(self, current=False):
        """Remove session data from the cache.

        .. versionadded:: 1.25
        .. versionchanged:: 1.27

        By default, data belonging to the current session won't be
        deleted. Set ``current=True`` to also clear current session.

        Args:
            current (bool, optional): If ``True``, also remove data for
                current session.

        """

        def _is_session_file(filename):
            if current:
                return filename.startswith("_wfsess-")
            return filename.startswith("_wfsess-") and not filename.startswith(
                self._session_prefix
            )

        self.clear_cache(_is_session_file)

    @property
    def obj(self) -> dict[str, Any]:
        """Feedback formatted for JSON serialization.

        Returns:
            dict: Data suitable for Alfred 3 feedback.

        """
        items = []
        for item in self._items:
            items.append(item.obj)

        output = {"items": items}
        if self.variables:
            output["variables"] = self.variables
        if self.rerun:
            output["rerun"] = self.rerun
        return output

    def warn_empty(self, title, subtitle="", icon=None):
        """Add a warning to feedback if there are no items.

        Add a "warning" item to Alfred feedback if no other items
        have been added. This is a handy shortcut to prevent Alfred
        from showing its fallback searches, which is does if no
        items are returned.

        Args:
            title (str): Title of feedback item.
            subtitle (str, optional): Subtitle of feedback item.
            icon (str, optional): Icon for feedback item. If not
                specified, ``ICON_WARNING`` is used.

        Returns:
            Item3: Newly-created item.

        """
        if len(self._items):
            return

        icon = icon or ICON_WARNING
        return self.add_item(title, subtitle, icon=icon)

    def send_feedback(self):
        """Print stored items to console/Alfred as JSON."""
        if self.debugging:
            json.dump(self.obj, sys.stdout, indent=2, separators=(",", ": "))
        else:
            json.dump(self.obj, sys.stdout)
        sys.stdout.flush()
