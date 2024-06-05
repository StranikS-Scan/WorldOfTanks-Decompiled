# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/FLAvatarComponent.py
import BattleReplay
from ReservesEvents import randomReservesEvents
from frontline_common.constants import CallbackDataNames
from script_component.DynamicScriptComponent import DynamicScriptComponent
from frontline.FLReplayController import FLReplayController

class FLAvatarComponent(DynamicScriptComponent):

    def onDestroy(self):
        FLReplayController.delDataCallback(CallbackDataNames.FL_MODIFIER, randomReservesEvents.onChangedReservesModifier)
        super(FLAvatarComponent, self).onDestroy()

    def _onAvatarReady(self):
        if not BattleReplay.g_replayCtrl.isPlaying:
            modifier = self.entity.arenaExtraData.get('reservesModifier')
            FLReplayController.serializeCallbackData(CallbackDataNames.FL_MODIFIER, (modifier,))
            randomReservesEvents.onChangedReservesModifier(modifier)
        FLReplayController.setDataCallback(CallbackDataNames.FL_MODIFIER, randomReservesEvents.onChangedReservesModifier)
