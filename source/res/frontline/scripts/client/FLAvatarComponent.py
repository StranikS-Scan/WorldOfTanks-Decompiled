# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/FLAvatarComponent.py
import BattleReplay
from ReservesEvents import randomReservesEvents
from frontline_common.constants import CallbackDataNames
from frontline.FLReplayController import FLReplayController
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent

class FLAvatarComponent(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onDestroy(self):
        FLReplayController.delDataCallback(CallbackDataNames.FL_MODIFIER, randomReservesEvents.onChangedReservesModifier)
        super(FLAvatarComponent, self).onDestroy()

    def _onAvatarReady(self):
        if not BattleReplay.g_replayCtrl.isPlaying:
            modifier = self.entity.arenaExtraData.get('reservesModifier')
            FLReplayController.serializeCallbackData(CallbackDataNames.FL_MODIFIER, (modifier,))
            randomReservesEvents.onChangedReservesModifier(modifier)
        FLReplayController.setDataCallback(CallbackDataNames.FL_MODIFIER, randomReservesEvents.onChangedReservesModifier)

    def callCtrl(self, func, *args):
        respawnCtrl = self.__guiSessionProvider.dynamic.respawn
        if respawnCtrl:
            getattr(respawnCtrl, func, lambda *x: None)(*args)

    def updateRespawnVehicles(self, vehsList):
        self.callCtrl('updateRespawnVehicles', vehsList)

    def updateRespawnCooldowns(self, cooldowns):
        cooldowns = {item['vehTypeCompDescr']:item['endOfCooldownPiT'] for item in cooldowns}
        self.callCtrl('updateRespawnCooldowns', cooldowns)

    def updateRespawnInfo(self, respawnInfo):
        self.callCtrl('updateRespawnInfo', respawnInfo)

    def updateVehicleLimits(self, respawnLimits):
        respawnLimits = {item['group']:item['vehTypeCompDescrs'] for item in respawnLimits}
        self.callCtrl('updateVehicleLimits', respawnLimits)

    def onTeamLivesRestored(self, teams):
        self.callCtrl('restoredTeamRespawnLives', teams)

    def updatePlayerLives(self, lives):
        self.callCtrl('updatePlayerRespawnLives', lives)
