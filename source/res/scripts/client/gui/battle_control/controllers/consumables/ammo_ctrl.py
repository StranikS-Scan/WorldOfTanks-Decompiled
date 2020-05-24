# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/ammo_ctrl.py
import weakref
from collections import namedtuple
from math import fabs
import BigWorld
import CommandMapping
import Event
from constants import VEHICLE_SETTING
from debug_utils import LOG_CODEPOINT_WARNING, LOG_ERROR
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import SHELL_SET_RESULT, CANT_SHOOT_ERROR, BATTLE_CTRL_ID, SHELL_QUANTITY_UNKNOWN
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.utils.MethodsRules import MethodsRules
from gui.shared.utils.decorators import ReprInjector
from ReloadEffect import DualGunReload
from items import vehicles
__all__ = ('AmmoController', 'AmmoReplayPlayer')
_ClipBurstSettings = namedtuple('_ClipBurstSettings', 'size interval')
_HUNDRED_PERCENT = 100.0

class _GunSettings(namedtuple('_GunSettings', 'clip burst shots reloadEffect autoReload')):

    @classmethod
    def default(cls):
        return cls.__new__(cls, _ClipBurstSettings(1, 0.0), _ClipBurstSettings(1, 0.0), {}, None, None)

    @classmethod
    def make(cls, gun):
        clip = _ClipBurstSettings(*gun.clip)
        burst = _ClipBurstSettings(*gun.burst)
        shots = {}
        reloadEffect = None
        reloadEffectDesc = gun.reloadEffect
        if reloadEffectDesc is not None:
            reloadEffect = reloadEffectDesc.create()
        for shotIdx, shotDescr in enumerate(gun.shots):
            nationID, itemID = shotDescr.shell.id
            intCD = vehicles.makeIntCompactDescrByID('shell', nationID, itemID)
            shots[intCD] = (shotIdx, shotDescr.piercingPower[0])

        autoReload = gun.autoreload if 'autoreload' in gun.tags else None
        return cls.__new__(cls, clip, burst, shots, reloadEffect, autoReload)

    def getShotIndex(self, intCD):
        if intCD in self.shots:
            index = self.shots[intCD][0]
        else:
            index = -1
        return index

    def getPiercingPower(self, intCD):
        if intCD in self.shots:
            power = self.shots[intCD][1]
        else:
            power = 0
        return power

    def isCassetteClip(self):
        return self.clip.size > 1 or self.burst.size > 1

    def hasAutoReload(self):
        return self.autoReload is not None


class IGunReloadingSnapshot(object):
    __slots__ = ()

    def clear(self):
        raise NotImplementedError

    def isReloading(self):
        raise NotImplementedError

    def getActualValue(self):
        raise NotImplementedError

    def getBaseValue(self):
        raise NotImplementedError

    def isReloadingFinished(self):
        raise NotImplementedError


class IGunReloadingState(IGunReloadingSnapshot):
    __slots__ = ()

    def getSnapshot(self):
        raise NotImplementedError

    def startPredictedReloading(self):
        raise NotImplementedError

    def stopPredicateReloading(self):
        raise NotImplementedError


@ReprInjector.simple(('_actualTime', 'actual'), ('_baseTime', 'base'), ('getTimePassed', 'timePassed'), ('isReloading', 'reloading'))
class ReloadingTimeSnapshot(IGunReloadingSnapshot):
    __slots__ = ('_actualTime', '_baseTime', '_startTime', '_updateTime', '_waitReloadingStartResponse')

    def __init__(self, actualTime=0.0, baseTime=0.0, startTime=0.0, updateTime=0.0, waitReloadingStartResponse=False):
        super(ReloadingTimeSnapshot, self).__init__()
        self._actualTime = actualTime
        self._baseTime = baseTime
        self._startTime = startTime
        self._updateTime = updateTime
        self._waitReloadingStartResponse = waitReloadingStartResponse

    def clear(self):
        self._actualTime = 0.0
        self._baseTime = 0.0
        self._startTime = 0.0
        self._updateTime = 0.0
        self._waitReloadingStartResponse = False

    def isReloading(self):
        return True if self._waitReloadingStartResponse else self._actualTime > 0

    def isReloadingFinished(self):
        return False if self._waitReloadingStartResponse else self._actualTime == 0

    def getActualValue(self):
        return self._actualTime

    def getBaseValue(self):
        return self._baseTime

    def getTimePassed(self):
        return self.__getTimePassedFrom(self._startTime)

    def getTimeLeft(self):
        return max(0.0, self._actualTime - self.__getTimePassedFrom(self._updateTime)) if not self.isReloadingFinished() else 0.0

    def __getTimePassedFrom(self, specifiedTime):
        return max(0.0, BigWorld.timeExact() - specifiedTime) if not self.isReloadingFinished() else 0.0


