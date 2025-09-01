# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/equipment_items.py
import weakref
import random
from functools import partial
from collections import namedtuple
import BigWorld
from Math import Vector3, Vector2
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control import avatar_getter
from gui.shared.system_factory import registerEquipmentItem
from gui.battle_control.controllers.consumables.equipment_ctrl import _TriggerItem, InCooldownError, _ReplayItem
from gui.Scaleform.genConsts.BATTLE_MARKERS_CONSTS import BATTLE_MARKERS_CONSTS
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from constants import EQUIPMENT_STAGES
from white_tiger.gui.white_tiger_gui_constants import BATTLE_CTRL_ID
from white_tiger.gui.battle_control.controllers.consumables.white_tiger_equipment_ctrl import WTEquipmentSound
from TeleportKeyPoint import TeleportKeyPoint
_ActivationError = namedtuple('_ActivationError', 'key ctx')

class WtHealthAtFullHP(_ActivationError):

    def __new__(cls, name):
        return super(WtHealthAtFullHP, cls).__new__(cls, 'wtEventTankIsAtFullHP', {'name': name})

    def __init__(self, name):
        super(WtHealthAtFullHP, self).__init__('wtEventTankIsAtFullHP', {'name': name})


class _WTItem(_TriggerItem):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getAnimationType(self):
        if self._stage == EQUIPMENT_STAGES.COOLDOWN:
            return ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE
        return ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN if self._stage == EQUIPMENT_STAGES.ACTIVE else super(_WTItem, self).getAnimationType()

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked or self._timeRemaining > 0 and self._stage and self._stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN) or self._stage and self._stage in (EQUIPMENT_STAGES.STARTUP_COOLDOWN, EQUIPMENT_STAGES.UNAVAILABLE):
            result = False
            error = InCooldownError(self._descriptor.userString)
            return (result, error)
        return super(_WTItem, self).canActivate(entityName, avatar)

    def _updateEquipmentState(self):
        eqCtrl = self._sessionProvider.shared.equipments
        eq = eqCtrl.getEquipment(self._descriptor.compactDescr)
        eqCtrl.onEquipmentUpdated(self._descriptor.compactDescr, eq)


class _WTSelfRepairItem(_WTItem):

    def canActivate(self, entityName=None, avatar=None):
        if not self._isLocked and self._stage == EQUIPMENT_STAGES.READY:
            vehicleID = avatar_getter.getPlayerVehicleID()
            if vehicleID is not None:
                vehicle = BigWorld.entities.get(vehicleID)
                if vehicle and vehicle.health == vehicle.maxHealth:
                    result = False
                    error = WtHealthAtFullHP(self._descriptor.userString)
                    return (result, error)
        return super(_WTSelfRepairItem, self).canActivate(entityName, avatar)


class _WTStrongholdItem(_WTItem):

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked:
            return (False, InCooldownError(self._descriptor.userString))
        else:
            return (True, None) if self._stage == EQUIPMENT_STAGES.ACTIVE or self._stage == EQUIPMENT_STAGES.READY else super(_WTStrongholdItem, self).canActivate(entityName, avatar)


