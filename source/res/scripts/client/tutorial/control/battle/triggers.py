# Embedded file name: scripts/client/tutorial/control/battle/triggers.py
import BigWorld
import TriggersManager
from constants import ARENA_PERIOD
from gui.battle_control import g_sessionProvider
from tutorial import g_tutorialWeaver
from tutorial.control.battle import aspects
from tutorial.control.triggers import Trigger, TriggerWithValidateVar
from tutorial.logger import LOG_ERROR, LOG_DEBUG, LOG_MEMORY
__all__ = ['VehicleOnArenaTrigger',
 'PlayerVehicleNoAmmoTrigger',
 'ObjectAIMTrigger',
 'AreaTrigger',
 'AimAtVehicleTrigger',
 'AutoAimAtVehicleTrigger',
 'VehicleDestroyedTrigger',
 'VehicleOnSoftTerrainTrigger',
 'ShotMissedTrigger',
 'ShotNoDamageTrigger',
 'ShotDamageTrigger',
 'SniperModeTrigger',
 'TriggersDispatcher']

class VehicleOnArenaTrigger(TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None, key = 'name'):
        super(VehicleOnArenaTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)
        self.__key = key

    def isOn(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        pVehicleID = getattr(BigWorld.player(), 'playerVehicleID', -1)
        var = self.getVar()
        result = False
        if arena is None:
            LOG_ERROR('Client arena not found')
            return result
        else:
            for vehicleID, vehicle in arena.vehicles.iteritems():
                if vehicleID == pVehicleID:
                    continue
                value = vehicle.get(self.__key)
                if value is not None and value == var:
                    self.setVar(vehicleID)
                    result = True
                    break

            return result


class PlayerVehicleNoAmmoTrigger(Trigger):

    def __init__(self, triggerID, stateFlagID = None):
        super(PlayerVehicleNoAmmoTrigger, self).__init__(triggerID)
        self.__pIdx = -1
        self.__ammoLayout = {}
        self._stateFlag = None
        self._stateFlagID = stateFlagID
        return

    def __del__(self):
        LOG_MEMORY('PlayerVehicleNoAmmoTrigger deleted')

    def run(self):
        if not self.isSubscribed:
            self.__addListeners()
            self.__pIdx = g_tutorialWeaver.weave(pointcut=aspects.AmmoQuantityPointcut, aspects=(aspects.AmmoQuantityAspect(self),))
            self.isSubscribed = True
        if self._stateFlag is None:
            self._stateFlag = self._tutorial.getFlags().isActiveFlag(self._stateFlagID)
        super(PlayerVehicleNoAmmoTrigger, self).run()
        return

    def isOn(self, shoot = False):
        return sum(self.__ammoLayout.values()) is 0 and shoot

    def toggle(self, isOn = True, **kwargs):
        if self._stateFlag is isOn:
            self.isRunning = False
            return
        self._stateFlag = isOn
        super(PlayerVehicleNoAmmoTrigger, self).toggle(isOn=isOn, **kwargs)

    def clear(self):
        g_tutorialWeaver.clear(self.__pIdx)
        self.__pIdx = -1
        self.__ammoLayout.clear()
        self.__removeListeners()
        self.isSubscribed = False
        super(PlayerVehicleNoAmmoTrigger, self).clear()

    def __addListeners(self):
        ammoCtrl = g_sessionProvider.getAmmoCtrl()
        if ammoCtrl:
            ammoCtrl.onShellsAdded += self.__onShellsAdded
            ammoCtrl.onShellsUpdated += self.__onShellsUpdated
            for intCD, (quantity, _) in ammoCtrl.getShellsLayout():
                self.__ammoLayout[intCD] = quantity

    def __removeListeners(self):
        ammoCtrl = g_sessionProvider.getAmmoCtrl()
        if ammoCtrl:
            ammoCtrl.onShellsAdded -= self.__onShellsAdded
            ammoCtrl.onShellsUpdated -= self.__onShellsUpdated

    def __onShellsAdded(self, intCD, descriptor, quantity, quantityInClip, gunSettings):
        self.__ammoLayout[intCD] = quantity

    def __onShellsUpdated(self, intCD, quantity, quantityInClip, result):
        self.__ammoLayout[intCD] = quantity


class _DispatchableTrigger(TriggerWithValidateVar):

    def __init__(self, triggerID, validateVarID, setVarID = None, stateFlagID = None):
        super(_DispatchableTrigger, self).__init__(triggerID, validateVarID, setVarID=setVarID)
        self._stateFlag = None
        self._stateFlagID = stateFlagID
        return

    def isAllowed(self, triggerType, event):
        return False

    def getAllowed(self):
        return []

    def resolveState(self, isOn = False):
        if self._stateFlag is None:
            self._stateFlag = self._tutorial.getFlags().isActiveFlag(self._stateFlagID)
            self.toggle(isOn=isOn, benefit=True)
        return

    def isOn(self, stateFlag):
        return stateFlag

    def toggle(self, isOn = True, **kwargs):
        if self._stateFlag is isOn:
            return
        self._stateFlag = isOn
        super(_DispatchableTrigger, self).toggle(isOn=isOn, benefit=False)


class ObjectAIMTrigger(_DispatchableTrigger):

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.AIM and self.getVar() == event.get('name')

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.AIM]

    def resolveState(self, isOn = False):
        manager = TriggersManager.g_manager
        if manager is not None and manager.isEnabled():
            isOn = manager.isAutoTriggerActive(TriggersManager.TRIGGER_TYPE.AIM, self.getVar())
        super(ObjectAIMTrigger, self).resolveState(isOn=isOn)
        return


