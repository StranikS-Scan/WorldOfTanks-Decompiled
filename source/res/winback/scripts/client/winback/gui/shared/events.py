# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/shared/events.py
from gui.shared.event_bus import SharedEvent

class WinbackViewEvent(SharedEvent):
    WINBACK_REWARD_VIEW_LOADED = 'onWinbackRewardViewLoad'
    WINBACK_REWARD_VIEW_CLOSED = 'onWinbackRewardViewClosed'
