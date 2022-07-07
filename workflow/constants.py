import re
import string

####################################################################
# Used by `Workflow.filter`
####################################################################

# Anchor characters in a name
#: Characters that indicate the beginning of a "word" in CamelCase

INITIALS = string.ascii_uppercase + string.digits

#: Split on non-letters, numbers
split_on_delimiters = re.compile('[^a-zA-Z0-9]').split

# Match filter flags
#: Match items that start with ``query``
MATCH_STARTSWITH = 1
#: Match items whose capital letters start with ``query``
MATCH_CAPITALS = 2
#: Match items with a component "word" that matches ``query``
MATCH_ATOM = 4
#: Match items whose initials (based on atoms) start with ``query``
MATCH_INITIALS_STARTSWITH = 8
#: Match items whose initials (based on atoms) contain ``query``
MATCH_INITIALS_CONTAIN = 16
#: Combination of :const:`MATCH_INITIALS_STARTSWITH` and
#: :const:`MATCH_INITIALS_CONTAIN`
MATCH_INITIALS = 24
#: Match items if ``query`` is a substring
MATCH_SUBSTRING = 32
#: Match items if all characters in ``query`` appear in the item in order
MATCH_ALLCHARS = 64
#: Combination of all other ``MATCH_*`` constants
MATCH_ALL = 127


####################################################################
# Used by `Workflow.check_update`
####################################################################

# Number of days to wait between checking for updates to the workflow
DEFAULT_UPDATE_FREQUENCY = 1
