####################################################################
# Standard system icons
####################################################################

# These icons are default macOS icons. They are super-high quality, and
# will be familiar to users.
# This library uses `ICON_ERROR` when a workflow dies in flames, so
# in my own workflows, I use `ICON_WARNING` for less fatal errors
# (e.g. bad user input, no results etc.)

# The system icons are all in this directory. There are many more than
# are listed here

import os


ICON_ROOT = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources'

ICON_ACCOUNT = os.path.join(ICON_ROOT, 'Accounts.icns')
ICON_BURN = os.path.join(ICON_ROOT, 'BurningIcon.icns')
ICON_CLOCK = os.path.join(ICON_ROOT, 'Clock.icns')
ICON_COLOR = os.path.join(ICON_ROOT, 'ProfileBackgroundColor.icns')
ICON_EJECT = os.path.join(ICON_ROOT, 'EjectMediaIcon.icns')
# Shown when a workflow throws an error
ICON_ERROR = os.path.join(ICON_ROOT, 'AlertStopIcon.icns')
ICON_FAVORITE = os.path.join(ICON_ROOT, 'ToolbarFavoritesIcon.icns')
ICON_GROUP = os.path.join(ICON_ROOT, 'GroupIcon.icns')
ICON_HELP = os.path.join(ICON_ROOT, 'HelpIcon.icns')
ICON_HOME = os.path.join(ICON_ROOT, 'HomeFolderIcon.icns')
ICON_INFO = os.path.join(ICON_ROOT, 'ToolbarInfo.icns')
ICON_NETWORK = os.path.join(ICON_ROOT, 'GenericNetworkIcon.icns')
ICON_NOTE = os.path.join(ICON_ROOT, 'AlertNoteIcon.icns')
ICON_SETTINGS = os.path.join(ICON_ROOT, 'ToolbarAdvanced.icns')
ICON_SWIRL = os.path.join(ICON_ROOT, 'ErasingIcon.icns')
ICON_SWITCH = os.path.join(ICON_ROOT, 'General.icns')
ICON_SYNC = os.path.join(ICON_ROOT, 'Sync.icns')
ICON_TRASH = os.path.join(ICON_ROOT, 'TrashIcon.icns')
ICON_USER = os.path.join(ICON_ROOT, 'UserIcon.icns')
ICON_WARNING = os.path.join(ICON_ROOT, 'AlertCautionIcon.icns')
ICON_WEB = os.path.join(ICON_ROOT, 'BookmarkIcon.icns')
