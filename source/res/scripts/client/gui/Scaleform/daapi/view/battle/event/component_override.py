# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/component_override.py
from gui.battle_control import avatar_getter
from constants import ARENA_GUI_TYPE

class EventComponentOverride(object):
    __slots__ = ('__usualObject', '__eventObject')

    def __init__(self, usualObject, eventObject):
        super(EventComponentOverride, self).__init__()
        self.__usualObject = usualObject
        self.__eventObject = eventObject

    def __call__(self):
        arena = avatar_getter.getArena()
        isEvent = arena.guiType == ARENA_GUI_TYPE.EVENT_BATTLES if arena else False
        return self.__eventObject if isEvent else self.__usualObject
