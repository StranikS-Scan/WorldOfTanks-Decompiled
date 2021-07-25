# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/common.py
import BigWorld
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider

class SoundPlayersController(object):

    def __init__(self):
        self._soundPlayers = set()

    def init(self):
        for player in self._soundPlayers:
            player.init()

    def destroy(self):
        for player in self._soundPlayers:
            player.destroy()

        self._soundPlayers = None
        return


class VehicleStateSoundPlayer(object):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        ctrl = self._sessionProvider.shared.vehicleState
        ctrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        BigWorld.player().onSwitchingViewPoint += self._onSwitchViewPoint

    def destroy(self):
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
        if isPlayerAvatar():
            BigWorld.player().onSwitchingViewPoint -= self._onSwitchViewPoint
        return

    def _onVehicleStateUpdated(self, state, value):
        pass

    def _onSwitchViewPoint(self):
        pass


class BaseEfficiencySoundPlayer(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def init(self):
        ctrl = self.__sessionProvider.shared.personalEfficiencyCtrl
        ctrl.onPersonalEfficiencyReceived += self._onEfficiencyReceived

    def destroy(self):
        ctrl = self.__sessionProvider.shared.personalEfficiencyCtrl
        if ctrl is not None:
            ctrl.onPersonalEfficiencyReceived -= self._onEfficiencyReceived
        return

    def _onEfficiencyReceived(self, events):
        pass
