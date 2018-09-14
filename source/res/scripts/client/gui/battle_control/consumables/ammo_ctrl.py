# Embedded file name: scripts/client/gui/battle_control/consumables/ammo_ctrl.py
import weakref
from collections import namedtuple
import BigWorld
import CommandMapping
import Event
from constants import VEHICLE_SETTING
from debug_utils import LOG_CODEPOINT_WARNING, LOG_ERROR
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import SHELL_SET_RESULT, CANT_SHOOT_ERROR
from gui.shared.utils.MethodsRules import MethodsRules
from items import vehicles
_ClipBurstSettings = namedtuple('_ClipBurstSettings', 'size interval')

class _GunSettings(namedtuple('_GunSettings', 'clip burst shots reloadEffect')):

    @classmethod
    def default(cls):
        return cls.__new__(cls, _ClipBurstSettings(1, 0.0), _ClipBurstSettings(1, 0.0), {}, None)

    @classmethod
    def make(cls, gun):
        clip = _ClipBurstSettings(*gun['clip'])
        burst = _ClipBurstSettings(*gun['burst'])
        shots = {}
        reloadEffect = None
        reloadEffectDesc = gun.get('reloadEffect', None)
        if reloadEffectDesc is not None:
            reloadEffect = reloadEffectDesc.create()
        for shotIdx, shotDescr in enumerate(gun['shots']):
            nationID, itemID = shotDescr['shell']['id']
            intCD = vehicles.makeIntCompactDescrByID('shell', nationID, itemID)
            shots[intCD] = (shotIdx, shotDescr['piercingPower'][0])

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
            if timeLeft == 0:
                self.__setCallback(_IGNORED_RELOADING_TIME + 0.01)
            if timeLeft < _IGNORED_RELOADING_TIME:
                result = True
            else:
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


class AmmoController(MethodsRules):
    __slots__ = ('__eManager', 'onShellsAdded', 'onShellsUpdated', 'onNextShellChanged', 'onCurrentShellChanged', 'onGunSettingsSet', 'onGunReloadTimeSet', 'onGunReloadTimeSetInPercent', '__ammo', '_order', '__currShellCD', '__nextShellCD', '__gunSettings', '__reloadTime', '__baseTime', '__autoShoots', '__weakref__')

    def __init__(self):
        super(AmmoController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onShellsAdded = Event.Event(self.__eManager)
        self.onShellsUpdated = Event.Event(self.__eManager)
        self.onNextShellChanged = Event.Event(self.__eManager)
        self.onCurrentShellChanged = Event.Event(self.__eManager)
        self.onGunSettingsSet = Event.Event(self.__eManager)
        self.onGunReloadTimeSet = Event.Event(self.__eManager)
        self.onGunReloadTimeSetInPercent = Event.Event(self.__eManager)
        self.__ammo = {}
        self._order = []
        self.__currShellCD = None
        self.__nextShellCD = None
        self.__gunSettings = _GunSettings.default()
        self.__reloadTime = 0.0
        self.__baseTime = 0.0
        self.__autoShoots = _AutoShootsCtrl(weakref.proxy(self))
        return

    def __repr__(self):
        return '{0:>s}(ammo = {1!r:s}, current = {2!r:s}, next = {3!r:s}, gun = {4!r:s})'.format(self.__class__.__name__, self.__ammo, self.__currShellCD, self.__nextShellCD, self.__gunSettings)

    def clear(self, leave = True):
        super(AmmoController, self).clear()
        if leave:
            self.__eManager.clear()
        self.__ammo.clear()
        self._order = []
        self.__currShellCD = None
        self.__nextShellCD = None
        self.__gunSettings = _GunSettings.default()
        self.__reloadTime = 0.0
        self.__baseTime = 0.0
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
                self.onCurrentShellChanged(intCD)
                result = True
        else:
            LOG_CODEPOINT_WARNING('Shell is not found in received list to set as current.', intCD)
        return result

    @MethodsRules.delayable('setCurrentShellCD')
    def setGunReloadTime(self, timeLeft, baseTime):
        interval = self.__gunSettings.clip.interval
        if timeLeft == baseTime and self.__gunSettings.reloadEffect is not None:
            self.__gunSettings.reloadEffect.start(baseTime)
        if interval > 0:
            if self.__ammo[self.__currShellCD][1] != 1:
                baseTime = interval
        isIgnored = False
        if CommandMapping.g_instance.isActive(CommandMapping.CMD_CM_SHOOT):
            isIgnored = self.__autoShoots.process(timeLeft, self.__reloadTime)
        else:
            self.__autoShoots.reset()
        self.__reloadTime = timeLeft
        self.__baseTime = baseTime
        if not isIgnored:
            self.onGunReloadTimeSet(self.__currShellCD, timeLeft, baseTime)
        return

    def getGunReloadTime(self):
        return self.__reloadTime

    def isGunReloadTimeInPercent(self):
        return False

    def isGunReloading(self):
        return self.__reloadTime != 0

    @MethodsRules.delayable('setGunReloadTime')
    def refreshGunReloading(self):
        self.onGunReloadTimeSet(self.__currShellCD, self.__reloadTime, self.__baseTime)

    def getShells(self, intCD):
        try:
            quantity, quantityInClip = self.__ammo[intCD]
        except KeyError:
            LOG_ERROR('Shell is not found.', intCD)
            quantity, quantityInClip = (-1, -1)

        return (quantity, quantityInClip)

    def getShellsLayout(self):
        return self.__ammo.iteritems()

    def getCurrentShells(self):
        return self.getShells(self.__currShellCD)

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
                else:
                    avatar_getter.refreshShotDispersionAngle()
            self.onShellsUpdated(intCD, quantity, quantityInClip, result)
        else:
            self.__ammo[intCD] = (quantity, quantityInClip)
            self._order.append(intCD)
            result |= SHELL_SET_RESULT.ADDED
            descriptor = vehicles.getDictDescr(intCD)
            self.onShellsAdded(intCD, descriptor, quantity, quantityInClip, self.__gunSettings)
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

    def applySettings(self, avatar = None):
        if self.__nextShellCD > 0 and self.__nextShellCD in self.__ammo:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.NEXT_SHELLS, self.__nextShellCD, avatar)
        if self.__currShellCD > 0 and self.__currShellCD in self.__ammo:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.CURRENT_SHELLS, self.__currShellCD, avatar)

    def changeSetting(self, intCD, avatar = None):
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

    def reloadPartialClip(self, avatar = None):
        clipSize = self.__gunSettings.clip.size
        if clipSize > 1 and self.__currShellCD in self.__ammo:
            quantity, quantityInClip = self.__ammo[self.__currShellCD]
            if quantity != 0 and (quantityInClip < clipSize or self.__nextShellCD != self.__currShellCD):
                avatar_getter.changeVehicleSetting(VEHICLE_SETTING.RELOAD_PARTIAL_CLIP, 0, avatar)

    def useLoaderIntuition(self):
        quantity, _ = self.__ammo[self.__currShellCD]
        clipSize = self.__gunSettings.clip.size
        if clipSize > 0 and not self.isGunReloading():
            for _cd, (_quantity, _) in self.__ammo.iteritems():
                self.__ammo[_cd] = (_quantity, 0)

            quantityInClip = clipSize if quantity >= clipSize else quantity
            self.setShells(self.__currShellCD, quantity, quantityInClip)

    def canShoot(self):
        if self.__currShellCD is None:
            result, error = False, CANT_SHOOT_ERROR.WAITING
        elif self.__ammo[self.__currShellCD][0] == 0:
            result, error = False, CANT_SHOOT_ERROR.NO_AMMO
        elif self.isGunReloading():
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

    def clear(self, leave = True):
        super(AmmoReplayRecorder, self).clear(leave)
        if leave:
            self.__changeRecord = None
            self.__timeRecord = None
            self.__replayCtrl = None
        return

    def setGunReloadTime(self, timeLeft, baseTime):
        self.__timeRecord(0, timeLeft)
        super(AmmoReplayRecorder, self).setGunReloadTime(timeLeft, baseTime)

    def changeSetting(self, intCD, avatar = None):
        if super(AmmoReplayRecorder, self).changeSetting(intCD, avatar) and intCD in self._order:
            self.__changeRecord(self._order.index(intCD))