_TIME_CORRECTION_THRESHOLD = 0.01

class ReloadingTimeState(ReloadingTimeSnapshot, IGunReloadingState):
    __slots__ = ('_startTime', '_baseTime', '_actualTime', '_updateTime', '_waitReloadingStartResponse')

    def getSnapshot(self):
        return ReloadingTimeSnapshot(actualTime=self._actualTime, baseTime=self._baseTime, startTime=self._startTime, updateTime=self._updateTime, waitReloadingStartResponse=self._waitReloadingStartResponse)

    def startPredictedReloading(self):
        self._waitReloadingStartResponse = True

    def stopPredicateReloading(self):
        self._waitReloadingStartResponse = False

    def setTimes(self, actualTime, baseTime):
        if actualTime > 0:
            correction = baseTime - actualTime
            if correction > _TIME_CORRECTION_THRESHOLD:
                self._startTime = BigWorld.timeExact() - correction
            else:
                self._startTime = BigWorld.timeExact()
            self._updateTime = BigWorld.timeExact()
        else:
            self._startTime = 0.0
            self._updateTime = 0.0
        if actualTime == 0:
            self.stopPredicateReloading()
        self._actualTime = actualTime
        self._baseTime = baseTime


_IGNORED_RELOADING_TIME = 0.15

class _AutoShootsCtrl(object):
    __slots__ = ('__proxy', '__isStarted', '__callbackID')

    def __init__(self, proxy):
        super(_AutoShootsCtrl, self).__init__()
        self.__proxy = proxy
        self.__isStarted = False
        self.__callbackID = None
        return

    def destroy(self):
        self.reset()
        self.__proxy = None
        return

    def reset(self):
        self.__clearCallback()
        self.__isStarted = False

    def process(self, timeLeft, prevTimeLeft):
        result = self.__isStarted
        if self.__isStarted:
            self.__clearCallback()
            if not timeLeft:
                self.__setCallback(_IGNORED_RELOADING_TIME + 0.01)
            if timeLeft >= _IGNORED_RELOADING_TIME:
                self.__isStarted = result = False
        elif 0 < timeLeft < _IGNORED_RELOADING_TIME:
            if prevTimeLeft == -1:
                self.__isStarted = result = True
            elif prevTimeLeft == 0:
                result = True
        return result

    def __setCallback(self, reloadTime):
        self.__callbackID = BigWorld.callback(reloadTime + 0.01, self.__update)

    def __clearCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __update(self):
        self.__callbackID = None
        if self.__proxy:
            self.__isStarted = False
            self.__proxy.refreshGunReloading()
        return


