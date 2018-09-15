# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/ammo_ctrl.py
import weakref
from collections import namedtuple, defaultdict
import BigWorld
import CommandMapping
from functools import partial
import Event
from constants import VEHICLE_SETTING
from debug_utils import LOG_CODEPOINT_WARNING, LOG_ERROR, LOG_DEBUG
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import SHELL_SET_RESULT, CANT_SHOOT_ERROR, BATTLE_CTRL_ID, GUN_RELOADING_VALUE_TYPE, SHELL_QUANTITY_UNKNOWN
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.utils.MethodsRules import MethodsRules
from gui.shared.utils.decorators import ReprInjector
from items import vehicles
from math import fabs
import traceback
import BattleReplay
__all__ = ('AmmoController', 'AmmoReplayPlayer')
_ClipBurstSettings = namedtuple('_ClipBurstSettings', 'size interval')

class _GunSettings(namedtuple('_GunSettings', 'clip burst shots reloadEffect')):

    @classmethod
    def default(cls):
        return cls.__new__(cls, _ClipBurstSettings(1, 0.0), _ClipBurstSettings(1, 0.0), {}, None)

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

        return cls.__new__(cls, clip, burst, shots, reloadEffect)

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


class IGunReloadingSnapshot(object):
    """Interface declares immutable state of reloading in a certain time"""
    __slots__ = ()

    def clear(self):
        """Clears data."""
        raise NotImplementedError

    def getValueType(self):
        """ Gets type of values that determine state of reloading: time, percent.
        :return: one of GUN_RELOADING_VALUE_TYPE.*.
        """
        raise NotImplementedError

    def isReloading(self):
        """Is gun still reloading.
        :return: bool.
        """
        raise NotImplementedError

    def getActualValue(self):
        """Gets actual value of reloading.
        :return: float.
        """
        raise NotImplementedError


class IGunReloadingState(IGunReloadingSnapshot):
    """Interface declares the state of reloading that can be update."""
    __slots__ = ()

    def getSnapshot(self):
        """Gets immutable state of reloading at time of request.
        :return: object implements IGunReloadingSnapshot.
        """
        raise NotImplementedError


@ReprInjector.simple(('_actualTime', 'actual'), ('_baseTime', 'base'), ('getTimePassed', 'timePassed'), ('isReloading', 'reloading'))
class ReloadingTimeSnapshot(IGunReloadingSnapshot):
    """ The state of reloading is based on time.
    Server sends this time each time when gun reloading time is changed"""
    __slots__ = ('_actualTime', '_baseTime', '_startTime', '_updateTime')

    def __init__(self, actualTime=0.0, baseTime=0.0, startTime=0.0, updateTime=0.0):
        super(ReloadingTimeSnapshot, self).__init__()
        self._actualTime = actualTime
        self._baseTime = baseTime
        self._startTime = startTime
        self._updateTime = updateTime

    def clear(self):
        self._actualTime = 0.0
        self._baseTime = 0.0
        self._startTime = 0.0
        self._updateTime = 0.0

    def getValueType(self):
        return GUN_RELOADING_VALUE_TYPE.TIME

    def isReloading(self):
        return self._actualTime != 0

    def getActualValue(self):
        return self._actualTime

    def getBaseValue(self):
        return self._baseTime

    def getTimePassed(self):
        """
        Returns time passed from start of reloading till current moment,
        ignoring setGunReloadTime updates(e.g intuition perk was applied or
        vehicle received crits, moves from one cell to another - in all these cases
        server will send updates for actual/base time)
        :return: int value
        """
        return self.__getTimePassedFrom(self._startTime)

    def getTimeLeft(self):
        """
        Return time left, considering _updateTime(the last update of actual/base time)
        :return: int value
        """
        return max(0.0, self._actualTime - self.__getTimePassedFrom(self._updateTime)) if self.isReloading() else 0.0

    def __getTimePassedFrom(self, specifiedTime):
        return max(0.0, BigWorld.timeExact() - specifiedTime) if self.isReloading() and self._actualTime else 0.0


_TIME_CORRECTION_THRESHOLD = 0.01