class AreaTrigger(_DispatchableTrigger):

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.AREA and self.getVar() == event.get('name')

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.AREA]

    def resolveState(self, isOn = False):
        manager = TriggersManager.g_manager
        if manager is not None and manager.isEnabled():
            isOn = manager.isAutoTriggerActive(TriggersManager.TRIGGER_TYPE.AREA, self.getVar())
        super(AreaTrigger, self).resolveState(isOn=isOn)
        return


class AimAtVehicleTrigger(_DispatchableTrigger):

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.AIM_AT_VEHICLE and self.getVar() == event.get('vehicleId')

    def getAllowed(self):
        return (TriggersManager.TRIGGER_TYPE.AIM_AT_VEHICLE,)


class AutoAimAtVehicleTrigger(_DispatchableTrigger):

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE and self.getVar() == event.get('vehicleId')

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.AUTO_AIM_AT_VEHICLE]


class VehicleDestroyedTrigger(_DispatchableTrigger):

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED and self.getVar() == event.get('vehicleId')

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.VEHICLE_DESTROYED]

    def resolveState(self, isOn = False):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            vehicle = arena.vehicles.get(self.getVar())
            if vehicle is not None:
                isOn = not vehicle.get('isAlive', True)
        super(VehicleDestroyedTrigger, self).resolveState(isOn=isOn)
        return


class VehicleOnSoftTerrainTrigger(_DispatchableTrigger):

    def __init__(self, triggerID, stateFlagID = None):
        super(VehicleOnSoftTerrainTrigger, self).__init__(triggerID, None, setVarID=None, stateFlagID=stateFlagID)
        return

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_ON_SOFT_TERRAIN

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_ON_SOFT_TERRAIN]


class ShotMissedTrigger(_DispatchableTrigger):

    def __init__(self, triggerID, stateFlagID = None):
        super(ShotMissedTrigger, self).__init__(triggerID, None, setVarID=None, stateFlagID=stateFlagID)
        return

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_MISSED

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_MISSED]


class ShotNoDamageTrigger(_DispatchableTrigger):

    def __init__(self, triggerID, validateVarID, setVarID = None, stateFlagID = None, maxCount = 1):
        super(ShotNoDamageTrigger, self).__init__(triggerID, validateVarID, setVarID)
        self._count = 0
        self._maxCount = maxCount

    def isAllowed(self, triggerType, event):
        return triggerType in [TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_RICOCHET, TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED] and self.getVar() == event.get('targetId')

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_RICOCHET, TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_NOT_PIERCED]

    def isOn(self, stateFlag):
        result = True
        if result:
            self._count += 1
            LOG_DEBUG('Player shot no damage', self._count)
            if self._count < self._maxCount:
                result = False
        return result and stateFlag


