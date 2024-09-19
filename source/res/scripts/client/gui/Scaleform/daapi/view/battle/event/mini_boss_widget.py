# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/mini_boss_widget.py
from cgf_components.wt_helpers import isBoss
from gui.Scaleform.daapi.view.meta.EventMiniBossWidgetMeta import EventMiniBossWidgetMeta
from gui.Scaleform.locale.EVENT import EVENT
from gui.battle_control.arena_info import player_format
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency, i18n
from skeletons.gui.battle_session import IBattleSessionProvider

class EventMiniBossWidget(EventMiniBossWidgetMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventMiniBossWidget, self).__init__()
        self.__playerFormatter = player_format.PlayerFullNameFormatter()

    def setupMiniBossInfo(self, vInfo):
        miniBossName = i18n.makeString(EVENT.BOTNAMES_ERMELINDA).encode('utf-8')
        self.as_setMiniBossWidgetDataS(miniBossName=miniBossName, hpCurrent=vInfo.vehicleType.maxHealth, hpMax=vInfo.vehicleType.maxHealth, isEnemy=not isBoss())

    def resetMiniBossWidget(self):
        self.as_resetMiniBossWidgetS()

    def _populate(self):
        super(EventMiniBossWidget, self)._populate()
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicHealthChange += self.__onPublicHealthChange
        arenaDP = self.__sessionProvider.getArenaDP()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if VEHICLE_TAGS.EVENT_MINI_BOSS in vInfo.vehicleType.tags:
                self.setupMiniBossInfo(vInfo)
                break

    def _dispose(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicHealthChange -= self.__onPublicHealthChange
        super(EventMiniBossWidget, self)._dispose()

    def __onPublicHealthChange(self, vehicleID, newHealth):
        arenaDP = self.__sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo(vehicleID)
        if VEHICLE_TAGS.EVENT_MINI_BOSS in vInfoVO.vehicleType.tags:
            self.as_updateMiniBossHpS(newHealth)