class ReloadingTimeState(ReloadingTimeSnapshot, IGunReloadingState):
    __slots__ = ('_startTime', '_baseTime', '_actualTime')

    def getSnapshot(self):
        return ReloadingTimeSnapshot(actualTime=self._actualTime, baseTime=self._baseTime, startTime=self._startTime, updateTime=self._updateTime)

    def setTimes(self, actualTime, baseTime):
        """ Sets new values of state.
        :param actualTime: float containing current time of gun reloading. Value can be:
            0 - reloading is completed.
            -1 - reloading is not completed, because there are no ammo or we disable reloading.
            0..n - start to reload at specified time.
        :param baseTime: float containing base time of gun reloading.
            N seconds that are needed to reload gun after shoot.
        """
        if actualTime > 0:
            if self._actualTime <= 0:
                correction = baseTime - actualTime
                if correction > _TIME_CORRECTION_THRESHOLD:
                    self._startTime = BigWorld.timeExact() - correction
                else:
                    self._startTime = BigWorld.timeExact()
            self._updateTime = BigWorld.timeExact()
        else:
            self._startTime = 0.0
            self._updateTime = 0.0
        self._actualTime = actualTime
        self._baseTime = baseTime


_BASE_PERCENT = 1.0

@ReprInjector.simple(('getActualValue', 'actual'), ('isReloading', 'reloading'))
class ReloadingPercentSnapshot(IGunReloadingSnapshot):
    """ The state of reloading is based on percent. It is used in replay."""
    __slots__ = ('__percent',)

    def __init__(self, percent=0.0):
        super(ReloadingPercentSnapshot, self).__init__()
        self.__percent = percent

    def clear(self):
        self.__percent = 0.0

    def getValueType(self):
        return GUN_RELOADING_VALUE_TYPE.PERCENT

    def getActualValue(self):
        return self.__percent

    def getBaseValue(self):
        return _BASE_PERCENT

    def isReloading(self):
        return self.getActualValue() > 0


class ReloadingPercentState(IGunReloadingState):
    __slots__ = ('__turretIndex', '__getter')

    def __init__(self, turretIndex, getter=None):
        super(ReloadingPercentState, self).__init__()
        if getter is None:

            def getter(turretIndex):
                pass

        self.__turretIndex = turretIndex
        self.__getter = getter
        return

    def clear(self):

        def getter(turretIndex):
            pass

        self.__getter = getter

    def getSnapshot(self):
        return ReloadingPercentSnapshot(percent=self.getActualValue())

    def getValueType(self):
        return GUN_RELOADING_VALUE_TYPE.PERCENT

    def getActualValue(self):
        return round(100.0 * self.__getter(self.__turretIndex))

    def isReloading(self):
        return self.getActualValue() > 0


_IGNORED_RELOADING_TIME = 0.15

class _AutoShootsCtrl(object):
    """ Reloading indicator is updated until player holds mouse button
    and value of reloading less than _IGNORED_RELOADING_TIME.
    """
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

    def process(self, timeLeft, prevTimeLeft, turretIndex):
        result = self.__isStarted
        if self.__isStarted:
            self.__clearCallback()
            if not timeLeft:
                self.__setCallback(_IGNORED_RELOADING_TIME + 0.01, turretIndex)
            if timeLeft >= _IGNORED_RELOADING_TIME:
                self.__isStarted = result = False
        elif 0 < timeLeft < _IGNORED_RELOADING_TIME:
            if prevTimeLeft == -1:
                self.__isStarted = result = True
            elif prevTimeLeft == 0:
                result = True
        return result

    def __setCallback(self, reloadTime, turretIndex):
        self.__callbackID = BigWorld.callback(reloadTime + 0.01, partial(self.__update, turretIndex))

    def __clearCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __update(self, turretIndex):
        self.__callbackID = None
        if self.__proxy:
            self.__isStarted = False
            self.__proxy.refreshGunReloading(turretIndex)
        return


