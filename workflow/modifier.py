from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class IconType(Enum):
    # when the icon is a filetype such as 'public.folder'
    FILETYPE = auto()
    # when you want to use the icon of a file
    FILEICON = auto()
    # if it points to an actual icon file
    FILEPATH = auto()


@dataclass
class Modifier:
    """Modify an Item arg/icon/variables when modifier key is pressed.

    Don't use this class directly (as it won't be associated with any
    Item) but rather use Item.add_modifier()
    to add modifiers to results.

    >>> it = wf.add_item('Title', 'Subtitle', valid=True)
    >>> it.setvar('name', 'default')
    >>> m = it.add_modifier('cmd')
    >>> m.setvar('name', 'alternate')

    Args:
        key (str): Modifier key, e.g. ``"cmd"``, ``"alt"`` etc.
        subtitle (str, optional): Override default subtitle.
        arg (str, optional): Argument to pass for this modifier.
        valid (bool, optional): Override item's validity.
        icon (str, optional): Filepath/UTI of icon to use
        icontype (str, optional): Type of icon. See
            :meth:`Workflow.add_item() <workflow.Workflow.add_item>`
            for valid values.

    Attributes:
        arg (str): Arg to pass to following action.
        config (dict): Configuration for a downstream element, such as
            a File Filter.
        icon (str): Filepath/UTI of icon.
        icontype (str): Type of icon. See
            :meth:`Workflow.add_item() <workflow.Workflow.add_item>`
            for valid values.
        key (str): Modifier key (see above).
        subtitle (str): Override item subtitle.
        valid (bool): Override item validity.
        variables (dict): Workflow variables set by this modifier.

    """

    key: str
    subtitle: Optional[str] = None
    arg: Optional[str] = None
    valid: bool = True
    icon: Optional[str] = None
    icontype: IconType = IconType.FILEPATH

    config: dict[str, str] = field(default_factory=lambda: {})
    variables: dict[str, Optional[str]] = field(default_factory=lambda: {})

    def setvar(self, name: str, value: str) -> None:
        """Set a workflow variable for this Item.

        Args:
            name (str): Name of variable.
            value (str): Value of variable.

        """
        self.variables[name] = value

    def getvar(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Return value of workflow variable for name

        Args:
            name (str): Variable name.
            default (None, optional): Value to return if variable is unset.

        Returns:
            str or default: Value of variable if set or default.

        """
        return self.variables.get(name, default)

    @property
    def obj(self) -> dict[str, str]:
        """Modifier formatted for JSON serialization for Alfred 3.

        Returns:
            dict: Modifier for serializing to JSON.

        """
        output = {}

        if self.subtitle is not None:
            output["subtitle"] = self.subtitle

        if self.arg is not None:
            output["arg"] = self.arg

        if self.valid is not None:
            output["valid"] = self.valid

        if self.variables:
            output["variables"] = self.variables

        if self.config:
            output["config"] = self.config

        icon = self._icon()
        if icon:
            output["icon"] = icon

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
