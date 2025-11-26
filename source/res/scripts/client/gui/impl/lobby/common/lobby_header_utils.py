# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/lobby_header_utils.py
from __future__ import absolute_import
from enum import Enum
from shared_utils import BitmaskHelper
HEADER_BUTTONS_COUNTERS_CHANGED_EVENT = 'lobbyHeaderButtonsCountersChanged'
_EXT_FIGHT_BUTTON_TOOLTIP_GETTERS = []

class HeaderMenuVisibilityState(BitmaskHelper):
    NOTHING = 0
    BG_OVERLAY = 1
    BUTTON_BAR = 2
    ONLINE_COUNTER = 4
    ALL = BG_OVERLAY | BUTTON_BAR | ONLINE_COUNTER


class LobbyHeaderVisibilityAction(Enum):
    ENTER = 0
    EXIT = 1


def registerFightButtonTooltipGetter(getter):
    _EXT_FIGHT_BUTTON_TOOLTIP_GETTERS.append(getter)


def findExtensionTooltip(pValidation):
    for getter in _EXT_FIGHT_BUTTON_TOOLTIP_GETTERS:
        tooltip = getter(pValidation)
        if tooltip is not None:
            return tooltip

    return
