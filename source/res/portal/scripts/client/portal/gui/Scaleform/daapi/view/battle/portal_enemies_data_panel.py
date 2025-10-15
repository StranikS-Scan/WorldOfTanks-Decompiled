# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_enemies_data_panel.py
import typing
import logging
import BigWorld
from helpers import dependency
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from skeletons.gui.battle_session import IBattleSessionProvider
from PortalBattleStateComponent import PortalBattleStateComponent
from portal.gui.Scaleform.daapi.view.meta.PortalEnemiesPanelMeta import PortalEnemiesPanelMeta
if typing.TYPE_CHECKING:
    from typing import List
_logger = logging.getLogger(__name__)

class PortalEnemiesDataPanel(PortalEnemiesPanelMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PortalEnemiesDataPanel, self).__init__()
        self.__arenaDP = None
        return

    def _populate(self):
        super(PortalEnemiesDataPanel, self)._populate()
        self.__arenaDP = self.__sessionProvider.getArenaDP()
        PortalBattleStateComponent.onWaveStarted += self.__onWaveStarted
        PortalBattleStateComponent.onWavesBuffed += self.__onWavesBuffed
        PortalBattleStateComponent.onLaneInfoChanged += self.__onLaneInfoChanged
        self.__updateModel()

    def _dispose(self):
        PortalBattleStateComponent.onLaneInfoChanged -= self.__onLaneInfoChanged
        PortalBattleStateComponent.onWavesBuffed -= self.__onWavesBuffed
        PortalBattleStateComponent.onWaveStarted -= self.__onWaveStarted
        self.__arenaDP = None
        super(PortalEnemiesDataPanel, self)._dispose()
        return

    def __updateModel(self):
        battleState = BigWorld.player().arena.arenaInfo.portalBattleStateComponent
        if not battleState:
            return
        self.__onWaveStarted(battleState.currentWave, battleState.wavesCount)
        self.__onWavesBuffed(battleState.wavesBuffed)
        for laneID, laneInfo in battleState.getLanesInfo().items():
            if laneInfo:
                self.__onLaneInfoChanged(laneID, laneInfo)

    def __onWaveStarted(self, currentWave, wavesCount):
        self.as_setCurrentPhaseS(currentWave)
        self.as_setPhasesCountS(wavesCount)

    def __onWavesBuffed(self, wavesBuffed):
        self.as_setBuffStatusVisibleS(wavesBuffed)

    def __onLaneInfoChanged(self, laneID, activeVehicles):
        heavyCount = 0
        lightCount = 0
        mediumCount = 0
        for vehicleID in activeVehicles:
            vInfoVo = self.__arenaDP.getVehicleInfo(vehicleID)
            classTag = vInfoVo.vehicleType.classTag
            if classTag == VEHICLE_CLASS_NAME.HEAVY_TANK:
                heavyCount += 1
            if classTag == VEHICLE_CLASS_NAME.LIGHT_TANK:
                lightCount += 1
            if classTag == VEHICLE_CLASS_NAME.MEDIUM_TANK:
                mediumCount += 1

        self.as_setLaneVehicleInfoS(laneID, heavyCount=heavyCount, lightCount=lightCount, mediumCount=mediumCount)