class AmmoReplayPlayer(AmmoController):
    __slots__ = ('__callbackID', '__isActivated', '__timeGetter', '__percent', '__replayCtrl')

    def __init__(self, replayCtrl):
        super(AmmoReplayPlayer, self).__init__()
        self.__callbackID = None
        self.__isActivated = False
        self.__timeGetter = lambda : 0
        self.__percent = None
        self.__replayCtrl = replayCtrl
        self.__replayCtrl.onAmmoSettingChanged += self.__onAmmoSettingChanged
        return

    def clear(self, leave = True):
        if leave:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            self.__timeGetter = lambda : 0
            self.__replayCtrl.onAmmoSettingChanged -= self.__onAmmoSettingChanged
            self.__replayCtrl = None
        super(AmmoReplayPlayer, self).clear(leave)
        return

    def setGunReloadTime(self, timeLeft, baseTime):
        self.__percent = None
        if not self.__isActivated:
            self.__isActivated = True
            self.__timeGetter = self.__replayCtrl.getGunReloadAmountLeft
            self.__timeLoop()
        return

    def changeSetting(self, intCD, avatar = None):
        return False

    def getGunReloadTime(self):
        return 100.0 * self.__timeGetter()

    def isGunReloading(self):
        return self.getGunReloadTime() > 0

    def isGunReloadTimeInPercent(self):
        return True

    def __timeLoop(self):
        self.__callbackID = None
        self.__tick()
        self.__callbackID = BigWorld.callback(0.1, self.__timeLoop)
        return

    def __tick(self):
        percent = round(100.0 * self.__timeGetter())
        if self.__percent != percent:
            self.__percent = percent
            self.onGunReloadTimeSetInPercent(self.getCurrentShellCD(), percent)

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


__all__ = ('AmmoController', 'AmmoReplayRecord', 'AmmoReplayPlayer')