class ShotDamageTrigger(_DispatchableTrigger):

    def __init__(self, triggerID, validateVarID, setVarID = None, stateFlagID = None, maxCount = 1):
        super(ShotDamageTrigger, self).__init__(triggerID, validateVarID, setVarID)
        self._count = 0
        self._maxCount = maxCount

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_MADE_NONFATAL_DAMAGE and self.getVar() == event.get('targetId')

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.PLAYER_SHOT_MADE_NONFATAL_DAMAGE]

    def isOn(self, stateFlag):
        result = True
        if result:
            self._count += 1
            LOG_DEBUG('Player shot damage', self._count)
            if self._count < self._maxCount:
                result = False
        return result and stateFlag


class SniperModeTrigger(_DispatchableTrigger):

    def __init__(self, triggerID, stateFlagID = None):
        super(SniperModeTrigger, self).__init__(triggerID, None, setVarID=None, stateFlagID=stateFlagID)
        return

    def isAllowed(self, triggerType, event):
        return triggerType is TriggersManager.TRIGGER_TYPE.SNIPER_MODE

    def getAllowed(self):
        return [TriggersManager.TRIGGER_TYPE.SNIPER_MODE]


class TriggersDispatcher(Trigger, TriggersManager.ITriggerListener):

    def __init__(self, triggerID, triggerIDs):
        super(TriggersDispatcher, self).__init__(triggerID)
        self._triggerIDs = triggerIDs
        self._types = set()

    def run(self):
        self.isRunning = True
        arena = getattr(BigWorld.player(), 'arena', None)
        if not self.isSubscribed:
            if arena is not None:
                arena.onPeriodChange += self.__arena_onPeriodChange
        self.isSubscribed = True
        getter = self._data.getTrigger
        for triggerID in self._triggerIDs:
            trigger = getter(triggerID)
            if trigger is not None:
                self._types.update(trigger.getAllowed())
                trigger.resolveState()
            else:
                LOG_ERROR('Trigger not found', triggerID)

        manager = TriggersManager.g_manager
        if manager is not None:
            manager.addListener(self)
        self.isRunning = not (arena is not None and arena.period is ARENA_PERIOD.BATTLE)
        return

    def clear(self):
        super(TriggersDispatcher, self).clear()
        if self.isSubscribed:
            manager = TriggersManager.g_manager
            if manager is not None and manager.isEnabled():
                manager.delListener(self)
            arena = getattr(BigWorld.player(), 'arena', None)
            if arena is not None:
                arena.onPeriodChange -= self.__arena_onPeriodChange
            self.isSubscribed = False
        self._triggerIDs = set()
        self._types = set()
        return

    def toggle(self, isOn = True, event = None, **kwargs):
        if event is None:
            event = {}
        eventType = event.get('type')
        if eventType not in self._types:
            return
        else:
            getter = self._data.getTrigger
            for triggerID in self._triggerIDs:
                trigger = getter(triggerID)
                if trigger is not None and trigger.isAllowed(eventType, event):
                    LOG_DEBUG('TriggersDispatcher.toggle', isOn, event)
                    triggerIsOn = trigger.isOn(isOn)
                    if triggerIsOn is isOn:
                        trigger.toggle(isOn=isOn)

            return

    def onTriggerDeactivated(self, event):
        self.toggle(isOn=False, event=event)

    def onTriggerActivated(self, event):
        self.toggle(isOn=True, event=event)

    def __arena_onPeriodChange(self, period, *args):
        if period is ARENA_PERIOD.BATTLE:
            self.isRunning = False
        elif period is ARENA_PERIOD.AFTERBATTLE:
            self.clear()
        else:
            self.isRunning = True
