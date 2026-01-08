# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/activation_triggers.py
import typing
import logging
import BigWorld
import TriggersManager
from helpers import dependency
from constants import ARENA_PERIOD
from gui.battle_control.battle_context_hints.common import HintId
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
_logger = logging.getLogger(__name__)

class HintActivationTrigger(object):

    def __init__(self, hintId, activationCallback, *args, **kwargs):
        self._hintId = hintId
        self._activationCallback = activationCallback
        self._args = args
        self._kwargs = kwargs

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class PreBattleHintActivationTrigger(HintActivationTrigger):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hintId, activationCallback, *args, **kwargs):
        super(PreBattleHintActivationTrigger, self).__init__(hintId, activationCallback, *args, **kwargs)
        self.__arena = self._sessionProvider.arenaVisitor.getArenaSubscription()

    def start(self):
        if self.__arena is not None:
            self.__arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def stop(self):
        if self.__arena is not None:
            self.__arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def needToShowHint(self):
        raise NotImplementedError

    def __onArenaPeriodChange(self, period, *args, **kwargs):
        if period == ARENA_PERIOD.BATTLE and self.needToShowHint():
            self._activationCallback(self._hintId, *self._args, **self._kwargs)


class KilledWhileObservedHintTrigger(HintActivationTrigger):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hintId, activationCallback, *args, **kwargs):
        super(KilledWhileObservedHintTrigger, self).__init__(hintId, activationCallback, *args, **kwargs)
        self.__vehicleStateCtrl = None
        return

    def start(self):
        if self.__vehicleStateCtrl is None:
            self.__vehicleStateCtrl = self.sessionProvider.shared.vehicleState
            if self.__vehicleStateCtrl is not None:
                self.__vehicleStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        return

    def stop(self):
        if self.__vehicleStateCtrl is not None:
            self.__vehicleStateCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            self.__vehicleStateCtrl = None
        return

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        playerVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if playerVehicle is None:
            _logger.error('playerVehicle is None')
            return
        else:
            sixthSenseState = playerVehicle.sixthSenseState
            if sixthSenseState:
                self._activationCallback(self._hintId, *self._args, **self._kwargs)
            return


class InSafetyWhileNotObservedHintTrigger(PreBattleHintActivationTrigger):

    def needToShowHint(self):
        hintsCtrl = self._sessionProvider.dynamic.battleContextHintsCtrl
        hintsData = hintsCtrl.getHintsData().get(HintId.KILLED_WHILE_OBSERVED)
        return hintsData and hintsData.getLastBattleTriggered()


class AmmunitionCritHintTrigger(HintActivationTrigger, TriggersManager.ITriggerListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hintId, activationCallback, *args, **kwargs):
        super(AmmunitionCritHintTrigger, self).__init__(hintId, activationCallback, *args, **kwargs)
        self.__vehicleStateCtrl = None
        self.__needToShowHint = False
        return

    def start(self):
        if self.__vehicleStateCtrl is None:
            self.__vehicleStateCtrl = self.__sessionProvider.shared.vehicleState
            if self.__vehicleStateCtrl is not None:
                self.__vehicleStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        TriggersManager.g_manager.addListener(self)
        return

    def stop(self):
        if self.__vehicleStateCtrl is not None:
            self.__vehicleStateCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            self.__vehicleStateCtrl = None
        TriggersManager.g_manager.delListener(self)
        return

    def onTriggerActivated(self, args):
        if args['type'] != TriggersManager.TRIGGER_TYPE.PLAYER_RECEIVE_DAMAGE:
            return
        elif args['vehicleId'] != BigWorld.player().playerVehicleID:
            return
        else:
            damageContext = args['damageContext']
            if damageContext is None:
                return
            if damageContext['damageCode'] == 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT':
                deviceName = damageContext['extra'].name[:-len('Health')]
                if deviceName == 'ammoBay' and self.__needToShowHint:
                    self._activationCallback(self._hintId, *self._args, **self._kwargs)
                    self.__needToShowHint = False
            return

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__needToShowHint = True


class FueltankCritHintTrigger(HintActivationTrigger):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hintId, activationCallback, *args, **kwargs):
        super(FueltankCritHintTrigger, self).__init__(hintId, activationCallback, *args, **kwargs)
        self._vehicleStateCtrl = None
        self._equipmentCtrl = None
        self._wasOnFire = False
        self._hasExtinguisher = True
        return

    def start(self):
        if self._equipmentCtrl is None:
            self._equipmentCtrl = self._sessionProvider.shared.equipments
        if self._vehicleStateCtrl is None:
            self._vehicleStateCtrl = self._sessionProvider.shared.vehicleState
            if self._vehicleStateCtrl is not None:
                self._vehicleStateCtrl.onPostMortemSwitched += self._onPostMortemSwitched
                self._vehicleStateCtrl.onVehicleStateUpdated += self._onVehicleStateUpdated
        return

    def stop(self):
        if self._vehicleStateCtrl is not None:
            self._vehicleStateCtrl.onPostMortemSwitched -= self._onPostMortemSwitched
            self._vehicleStateCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
            self._vehicleStateCtrl = None
        self._equipmentCtrl = None
        self._wasOnFire = False
        self._hasExtinguisher = True
        return

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.FIRE:
            if value:
                self._wasOnFire = True
                self._vehicleStateCtrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
                self._hasExtinguisher = bool(next(self._equipmentCtrl.iterEquipmentsByTag('extinguisher'), False))

    def _onPostMortemSwitched(self, *_):
        if self._wasOnFire and not self._hasExtinguisher:
            self._activationCallback(self._hintId, *self._args, **self._kwargs)


class ModuleDamageHintTrigger(PreBattleHintActivationTrigger):
    _MODULE_RELATED_HINTS = [HintId.ENGINE_DAMAGE_REPAIR_KIT,
     HintId.ENGINE_DESTROY_REPAIR_KIT,
     HintId.AMMUNITION_DAMAGE_REPAIR_KIT,
     HintId.GUN_ROTATOR_DAMAGE_REPAIR_KIT,
     HintId.GUN_ROTATOR_DESTROY_REPAIR_KIT,
     HintId.GUN_DAMAGE_REPAIR_KIT,
     HintId.GUN_DESTROY_REPAIR_KIT,
     HintId.TRACK_DESTROY_REPAIR_KIT,
     HintId.FUELTANK_DAMAGE_REPAIR_KIT]

    def needToShowHint(self):
        hintsCtrl = self._sessionProvider.dynamic.battleContextHintsCtrl
        hintsData = hintsCtrl.getHintsData()
        return all((hintData.getWatchingCounter() == 0 for hintId, hintData in hintsData.iteritems() if hintId in self._MODULE_RELATED_HINTS))
