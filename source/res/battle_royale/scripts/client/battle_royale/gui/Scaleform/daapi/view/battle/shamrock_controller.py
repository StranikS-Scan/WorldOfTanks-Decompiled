# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/shamrock_controller.py
import BattleReplay
import BigWorld
from gui.Scaleform.daapi.view.meta.BRShamrockControllerMeta import BRShamrockControllerMeta
from ReplayEvents import g_replayEvents
from VehicleBRStPatrickComponent import VehicleBRStPatrickComponent

class BRShamrockController(BRShamrockControllerMeta):

    def __init__(self):
        super(BRShamrockController, self).__init__()
        self.__observedVehicleID = None
        return

    def _populate(self):
        super(BRShamrockController, self)._populate()
        BigWorld.player().onObserverVehicleChanged += self.__setCounter
        if not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            VehicleBRStPatrickComponent.onCoinsAdded += self.__onCoinsAdded
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart += self.__onReplayTimeWarpStart
            g_replayEvents.onTimeWarpFinish += self.__onReplayTimeWarpFinish
        self.__setCounter()

    def _dispose(self):
        player = BigWorld.player()
        if player:
            player.onObserverVehicleChanged -= self.__setCounter
        VehicleBRStPatrickComponent.onCoinsAdded -= self.__onCoinsAdded
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onTimeWarpStart -= self.__onReplayTimeWarpStart
            g_replayEvents.onTimeWarpFinish -= self.__onReplayTimeWarpFinish
        self.__observedVehicleID = None
        super(BRShamrockController, self)._dispose()
        return

    def __onCoinsAdded(self, amount, newTotal, fromTeammate=False):
        self.as_addPointsS(amount, newTotal, fromTeammate)

    def __setCounter(self, force=False):
        vehicle = BigWorld.player().vehicle
        if not vehicle or vehicle.id == self.__observedVehicleID and not force:
            return
        self.__observedVehicleID = vehicle.id
        stPatrickComp = vehicle.dynamicComponents.get('vehicleBRStPatrickComponent')
        if stPatrickComp:
            self.as_setCounterS(stPatrickComp.totalCoins)

    def __onReplayTimeWarpStart(self):
        VehicleBRStPatrickComponent.onCoinsAdded -= self.__onCoinsAdded

    def __onReplayTimeWarpFinish(self):
        VehicleBRStPatrickComponent.onCoinsAdded += self.__onCoinsAdded
        self.__setCounter(True)
