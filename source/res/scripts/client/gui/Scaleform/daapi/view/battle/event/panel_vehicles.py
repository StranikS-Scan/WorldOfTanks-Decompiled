# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/panel_vehicles.py
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.daapi.view.meta.PanelVehiclesMeta import PanelVehiclesMeta

class EventPanelVehicles(PanelVehiclesMeta):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(EventPanelVehicles, self)._populate()
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated += self.__onPlayerRespawnLivesUpdated
        return

    def _dispose(self):
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated -= self.__onPlayerRespawnLivesUpdated
        super(EventPanelVehicles, self)._dispose()
        return

    def __onPlayerRespawnLivesUpdated(self, playerLives):
        self.as_setCountLivesS(playerLives)
