# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/common.py
import typing
import BattleReplay
import BigWorld
import SoundGroups
from Event import EventsSubscriber
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from shared_utils import nextTick

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


class SoundPlayersBattleController(IBattleController):

    def __init__(self):
        self.__soundPlayers = self._initializeSoundPlayers()

    def startControl(self, *args):
        self.__startPlayers()

    def stopControl(self):
        self.__destroyPlayers()

    def getControllerID(self):
        return BATTLE_CTRL_ID.SOUND_PLAYERS_CTRL

    def _initializeSoundPlayers(self):
        raise NotImplementedError

    def __startPlayers(self):
        for player in self.__soundPlayers:
            player.init()

    def __destroyPlayers(self):
        for player in self.__soundPlayers:
            player.destroy()

        self.__soundPlayers = None
        return


class ISoundPlayer(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError


class SoundPlayer(ISoundPlayer):

    def init(self):
        nextTick(self._subscribe)()

    def destroy(self):
        self._unsubscribe()

    def _subscribe(self):
        raise NotImplementedError

    def _unsubscribe(self):
        raise NotImplementedError

    @staticmethod
    def _playSound2D(event, checkAlive=False):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            return
        else:
            if checkAlive:
                vehicle = BigWorld.player().getVehicleAttached()
                if vehicle is not None and not vehicle.isAlive():
                    return
            SoundGroups.g_instance.playSound2D(event)
            return


class VehicleStateSoundPlayer(SoundPlayer):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _subscribe(self):
        ctrl = self._sessionProvider.shared.vehicleState
        ctrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        BigWorld.player().onSwitchingViewPoint += self._onSwitchViewPoint

    def _unsubscribe(self):
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


class BaseEfficiencySoundPlayer(SoundPlayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _subscribe(self):
        ctrl = self.__sessionProvider.shared.personalEfficiencyCtrl
        ctrl.onPersonalEfficiencyReceived += self._onEfficiencyReceived

    def _unsubscribe(self):
        ctrl = self.__sessionProvider.shared.personalEfficiencyCtrl
        if ctrl is not None:
            ctrl.onPersonalEfficiencyReceived -= self._onEfficiencyReceived
        return

    def _onEfficiencyReceived(self, events):
        pass


class EquipmentComponentSoundPlayer(object):
    __slots__ = ('__eventsSubscriber',)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__eventsSubscriber = None
        return

    def init(self):
        self.__eventsSubscriber = EventsSubscriber()
        self.__eventsSubscriber.subscribeToContextEvent(self.__sessionProvider.shared.vehicleState.onEquipmentComponentUpdated, self._onEquipmentComponentUpdated, self._getEquipmentName())
        self.__eventsSubscriber.subscribeToEvent(self.__sessionProvider.shared.vehicleState.onVehicleControlling, self.__onVehicleControlling)

    def destroy(self):
        self.__eventsSubscriber.unsubscribeFromAllEvents()
        self.__eventsSubscriber = None
        return

    def _onEquipmentComponentUpdated(self, equipmentName, vehicleID, equipmentInfo):
        raise NotImplementedError

    def _getEquipmentName(self):
        raise NotImplementedError

    def _stopSounds(self):
        raise NotImplementedError

    def _getComponentName(self):
        raise NotImplementedError

    def __onVehicleControlling(self, vehicle):
        self._stopSounds()
        component = vehicle.dynamicComponents.get(self._getComponentName())
        if component is not None:
            self._onEquipmentComponentUpdated(component.EQUIPMENT_NAME, vehicle.id, component.getInfo())
        return