class AmmoController(MethodsRules, IBattleController):
    __slots__ = ('__eManager', 'onShellsAdded', 'onSubShellsAdded', 'onShellsUpdated', 'onNextShellChanged', 'onCurrentShellChanged', 'onGunSettingsListSet', 'onGunReloadTimeSet', '__ammo', '__subAmmo', '_order', '__currShellCD', '__currSubShellCD', '__nextShellCD', '__gunSettings', '_reloadingState', '__autoShoots', '__weakref__')

    def __init__(self, reloadingState=None):
        super(AmmoController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onShellsAdded = Event.Event(self.__eManager)
        self.onSubShellsAdded = Event.Event(self.__eManager)
        self.onShellsUpdated = Event.Event(self.__eManager)
        self.onNextShellChanged = Event.Event(self.__eManager)
        self.onCurrentShellChanged = Event.Event(self.__eManager)
        self.onGunSettingsListSet = Event.Event(self.__eManager)
        self.onGunReloadTimeSet = Event.Event(self.__eManager)
        self.__ammo = {}
        self.__subAmmo = defaultdict(dict)
        self._order = []
        self._reloadingState = [reloadingState or ReloadingTimeState()]
        self.__currShellCD = None
        self.__currSubShellCD = defaultdict(dict)
        self.__nextShellCD = None
        self.__gunSettings = [_GunSettings.default()]
        self.__autoShoots = _AutoShootsCtrl(weakref.proxy(self))
        return

    def __repr__(self):
        return '{0:>s}(ammo = {1!r:s}, current = {2!r:s}, next = {3!r:s}, gun = {4!r:s})'.format(self.__class__.__name__, self.__ammo, self.__subAmmo, self.__currShellCD, self.__currSubShellCD, self.__nextShellCD, self.__gunSettings[0])

    def getSubGunsCount(self):
        return len(self.__gunSettings[1:]) if len(self.__gunSettings) > 1 else 0

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
        self.__subAmmo.clear()
        self._order = []
        self.__currShellCD = None
        self.__currSubShellCD = {}
        self.__nextShellCD = None
        reloadEffects = []
        for gunSetting in self.__gunSettings:
            reloadEffects.append(gunSetting.reloadEffect)
            if gunSetting.reloadEffect is not None:
                gunSetting.reloadEffect.stop()

        self.__gunSettings = [ _GunSettings.default() for i in self.__gunSettings[:] ]
        for reloadState in self._reloadingState:
            reloadState.clear()

        self.__autoShoots.destroy()
        return

    def getGunSettings(self, turretIndex):
        return self.__gunSettings[turretIndex]

    def getGunSettingsList(self):
        return self.__gunSettings

    @MethodsRules.delayable()
    def setGunSettings(self, guns):
        self.__gunSettings = []
        for gun in guns:
            self.__gunSettings.append(_GunSettings.make(gun))

        self.setReloadingStates()
        self.onGunSettingsListSet(self.__gunSettings)

    def setReloadingStates(self):
        for i in xrange(len(self._reloadingState)):
            self._reloadingState[i] = type(self._reloadingState[i])()

        reloadingStateLength = len(self._reloadingState)
        gunSettingsLength = len(self.__gunSettings)
        if reloadingStateLength == 0 and gunSettingsLength != 0:
            self._reloadingState.append(ReloadingTimeState())
        while len(self._reloadingState) < len(self.__gunSettings):
            self._reloadingState.append(type(self._reloadingState[0])())

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
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as next.', intCD, self.__ammo)
        return result

    def getCurrentShellCD(self, turretIndex):
        if turretIndex == 0:
            return self.__currShellCD
        else:
            return self.__currSubShellCD[turretIndex] if len(self.__currSubShellCD) >= turretIndex else None

    @MethodsRules.delayable('setShells')
    def setCurrentShellCD(self, intCD):
        result = False
        if intCD in self.__ammo:
            if self.__currShellCD != intCD:
                self.__currShellCD = intCD
                self.onCurrentShellChanged(intCD)
                result = True
        else:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as current.', intCD)
        return result

    @MethodsRules.delayable('setSubShells')
    def setCurrentSubShellCD(self, intCD, turretIndex):
        result = False
        if intCD in self.__subAmmo[turretIndex]:
            if self.__currSubShellCD[turretIndex] != intCD:
                self.__currSubShellCD[turretIndex] = intCD
                result = True
        else:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as current.', intCD)
        return result

    @MethodsRules.delayable('setCurrentShellCD')
    def setGunReloadTime(self, gunIdX, timeLeft, baseTime):
        self.triggerReloadEffect(gunIdX, timeLeft, baseTime)
        interval = self.__gunSettings[gunIdX].clip.interval
        shellCD = self.getCurrentShellCD(gunIdX)
        if interval > 0:
            clipIndex = 1
            if gunIdX == 0:
                amountLeftInClip = self.__ammo[shellCD][clipIndex]
            else:
                amountLeftInClip = self.__subAmmo[gunIdX][shellCD][clipIndex]
            if not (amountLeftInClip == 1 and timeLeft == 0 or amountLeftInClip == 0 and timeLeft > 0):
                baseTime = interval
        isIgnored = False
        if CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT):
            isIgnored = self.__autoShoots.process(timeLeft, self._reloadingState[gunIdX].getActualValue(), gunIdX)
        else:
            self.__autoShoots.reset()
        self._reloadingState[gunIdX].setTimes(timeLeft, baseTime)
        if not isIgnored:
            self.onGunReloadTimeSet(gunIdX, shellCD, self._reloadingState[gunIdX].getSnapshot())

    def triggerReloadEffect(self, gunIndex, timeLeft, baseTime):
        if timeLeft > 0.0 and self.__gunSettings[gunIndex].reloadEffect is not None:
            shellCD = self.getCurrentShellCD(gunIndex)
            if gunIndex == 0:
                shellCounts = self.__ammo[shellCD]
            else:
                shellCounts = self.__subAmmo[gunIndex][shellCD]
            clipCapacity = self.__gunSettings[gunIndex].clip.size
            ammoLow = False
            totalAmmoCount = shellCounts[0]
            if clipCapacity > totalAmmoCount:
                ammoLow = True
                clipCapacity = totalAmmoCount
            reloadStart = fabs(timeLeft - baseTime) < 0.001
            self.__gunSettings[gunIndex].reloadEffect.start(timeLeft, ammoLow, shellCounts[1], clipCapacity, shellCD, reloadStart)
        return

    def getGunReloadingState(self, turretIndex):
        """ Gets snapshot of reloading state.
        :return: instance of object that implements IGunReloadingSnapshot.
        """
        return self._reloadingState[turretIndex].getSnapshot()

    def isGunReloading(self, turretIndex):
        """ Is gun reloading.
        :return: bool.
        """
        return self._reloadingState[turretIndex].isReloading()

    @MethodsRules.delayable('setGunReloadTime')
    def refreshGunReloading(self, turretIndex):
        """Refreshes current state of reloading."""
        self.onGunReloadTimeSet(turretIndex, self.getCurrentShellCD(turretIndex), self._reloadingState[turretIndex].getSnapshot())

    def getShells(self, intCD, turretIndex=0):
        """Gets quantity of shells by compact descriptor.
        :param intCD: integer containing compact descriptor of shell.
        :return: tuple(quantity, quantityInClip) or (-1, -1) if shells is not found.
        """
        try:
            quantity, quantityInClip = self.__ammo[intCD] if turretIndex == 0 else self.__subAmmo[turretIndex][intCD]
        except KeyError:
            LOG_ERROR('Shell is not found.', intCD)
            quantity, quantityInClip = (SHELL_QUANTITY_UNKNOWN,) * 2

        return (quantity, quantityInClip)

    def getOrderedShellsLayout(self):
        """Gets list of shell.
        :return: list( (intCD, descriptor, quantity, quantityInClip, gunSettings)), ... ).
        """
        result = []
        for intCD in self._order:
            descriptor = vehicles.getItemByCompactDescr(intCD)
            quantity, quantityInClip = self.__ammo[intCD]
            turretIndex = 0
            result.append((intCD,
             descriptor,
             quantity,
             quantityInClip,
             self.__gunSettings[turretIndex]))

        return result

    def getShellsLayout(self):
        """Gets list of shell (it's not sorted by adding time).
        :return: list( (intCD, (quantity, quantityInClip)), ... ).
        """
        return self.__ammo.iteritems()

    def getCurrentShells(self, turretIndex):
        """Gets quantity of current shells.
        :return: tuple(quantity, quantityInClip) or (-1, -1) if shells is not found.
        """
        shellCD = self.getCurrentShellCD(turretIndex)
        return self.getShells(shellCD, turretIndex) if shellCD is not None else (SHELL_QUANTITY_UNKNOWN,) * 2

    def getShellsQuantityLeft(self, turretIndex):
        """Gets quantity of shells that are left before to next clip reloading.
        :return: integer containing quantity of clip.
        """
        quantity, quantityInClip = self.getCurrentShells(turretIndex)
        if self.__gunSettings[turretIndex].isCassetteClip():
            result = quantityInClip
            if result == 0 and not self._reloadingState[turretIndex].isReloading():
                clipSize = self.__gunSettings[turretIndex].clip.size
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
            turretIndex = 0
            self.onShellsAdded(intCD, descriptor, quantity, quantityInClip, self.__gunSettings[turretIndex])
        return result

    @MethodsRules.delayable('setGunSettings')
    def setSubShells(self, intCD, quantity, quantityInClip, gunIdX):
        result = SHELL_SET_RESULT.UNDEFINED
        if intCD in self.__subAmmo[gunIdX]:
            prevAmmo = self.__subAmmo[gunIdX][intCD]
            self.__subAmmo[gunIdX][intCD] = (quantity, quantityInClip)
            result |= SHELL_SET_RESULT.UPDATED
            if intCD == self.__currSubShellCD[gunIdX]:
                result |= SHELL_SET_RESULT.CURRENT
                if quantityInClip > 0 and prevAmmo[1] == 0 and quantity == prevAmmo[0]:
                    result |= SHELL_SET_RESULT.CASSETTE_RELOAD
        else:
            self.__subAmmo[gunIdX][intCD] = (quantity, quantityInClip)
            self._order.append(intCD)
            result |= SHELL_SET_RESULT.ADDED
            descriptor = vehicles.getItemByCompactDescr(intCD)
            self.onSubShellsAdded(intCD, descriptor, quantity, quantityInClip, self.__gunSettings[gunIdX])
        return result

    def getNextSettingCode(self, intCD):
        code = None
        if intCD == self.__currShellCD and intCD == self.__nextShellCD:
            return code
        elif intCD not in self.__ammo.keys():
            LOG_ERROR('Shell is not found.', intCD)
            return code
        else:
            quantity, _ = self.__ammo[intCD]
            if quantity <= 0:
                return code
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
            turretIndex = 0
            avatar_getter.updateVehicleSetting(code, intCD, turretIndex, avatar)
            if avatar_getter.isPlayerOnArena(avatar):
                avatar_getter.changeVehicleSetting(code, intCD, avatar)
            return True

    def reloadPartialClip(self, avatar=None):
        turretIndex = 0
        clipSize = self.__gunSettings[turretIndex].clip.size
        if clipSize > 1 and self.__currShellCD in self.__ammo:
            quantity, quantityInClip = self.__ammo[self.__currShellCD]
            if quantity != 0 and (quantityInClip < clipSize or self.__nextShellCD != self.__currShellCD):
                avatar_getter.changeVehicleSetting(VEHICLE_SETTING.RELOAD_PARTIAL_CLIP, 0, avatar)

    def useLoaderIntuition(self):
        quantity, _ = self.__ammo[self.__currShellCD]
        turretIndex = 0
        clipSize = self.__gunSettings[turretIndex].clip.size
        if clipSize > 0 and not self.isGunReloading(turretIndex):
            for _cd, (_quantity, _) in self.__ammo.iteritems():
                self.__ammo[_cd] = (_quantity, 0)

            quantityInClip = clipSize if quantity >= clipSize else quantity
            self.setShells(self.__currShellCD, quantity, quantityInClip)

    def canShoot(self, turretIndex=0):
        totalQuantity, quantityInClip = self.getCurrentShells(turretIndex)
        if totalQuantity == SHELL_QUANTITY_UNKNOWN:
            result, error = False, CANT_SHOOT_ERROR.WAITING
        elif totalQuantity == 0:
            result, error = False, CANT_SHOOT_ERROR.NO_AMMO
        elif self.isGunReloading(turretIndex):
            result, error = False, CANT_SHOOT_ERROR.RELOADING
        else:
            result, error = True, CANT_SHOOT_ERROR.UNDEFINED
        return (result, error)


