# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/damage/damage_log_panel_override.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_GUI_TYPE
from gui.shared.system_factory import collectDamageLogPanel

class DamageLogPanelOverride(object):
    __slots__ = ('__usualObject',)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, usualObject):
        self.__usualObject = usualObject

    def __call__(self):
        guiType = self.sessionProvider.arenaVisitor.getArenaGuiType()
        if guiType in ARENA_GUI_TYPE.EPIC_RANGE:
            from gui.Scaleform.daapi.view.battle.epic.damage_log_panel import EpicDamageLogPanel
            return EpicDamageLogPanel
        else:
            panelCls = collectDamageLogPanel(guiType)
            return panelCls if panelCls is not None else self.__usualObject