class AmmoController(MethodsRules, IBattleController):
    __slots__ = ('__eManager', 'onShellsAdded', 'onShellsUpdated', 'onNextShellChanged', 'onCurrentShellChanged', 'onGunSettingsSet', 'onGunReloadTimeSet', 'onGunAutoReloadTimeSet', '__ammo', '_order', '__currShellCD', '__nextShellCD', '__gunSettings', '_reloadingState', '_autoReloadingState', '__autoShoots', '__weakref__', 'onDebuffStarted')

    def __init__(self, reloadingState=None):
        super(AmmoController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onShellsAdded = Event.Event(self.__eManager)
        self.onShellsUpdated = Event.Event(self.__eManager)
        self.onNextShellChanged = Event.Event(self.__eManager)
        self.onCurrentShellChanged = Event.Event(self.__eManager)
        self.onGunSettingsSet = Event.Event(self.__eManager)
        self.onGunReloadTimeSet = Event.Event(self.__eManager)
        self.onDebuffStarted = Event.Event(self.__eManager)
        self.onGunAutoReloadTimeSet = Event.Event(self.__eManager)
        self.__ammo = {}
        self._order = []
        self._reloadingState = reloadingState or ReloadingTimeState()
        self._autoReloadingState = ReloadingTimeState()
        self.__currShellCD = None
        self.__nextShellCD = None
        self.__gunSettings = _GunSettings.default()
        self.__autoShoots = _AutoShootsCtrl(weakref.proxy(self))
        return

    def __repr__(self):
        return '{0:>s}(ammo = {1!r:s}, current = {2!r:s}, next = {3!r:s}, gun = {4!r:s})'.format(self.__class__.__name__, self.__ammo, self.__currShellCD, self.__nextShellCD, self.__gunSettings)

    def getControllerID(self):
        return BATTLE_CTRL_ID.AMMO

    def startControl(self):
        pass

    def stopControl(self):
        self.clear(leave=True)

    def clear(self, leave=True):
        super(AmmoController, self).clear()
        if leave:
            self.__eManager.clear()
        self.__ammo.clear()
        self._order = []
        self.__currShellCD = None
        self.__nextShellCD = None
        reloadEffect = self.__gunSettings.reloadEffect
        if reloadEffect is not None:
            reloadEffect.stop()
        self.__gunSettings = _GunSettings.default()
        if leave:
            self._reloadingState.clear()
            self.__autoShoots.destroy()
        return

    def getGunSettings(self):
        return self.__gunSettings

    @MethodsRules.delayable()
    def setGunSettings(self, gun):
        self.__gunSettings = _GunSettings.make(gun)
        self.onGunSettingsSet(self.__gunSettings)

    def getNextShellCD(self):
        return self.__nextShellCD

    @MethodsRules.delayable('setShells')
    def setNextShellCD(self, intCD):
        result = False
        if intCD in self.__ammo:
            if self.__nextShellCD != intCD:
                self.__nextShellCD = intCD
                self.onNextShellChanged(intCD)
                result = True
        else:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as next.', intCD)
        return result

    def getCurrentShellCD(self):
        return self.__currShellCD

    @MethodsRules.delayable('setShells')
    def setCurrentShellCD(self, intCD):
        result = False
        if intCD in self.__ammo:
            if self.__currShellCD != intCD:
                self.__currShellCD = intCD
                self._reloadingState.startPredictedReloading()
                self.onCurrentShellChanged(intCD)
                result = True
        else:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as current.', intCD)
        return result

    @MethodsRules.delayable('setCurrentShellCD')
    def setGunReloadTime(self, timeLeft, baseTime):
        interval = self.__gunSettings.clip.interval
        self.triggerReloadEffect(timeLeft, baseTime)
        if interval > 0 and self.__currShellCD in self.__ammo:
            shellsInClip = self.__ammo[self.__currShellCD][1]
            if not (shellsInClip == 1 and timeLeft == 0 and not self.__gunSettings.hasAutoReload() or shellsInClip == 0 and timeLeft != 0):
                baseTime = interval
        isIgnored = False
        if CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT):
            isIgnored = self.__autoShoots.process(timeLeft, self._reloadingState.getActualValue())
        else:
            self.__autoShoots.reset()
        self._reloadingState.setTimes(timeLeft, baseTime)
        if not isIgnored:
            self.onGunReloadTimeSet(self.__currShellCD, self._reloadingState.getSnapshot())

    def setGunAutoReloadTime(self, timeLeft, baseTime, isSlowed):
        self._autoReloadingState.setTimes(timeLeft, baseTime)
        self.__notifyAboutAutoReloadTimeChanges(isSlowed)
        if self.__gunSettings.reloadEffect is not None and self.__currShellCD in self.__ammo:
            shellCounts = self.__ammo[self.__currShellCD]
            shellsInClip = shellCounts[1]
            clipCapacity = self.__gunSettings.clip.size
            canBeFull = shellCounts[0] >= clipCapacity
            lastShell = shellsInClip == clipCapacity - 1
            reloadStart = fabs(timeLeft - baseTime) < 0.001
            if timeLeft > 0.0 and reloadStart:
                self.__gunSettings.reloadEffect.onClipLoad(timeLeft, shellsInClip, lastShell, canBeFull)
            elif self.__gunSettings.clip.size == shellsInClip and not reloadStart:
                self.__gunSettings.reloadEffect.onFull()
        return

    def triggerReloadEffect(self, timeLeft, baseTime, directTrigger=False):
        if timeLeft > 0.0 and self.__gunSettings.reloadEffect is not None and self.__currShellCD in self.__ammo:
            shellCounts = self.__ammo[self.__currShellCD]
            clipCapacity = self.__gunSettings.clip.size
            ammoLow = False
            if clipCapacity > shellCounts[0]:
                ammoLow = True
                clipCapacity = shellCounts[0]
            reloadStart = fabs(timeLeft - baseTime) < 0.001
            if isinstance(self.__gunSettings.reloadEffect, DualGunReload):
                if self.getShellsQuantityLeft() == 1:
                    ammoLow = True
                self.__gunSettings.reloadEffect.start(timeLeft, ammoLow, directTrigger)
            else:
                self.__gunSettings.reloadEffect.start(timeLeft, ammoLow, shellCounts[1], clipCapacity, self.__currShellCD, reloadStart)
        return

    def getGunReloadingState(self):
        return self._reloadingState.getSnapshot()

    def isGunReloading(self):
        return not self._reloadingState.isReloadingFinished()

    @MethodsRules.delayable('setGunReloadTime')
    def refreshGunReloading(self):
        self.onGunReloadTimeSet(self.__currShellCD, self._reloadingState.getSnapshot())

    def getShells(self, intCD):
        try:
            quantity, quantityInClip = self.__ammo[intCD]
        except KeyError:
            LOG_ERROR('Shell is not found.', intCD)
            quantity, quantityInClip = (SHELL_QUANTITY_UNKNOWN,) * 2

        return (quantity, quantityInClip)

    def getOrderedShellsLayout(self):
        result = []
        for intCD in self._order:
            descriptor = vehicles.getItemByCompactDescr(intCD)
            quantity, quantityInClip = self.__ammo[intCD]
            result.append((intCD,
             descriptor,
             quantity,
             quantityInClip,
             self.__gunSettings))

        return result

    def getShellsLayout(self):
        return self.__ammo.iteritems()

    def getCurrentShells(self):
        return self.getShells(self.__currShellCD) if self.__currShellCD is not None else (SHELL_QUANTITY_UNKNOWN,) * 2

    def getShellsQuantityLeft(self):
        quantity, quantityInClip = self.getCurrentShells()
        if self.__gunSettings.isCassetteClip():
            result = quantityInClip
            if result == 0 and self._reloadingState.isReloadingFinished():
                clipSize = self.__gunSettings.clip.size
                if clipSize <= quantity:
                    result = clipSize
                else:
                    result = quantity
            return result
        else:
            return quantity

    @MethodsRules.delayable('setGunSettings')
    def setShells(self, intCD, quantity, quantityInClip):
        result = SHELL_SET_RESULT.UNDEFINED
        if intCD in self.__ammo:
            prevAmmo = self.__ammo[intCD]
            self.__ammo[intCD] = (quantity, quantityInClip)
            result |= SHELL_SET_RESULT.UPDATED
            if intCD == self.__currShellCD:
                result |= SHELL_SET_RESULT.CURRENT
                if quantityInClip > 0 and prevAmmo[1] == 0 and quantity == prevAmmo[0]:
                    result |= SHELL_SET_RESULT.CASSETTE_RELOAD
            self.onShellsUpdated(intCD, quantity, quantityInClip, result)
        else:
            self.__ammo[intCD] = (quantity, quantityInClip)
            self._order.append(intCD)
            result |= SHELL_SET_RESULT.ADDED
            descriptor = vehicles.getItemByCompactDescr(intCD)
            self.onShellsAdded(intCD, descriptor, quantity, quantityInClip, self.__gunSettings)
        return result

    def getNextSettingCode(self, intCD):
        if intCD == self.__currShellCD and intCD == self.__nextShellCD:
            return None
        elif intCD not in self.__ammo.keys():
            LOG_ERROR('Shell is not found.', intCD)
            return None
        else:
            quantity, _ = self.__ammo[intCD]
            if quantity <= 0:
                return None
            if intCD == self.__nextShellCD:
                code = VEHICLE_SETTING.CURRENT_SHELLS
            else:
                code = VEHICLE_SETTING.NEXT_SHELLS
            return code

    def applySettings(self, avatar=None):
        if self.__nextShellCD > 0 and self.__nextShellCD in self.__ammo:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.NEXT_SHELLS, self.__nextShellCD, avatar)
        if self.__currShellCD > 0 and self.__currShellCD in self.__ammo:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.CURRENT_SHELLS, self.__currShellCD, avatar)

    def changeSetting(self, intCD, avatar=None):
        if not avatar_getter.isVehicleAlive(avatar):
            return False
        else:
            code = self.getNextSettingCode(intCD)
            if code is None:
                return False
            avatar_getter.updateVehicleSetting(code, intCD, avatar)
            if avatar_getter.isPlayerOnArena(avatar):
                avatar_getter.changeVehicleSetting(code, intCD, avatar)
            return True

    def reloadPartialClip(self, avatar=None):
        clipSize = self.__gunSettings.clip.size
        if clipSize > 1 and self.__currShellCD in self.__ammo and not self.__gunSettings.hasAutoReload():
            quantity, quantityInClip = self.__ammo[self.__currShellCD]
            if quantity != 0 and (quantityInClip < clipSize or self.__nextShellCD != self.__currShellCD):
                avatar_getter.changeVehicleSetting(VEHICLE_SETTING.RELOAD_PARTIAL_CLIP, 0, avatar)

    def useLoaderIntuition(self):
        if self.__currShellCD in self.__ammo:
            quantity, _ = self.__ammo[self.__currShellCD]
            clipSize = self.__gunSettings.clip.size
            self._reloadingState.stopPredicateReloading()
            if clipSize > 0 and not self.isGunReloading():
                for _cd, (_quantity, _) in self.__ammo.iteritems():
                    self.__ammo[_cd] = (_quantity, 0)

                quantityInClip = clipSize if quantity >= clipSize else quantity
                self.setShells(self.__currShellCD, quantity, quantityInClip)

    def canShoot(self, isRepeat=False):
        if self.__currShellCD is None:
            result, error = False, CANT_SHOOT_ERROR.WAITING
        elif self.__ammo[self.__currShellCD][0] == 0:
            result, error = False, CANT_SHOOT_ERROR.NO_AMMO
        elif self.isGunReloading():
            if not isRepeat and self.__gunSettings.hasAutoReload():
                self.__shotFail()
            result, error = False, CANT_SHOOT_ERROR.RELOADING
        elif self.__ammo[self.__currShellCD][1] == 0 and self.__gunSettings.isCassetteClip():
            result, error = True, CANT_SHOOT_ERROR.EMPTY_CLIP
        else:
            result, error = True, CANT_SHOOT_ERROR.UNDEFINED
        return (result, error)

    def __shotFail(self):
        if self.__gunSettings.reloadEffect is not None and self.__currShellCD in self.__ammo:
            shellCounts = self.__ammo[self.__currShellCD]
            if shellCounts[1] == 0:
                self.__gunSettings.reloadEffect.shotFail()
        return

    def __notifyAboutAutoReloadTimeChanges(self, isSlowed):
        self.onGunAutoReloadTimeSet(self._autoReloadingState.getSnapshot(), isSlowed)