class AmmoReplayRecorder(AmmoController):
    __slots__ = ('__changeRecord', '__timeRecord', '__replayCtrl')

    def __init__(self, replayCtrl):
        super(AmmoReplayRecorder, self).__init__()
        self.__replayCtrl = replayCtrl
        self.__changeRecord = replayCtrl.setAmmoSetting
        self.__timeRecord = replayCtrl.setGunReloadTime

    def clear(self, leave=True):
        super(AmmoReplayRecorder, self).clear(leave)
        if leave:
            self.__changeRecord = None
            self.__timeRecord = None
            self.__replayCtrl = None
        return

    def setGunReloadTime(self, gunIdX, timeLeft, baseTime):
        if self.__timeRecord is not None:
            if timeLeft < 0:
                self.__timeRecord(gunIdX, 0, -1)
            else:
                startTime = baseTime - timeLeft
                self.__timeRecord(gunIdX, startTime, baseTime)
        super(AmmoReplayRecorder, self).setGunReloadTime(gunIdX, timeLeft, baseTime)
        return

    def changeSetting(self, intCD, avatar=None):
        changed = super(AmmoReplayRecorder, self).changeSetting(intCD, avatar)
        if changed and intCD in self._order:
            if self.__changeRecord is not None:
                self.__changeRecord(self._order.index(intCD))
        return changed


