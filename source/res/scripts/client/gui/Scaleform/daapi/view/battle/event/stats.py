# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/stats.py
from helpers import dependency
from gui.Scaleform.daapi.view.meta.EventStatsMeta import EventStatsMeta
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.Scaleform.daapi.view.battle.event.team_info import makeTeamVehiclesInfo, makeTeamMissionsInfo

class EventStats(EventStatsMeta, GameEventGetterMixin):
    itemsFactory = dependency.descriptor(IGuiItemsFactory)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(EventStats, self)._populate()
        checkpoints = self.checkpoints
        if checkpoints:
            checkpoints.onUpdated += self.__onTeamMissionUpdate
        self.__onTeamMissionUpdate()
        generals = self.generals
        if generals:
            generals.onUpdated += self.__onGeneralsUpdated
            self.__onGeneralsUpdated()

    def _dispose(self):
        checkpoints = self.checkpoints
        if checkpoints:
            checkpoints.onUpdated -= self.__onTeamMissionUpdate
        generals = self.generals
        if generals:
            generals.onUpdated -= self.__onGeneralsUpdated
        super(EventStats, self)._dispose()

    def __onTeamMissionUpdate(self):
        checkpoints = self.checkpoints
        if not checkpoints:
            return
        self.as_setTeamMissionsProgressS(makeTeamMissionsInfo(checkpoints))

    def __onGeneralsUpdated(self):
        vehiclesInfo = makeTeamVehiclesInfo(self.generals, self.sessionProvider.getArenaDP(), self.itemsFactory)
        if vehiclesInfo:
            self.as_setTeamMissionsVehiclesS({'dataprovider': vehiclesInfo})
