# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/menu_radial/radial_menu_override.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_GUI_TYPE

class RadialMenuOverride(object):
    __slots__ = ('__usualObject',)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, usualObject):
        self.__usualObject = usualObject

    def __call__(self):
        if self.sessionProvider.arenaVisitor.getArenaGuiType() in ARENA_GUI_TYPE.EPIC_RANGE:
            from gui.Scaleform.daapi.view.battle.epic.radial_menu import EpicRadialMenu
            return EpicRadialMenu
        return self.__usualObject
