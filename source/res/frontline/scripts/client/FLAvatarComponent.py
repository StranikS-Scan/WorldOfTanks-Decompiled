# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/FLAvatarComponent.py
import BigWorld
from ReservesEvents import randomReservesEvents
from frontline.FLReplayController import FLReplayController, CallbackDataNames
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

class FLAvatarComponent(BigWorld.DynamicScriptComponent):
    __epicMetaCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self):
        super(FLAvatarComponent, self).__init__()
        FLReplayController.serializeCallbackData(CallbackDataNames.FL_MODIFIER, (self.__epicMetaCtrl.getEpicBattlesReservesModifier(),))
        FLReplayController.setDataCallback(CallbackDataNames.FL_MODIFIER, self.__restoreReplayReservesModifier)

    def onDestroy(self):
        FLReplayController.delDataCallback(CallbackDataNames.FL_MODIFIER, self.__restoreModifier)
        super(FLAvatarComponent, self).onDestroy()

    @staticmethod
    def __restoreReplayReservesModifier(value):
        randomReservesEvents.onChangedReservesModifier(value)
