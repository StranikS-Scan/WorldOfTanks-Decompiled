# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/limited_ui/constants.py
from enum import Enum
FEATURE = 'limited_ui'

class LimitedUILogItem(Enum):
    DISABLE_LIMITED_UI_BUTTON = 'disable_limited_ui_button'


class LimitedUILogScreenParent(Enum):
    SETTINGS_WINDOW = 'settings_window'


class LimitedUILogActions(Enum):
    CLICK = 'click'
