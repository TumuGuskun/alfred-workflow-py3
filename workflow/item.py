from dataclasses import dataclass, field
from typing import Optional

from workflow.modifier import IconType, Modifier


@dataclass
class Item:
    """Represents a feedback item for Alfred 3+.

    Generates Alfred-compliant JSON for a single item.

    Don't use this class directly (as it then won't be associated with
    any :class:`Workflow3 <workflow.Workflow3>` object), but rather use
    :meth:`Workflow3.add_item() <workflow.Workflow3.add_item>`.
    See :meth:`~workflow.Workflow3.add_item` for details of arguments.

    """
    title: str
    subtitle: str = ''
    arg: Optional[str] = None
    autocomplete: Optional[str] = None
    match: Optional[str] = None
    valid: bool = False
    uid: Optional[str] = None
    icon: Optional[str] = None
    icontype: Optional[str] = None
    item_type: Optional[str] = None
    largetext: Optional[str] = None
    copytext: Optional[str] = None
    quicklookurl: Optional[str] = None

    modifiers: dict = field(default_factory=lambda: {})
    config: dict = field(default_factory=lambda: {})
    variables: dict[str, Optional[str]] = field(default_factory=lambda: {})

    def setvar(self, name: str, value: str) -> None:
        """Set a workflow variable for this Item.

        Args:
            name (str): Name of variable.
            value (str): Value of variable.

        """
        self.variables[name] = value

    def getvar(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Return value of workflow variable for ``name`` or ``default``.

        Args:
            name (str): Variable name.
            default (None, optional): Value to return if variable is unset.

        Returns:
            str or ``default``: Value of variable if set or ``default``.

        """
        return self.variables.get(name, default)

    def add_modifier(
        self, key: str, subtitle: Optional[str] = None, arg: Optional[str] = None, valid: bool = True, icon: Optional[str] = None, icontype: IconType = IconType.FILEPATH
    ) -> Modifier:
        """Add alternative values for a modifier key.

        Args:
            key (str): Modifier key, e.g. ``"cmd"`` or ``"alt"``
            subtitle (str, optional): Override item subtitle.
            arg (str, optional): Input for following action.
            valid (bool, optional): Override item validity.
            icon (str, optional): Filepath/UTI of icon.
            icontype (IconType, optional): Type of icon.  See


        Returns:
            Modifier: Configured :class:`Modifier`.

        """
        mod = Modifier(key, subtitle, arg, valid, icon, icontype)

        # Add Item variables to Modifier
        mod.variables.update(self.variables)

        self.modifiers[key] = mod

        return mod

    @property
    def obj(self) -> dict[str, str]:
        """Item formatted for JSON serialization.

        Returns:
            dict: Data suitable for Alfred 3 feedback.

        """
        # Required values
        output = {"title": self.title,
                  "subtitle": self.subtitle, "valid": self.valid}

        # Optional values
        if self.arg is not None:
            output["arg"] = self.arg

        if self.autocomplete is not None:
            output["autocomplete"] = self.autocomplete

        if self.match is not None:
            output["match"] = self.match

        if self.uid is not None:
            output["uid"] = self.uid

        if self.item_type is not None:
            output["type"] = self.item_type

        if self.quicklookurl is not None:
            output["quicklookurl"] = self.quicklookurl

        if self.variables:
            output["variables"] = self.variables

        if self.config:
            output["config"] = self.config

        # Largetype and copytext
        text = self._text()
        if text:
            output["text"] = text

        icon = self._icon()
        if icon:
            output["icon"] = icon

        # Modifiers
        mods = self._modifiers()
        if mods:
            output["mods"] = mods

        return output

    def _icon(self) -> dict[str, str]:
        """Return `icon` object for item.

        Returns:
            dict: Mapping for item `icon` (may be empty).

        """
        icon = {}
        if self.icon is not None:
            icon["path"] = self.icon

        if self.icontype is not None:
            icon["type"] = self.icontype

        return icon

    def _text(self) -> dict[str, str]:
        """Return `largetext` and `copytext` object for item.

        Returns:
            dict: `text` mapping (may be empty)

        """
        text = {}
        if self.largetext is not None:
            text["largetype"] = self.largetext

        if self.copytext is not None:
            text["copy"] = self.copytext

        return text

    def _modifiers(self) -> dict[str, str]:
        """Build `mods` dictionary for JSON feedback.

        Returns:
            dict: Modifier mapping or `None`.

        """

        mods = {}
        if self.modifiers:
            for k, mod in list(self.modifiers.items()):
                mods[k] = mod.obj

        return mods