class _TeleportItem(_WTItem):

    def __init__(self, descriptor, quantity, stage, timeRemaining, _, tags=None):
        totalTime = descriptor.cooldownSeconds
        self.teleportPoints = [ {'guid': udo.guid,
         'position': (udo.position.x, udo.position.z),
         'position3D': (udo.position.x, udo.position.y, udo.position.z),
         'yaw': udo.yaw,
         'index': udo.positionNumber} for udo in BigWorld.userDataObjects.values() if isinstance(udo, TeleportKeyPoint) ]
        super(_TeleportItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_TeleportItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.DEPLOYING:
            self._totalTime = self._descriptor.deploySeconds
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = timeRemaining
        elif stage == EQUIPMENT_STAGES.PREPARING:
            self._totalTime = 0
        teleport = self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
        if stage != EQUIPMENT_STAGES.PREPARING and teleport.isSpawnPointsVisible:
            teleport.closeSpawnPoints()

    def canActivate(self, entityName=None, avatar=None):
        if self._timeRemaining > 0 and self._stage and self._stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            result = False
            error = InCooldownError(self._descriptor.userString)
            return (result, error)
        return super(_TeleportItem, self).canActivate(entityName, avatar)

    def activate(self, entityName=None, avatar=None):
        teleport = self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
        if teleport is not None:
            teleport.setEquipment(weakref.proxy(self))
            teleport.showSpawnPoints(self.teleportPoints)
            self._stage = EQUIPMENT_STAGES.PREPARING
            self._updateEquipmentState()
        return

    def deactivate(self):
        teleport = self._sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
        if teleport is not None:
            teleport.closeSpawnPoints()
            self._stage = EQUIPMENT_STAGES.READY
            self._updateEquipmentState()
        return

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def apply(self, pointGuid):
        chosen = random.choice(self.teleportPoints)
        for spawn in self.teleportPoints:
            if spawn['guid'] == pointGuid:
                chosen = spawn
                break

        BigWorld.player().setEquipmentApplicationPoint(self.getEquipmentID(), Vector3(chosen['position3D']), Vector2(chosen['yaw'], 0))


class _HyperionItem(_WTItem):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_YELLOW

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def setLocked(self, isLocked):
        vehicleID = avatar_getter.getPlayerVehicleID()
        if vehicleID is not None:
            vehicle = BigWorld.entities.get(vehicleID)
            if self._stage == EQUIPMENT_STAGES.ACTIVE and 'wtTeleportDebuff' in vehicle.dynamicComponents:
                self._isLocked = False
                return
        self._isLocked = isLocked
        return

    def activate(self, entityName=None, avatar=None):
        from AvatarInputHandler import MapCaseMode
        self._stage = EQUIPMENT_STAGES.PREPARING
        MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate), self.getAimingControlMode())
        self._updateEquipmentState()

    def deactivate(self):
        self.__cancelAiming(True)
        self._stage = EQUIPMENT_STAGES.READY
        self._updateEquipmentState()

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_HyperionItem, self).update(quantity, stage, timeRemaining, totalTime)
        if self._stage in (EQUIPMENT_STAGES.EXHAUSTED, EQUIPMENT_STAGES.READY):
            self.__cancelAiming()
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            self._timeRemaining = -1
            self._totalTime = 0

    def getAnimationType(self):
        return ANIMATION_TYPES.SHOW_COUNTER_GREEN if self._stage == EQUIPMENT_STAGES.COOLDOWN else super(_HyperionItem, self).getAnimationType()

    def getStrikeSelector(self):
        from white_tiger.avatar_input_handler.map_case_mode import HyperionStrikeSelector
        return HyperionStrikeSelector

    def getAimingControlMode(self):
        from WTMapCaseMode import HyperionMapCaseControlMode
        return HyperionMapCaseControlMode

    def __cancelAiming(self, playCancelSound=False):
        if playCancelSound:
            WTEquipmentSound.playCancel(self)
        from AvatarInputHandler import MapCaseMode
        MapCaseMode.turnOffMapCase(self.getEquipmentID(), self.getAimingControlMode())

    def getTotalTime(self):
        return self._descriptor.deploySeconds


class _ShellOverrideItem(_WTItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_ShellOverrideItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.READY:
            self._timeRemaining = 0
            self._totalTime = 0
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._timeRemaining = -1
            self._totalTime = 0


def isWtEventItem(item):
    return isinstance(item, _WTItem)


def registerWTEquipmentsItems():
    registerEquipmentItem('builtinAfterburning_wt', _WTItem, _ReplayItem)
    registerEquipmentItem('builtinInstantStunShoot_wt', _WTItem, _ReplayItem)
    registerEquipmentItem('builtinImpulse_wt', _WTItem, _ReplayItem)
    registerEquipmentItem('builtinShield_wt', _WTItem, _ReplayItem)
    registerEquipmentItem('builtinSelfRepair_wt', _WTSelfRepairItem, _ReplayItem)
    registerEquipmentItem('builtinStronghold_wt', _WTStrongholdItem, _ReplayItem)
    registerEquipmentItem('builtinTeleport_wt', _TeleportItem, _ReplayItem)
    registerEquipmentItem('builtinChargedShot_wt', _ShellOverrideItem, _ReplayItem)
    registerEquipmentItem('builtinExplosiveShot_wt', _ShellOverrideItem, _ReplayItem)
    registerEquipmentItem('builtinHyperion_wt', _HyperionItem, _ReplayItem)
