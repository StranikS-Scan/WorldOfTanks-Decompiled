# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/settings/constants.py
from enum import Enum
FEATURE = 'settings'
GROUP = 'settings'

class SettingsLogActions(Enum):
    SETTINGS_INITED = 'settings_inited'
    SETTINGS_CHANGED = 'settings_changed'
