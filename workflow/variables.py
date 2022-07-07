class Variables(dict):
    """Workflow variables for Run Script actions.

    This class allows you to set workflow variables from
    Run Script actions.

    >>> v = Variables(username='deanishe', password='hunter2')
    >>> v.arg = u'output value'
    >>> print(v)

    See :ref:`variables-run-script` in the User Guide for more
    information.

    Args:
        arg (str or list, optional): Main output/``{query}``.
        **variables: Workflow variables to set.

    In Alfred 4.1+ and Alfred-Workflow 1.40+, ``arg`` may also be a
    :class:`list` or :class:`tuple`.

    Attributes:
        arg (str or list): Output value (``{query}``).
            In Alfred 4.1+ and Alfred-Workflow 1.40+, ``arg`` may also be a
            :class:`list` or :class:`tuple`.
        config (dict): Configuration for downstream workflow element.

    """

    def __init__(self, arg=None, **variables):
        """Create a new `Variables` object."""
        self.arg = arg
        self.config = {}
        super(Variables, self).__init__(**variables)

    @property
    def obj(self):
        """``alfredworkflow`` :class:`dict`."""
        output = {}
        if self:
            d2 = {}
            for k, v in list(self.items()):
                d2[k] = v
            output["variables"] = d2

        if self.config:
            output["config"] = self.config

        if self.arg is not None:
            output["arg"] = self.arg

        return {"alfredworkflow": output}

    def __str__(self):
        """Convert to ``alfredworkflow`` JSON object.

        Returns:
            str: ``alfredworkflow`` JSON object

        """
        if not self and not self.config:
            if not self.arg:
                return ""
            if isinstance(self.arg, str):
                return self.arg

        return json.dumps(self.obj)