class AmmoReplayPlayer(AmmoController):
    __slots__ = ('__callbackID', '__isActivated', '__timeGetter', '__percents', '__replayCtrl')

    def __init__(self, replayCtrl):
        self.__replayCtrl = replayCtrl
        super(AmmoReplayPlayer, self).__init__(reloadingState=ReloadingPercentState(turretIndex=0, getter=replayCtrl.getGunReloadAmountLeft))
        self.__callbackID = None
        self.__isActivated = False
        self.__percents = None
        self.__replayCtrl.onAmmoSettingChanged += self.__onAmmoSettingChanged
        return

    def setReloadingStates(self):
        self._reloadingState = []
        for i in xrange(self.getSubGunsCount() + 1):
            self._reloadingState.append(ReloadingPercentState(turretIndex=i, getter=self.__replayCtrl.getGunReloadAmountLeft))

    def clear(self, leave=True):
        if leave and self.__replayCtrl is not None:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            self.__timeGetter = lambda : 0
            if self.__replayCtrl is not None:
                self.__replayCtrl.onAmmoSettingChanged -= self.__onAmmoSettingChanged
                self.__replayCtrl = None
        super(AmmoReplayPlayer, self).clear(leave)
        return

    def setGunReloadTime(self, gunIdX, timeLeft, baseTime):
        self.__percents = None
        self.triggerReloadEffect(gunIdX, timeLeft, baseTime)
        if not self.__isActivated:
            self.__isActivated = True
            self.__timeLoop()
        return

    def changeSetting(self, intCD, avatar=None):
        return False

    def __timeLoop(self):
        self.__callbackID = None
        self.__tick()
        self.__callbackID = BigWorld.callback(0.1, self.__timeLoop)
        return

    def __tick(self):
        if self.__percents is None or len(self.__percents) != len(self._reloadingState):
            self.__percents = [ 0.0 for i in xrange(len(self._reloadingState)) ]
        for turretIndex, state in enumerate(self._reloadingState):
            percent = state.getActualValue()
            if self.__percents[turretIndex] != percent:
                self.__percents[turretIndex] = percent
                self.onGunReloadTimeSet(turretIndex, self.getCurrentShellCD(turretIndex), state.getSnapshot())

        return

    @MethodsRules.delayable('setShells')
    def __onAmmoSettingChanged(self, shellIndex):
        if shellIndex >= len(self._order) or shellIndex < 0:
            return
        else:
            intCD = self._order[shellIndex]
            code = self.getNextSettingCode(intCD)
            if code is not None:
                turretIndex = 0
                avatar_getter.updateVehicleSetting(code, intCD, turretIndex)
            return
