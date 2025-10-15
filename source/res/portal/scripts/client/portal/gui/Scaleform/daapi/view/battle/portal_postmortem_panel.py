# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_postmortem_panel.py
import BigWorld
from helpers import dependency
from gui.battle_control import avatar_getter
from portal.sounds.sound_constants import PortalMusicState, PortalBattleUISound
from portal.sounds.sound_helpers import play2DSound
from skeletons.gui.battle_session import IBattleSessionProvider
from VehicleRespawnComponent import VehicleRespawnComponent
from portal.gui.Scaleform.daapi.view.meta.PortalPostmortemPanelMeta import PortalPostmortemPanelMeta

class PortalPostmortemPanel(PortalPostmortemPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(PortalPostmortemPanel, self)._populate()
        VehicleRespawnComponent.onSetSpawnTime += self.__onSetSpawnTime
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        return

    def _dispose(self):
        VehicleRespawnComponent.onSetSpawnTime -= self.__onSetSpawnTime
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            ctrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        super(PortalPostmortemPanel, self)._dispose()
        return

    def __onSetSpawnTime(self, entityID, spawnTime):
        if entityID == avatar_getter.getPlayerVehicleID():
            self.as_setTimerS(spawnTime - BigWorld.serverTime())

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        play2DSound(PortalBattleUISound.POSTMORTEM_ON)
        PortalMusicState.setState(PortalMusicState.RESPAWN)

    def __onRespawnBaseMoving(self):
        play2DSound(PortalBattleUISound.POSTMORTEM_OFF)
