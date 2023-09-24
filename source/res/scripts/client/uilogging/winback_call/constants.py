# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/winback_call/constants.py
from enum import Enum
FEATURE = 'winback_call'

class WinbackCallLogItem(Enum):
    ACCEPT_BUTTON = 'accept_button'
    LINK_BUTTON = 'link_button'
    FRIENDS_FORM_BUTTON = 'friends_form_button'
    INVITE_BUTTON = 'invite_button'
    CLOSE_BUTTON = 'close_button'


class WinbackCallLogScreenParent(Enum):
    INTRO_SCREEN = 'intro_screen'
    MAIN_VIEW = 'main_view'
    FRIENDS_FORM = 'friends_form'
    REWARDS_SCREEN = 'rewards_screen'


class WinBackCallLogActions(Enum):
    CLICK = 'click'
