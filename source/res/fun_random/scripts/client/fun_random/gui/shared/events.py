# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/events.py
from enum import unique, IntEnum
from gui.shared.events import HasCtxEvent
from gui.shared.event_bus import SharedEvent

class FunSelectionEvent(SharedEvent):

    def __init__(self, selectedSubModeID):
        super(FunSelectionEvent, self).__init__(FunEventType.SUB_SELECTION)
        self.selectedSubModeID = selectedSubModeID


class FunSubModesEvent(HasCtxEvent):

    def __init__(self, eventType, subModes, ctx=None):
        super(FunSubModesEvent, self).__init__(eventType, ctx)
        self.subModes = subModes


@unique
class FunEventScope(IntEnum):
    DEFAULT = 1
    DESIRABLE = 2


@unique
class FunEventType(IntEnum):
    SUB_SETTINGS = 1
    SUB_SELECTION = 2
    SUB_STATUS_UPDATE = 3
    SUB_STATUS_TICK = 4
    PROGRESSION_UPDATE = 5
    PROGRESSION_TICK = 6