class AmmoReplayRecorder(AmmoController):
    __slots__ = ('__changeRecord', '__timeRecord')

    def __init__(self, replayCtrl):
        super(AmmoReplayRecorder, self).__init__()
        self.__changeRecord = replayCtrl.setAmmoSetting
        self.__timeRecord = replayCtrl.setGunReloadTime

    def clear(self, leave=True):
        super(AmmoReplayRecorder, self).clear(leave)
        if leave:
            self.__changeRecord = None
            self.__timeRecord = None
        return

    def setGunReloadTime(self, timeLeft, baseTime):
        if self.__timeRecord is not None:
            if timeLeft < 0:
                self.__timeRecord(0, -1)
            else:
                startTime = baseTime - timeLeft
                self.__timeRecord(startTime, baseTime)
        super(AmmoReplayRecorder, self).setGunReloadTime(timeLeft, baseTime)
        return

    def changeSetting(self, intCD, avatar=None):
        changed = super(AmmoReplayRecorder, self).changeSetting(intCD, avatar)
        if changed and intCD in self._order:
            if self.__changeRecord is not None:
                self.__changeRecord(self._order.index(intCD))
        return changed


class AmmoReplayPlayer(AmmoController):
    __slots__ = ('__replayCtrl',)

    def __init__(self, replayCtrl):
        super(AmmoReplayPlayer, self).__init__()
        self.__replayCtrl = replayCtrl
        self.__replayCtrl.onAmmoSettingChanged += self.__onAmmoSettingChanged

    def clear(self, leave=True):
        if leave:
            if self.__replayCtrl is not None:
                self.__replayCtrl.onAmmoSettingChanged -= self.__onAmmoSettingChanged
                self.__replayCtrl = None
        super(AmmoReplayPlayer, self).clear(leave)
        return

    def changeSetting(self, intCD, avatar=None):
        return False

    @MethodsRules.delayable('setShells')
    def __onAmmoSettingChanged(self, idx):
        if idx >= len(self._order) or idx < 0:
            return
        else:
            intCD = self._order[idx]
            code = self.getNextSettingCode(intCD)
            if code is not None:
                avatar_getter.updateVehicleSetting(code, intCD)
            return
