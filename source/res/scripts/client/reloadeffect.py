# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ReloadEffect.py
import logging
from copy import copy
from math import fabs
from constants import ExtraShotClipStates, STATIONARY_RELOAD_STATE
from helpers.CallbackDelayer import CallbackDelayer
from helpers import gEffectsDisabled, dependency
from debug_utils import LOG_DEBUG
import SoundGroups
import BigWorld
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
BARREL_DEBUG_ENABLED = False
GUN_RAMMER_TIME = 1.5
GUN_RAMMER_EFFECT_NAME = 'cons_gun_rammer_start'
_CALIBER_RELOAD_SOUND_SWITCH = 'SWITCH_ext_rld_autoloader_caliber'

class ReloadEffectsType(object):
    SIMPLE_RELOAD = 'SimpleReload'
    BARREL_RELOAD = 'BarrelReload'
    AUTO_RELOAD = 'AutoReload'
    DUALGUN_RELOAD = 'DualGunReload'
    TWINGUN_RELOAD = 'TwinGunReload'
    EXTRASHOTCLIP_RELOAD = 'ExtraShotClipReload'
    CHARGEABLEBURST_RELOAD = 'ChargeableBurstReload'
    STATIONARY_RELOAD = 'StationaryReloadReload'


def _createReloadEffectDesc(eType, dataSection, parentSection):
    if not dataSection.values():
        return None
    elif eType == ReloadEffectsType.SIMPLE_RELOAD:
        return _SimpleReloadDesc(dataSection, eType)
    elif eType == ReloadEffectsType.BARREL_RELOAD:
        return _BarrelReloadDesc(dataSection, eType)
    elif eType == ReloadEffectsType.AUTO_RELOAD:
        return _AutoReloadDesc(dataSection, eType)
    elif eType == ReloadEffectsType.DUALGUN_RELOAD:
        return _DualGunReloadDesc(dataSection, eType)
    elif eType == ReloadEffectsType.TWINGUN_RELOAD:
        return _TwinGunReloadDesc(dataSection, eType)
    elif eType == ReloadEffectsType.EXTRASHOTCLIP_RELOAD:
        return _ExtraShotClipReloadDesc(dataSection, eType, parentSection)
    elif eType == ReloadEffectsType.CHARGEABLEBURST_RELOAD:
        return _ChargeableBurstReloadDesc(dataSection, eType)
    else:
        return _StationaryReloadDesc(dataSection, eType, parentSection) if eType == ReloadEffectsType.STATIONARY_RELOAD else None


class _ReloadDesc(object):
    __slots__ = ('_intuitionOverrides',)

    def __init__(self):
        self._intuitionOverrides = {}

    def create(self):
        return None

    def createIntuitionReload(self):
        return None

    def hasUniqueIntuitionReload(self):
        return bool(self._intuitionOverrides)


class _SimpleReloadDesc(_ReloadDesc):
    __slots__ = ('duration', 'soundEvent', 'effectType')

    def __init__(self, dataSection, eType):
        super(_SimpleReloadDesc, self).__init__()
        self.duration = dataSection.readFloat('duration', 0.0) / 1000.0
        self.soundEvent = dataSection.readString('sound', '')
        self.effectType = eType
        intuitionOverrides = dataSection['intuition_overrides']
        if intuitionOverrides is not None:
            self._intuitionOverrides['duration'] = intuitionOverrides.readFloat('duration', self.duration * 1000.0) / 1000.0
            self._intuitionOverrides['sound'] = intuitionOverrides.readString('sound', self.soundEvent)
        return

    def create(self):
        return SimpleReload(self)

    def createIntuitionReload(self):
        decr = copy(self)
        decr.duration = self._intuitionOverrides.get('duration', self.duration)
        decr.soundEvent = self._intuitionOverrides.get('sound', self.soundEvent)
        return decr.create()


class _DualGunReloadDesc(_SimpleReloadDesc):
    __slots__ = ('ammoLowSound', 'soundEvent', 'runTimeDelta', 'runTimeDeltaAmmoLow', 'caliber')

    def __init__(self, dataSection, eType):
        super(_DualGunReloadDesc, self).__init__(dataSection, eType)
        self.ammoLowSound = dataSection.readString('ammoLowSound', '')
        self.runTimeDelta = dataSection.readFloat('runTimeDelta', 0.0)
        self.runTimeDeltaAmmoLow = dataSection.readFloat('runTimeDeltaAmmoLow', 0.0)
        self.caliber = dataSection.readString('caliber', '')

    def create(self):
        return DualGunReload(self)

    def createIntuitionReload(self):
        return DualGunReload(self)


class _TwinGunReloadDesc(_SimpleReloadDesc):
    __slots__ = ('twinGunSound', 'runTimeDeltaOneGun', 'runTimeDeltaTwinGun', 'caliber')

    def __init__(self, dataSection, eType):
        super(_TwinGunReloadDesc, self).__init__(dataSection, eType)
        self.twinGunSound = dataSection.readString('twinGunSound', '')
        self.runTimeDeltaOneGun = dataSection.readFloat('runTimeDeltaOneGun', 0.0)
        self.runTimeDeltaTwinGun = dataSection.readFloat('runTimeDeltaTwinGun', 0.0)
        self.caliber = dataSection.readString('caliber', '')

    def create(self):
        return TwinGunReload(self)

    def createIntuitionReload(self):
        return TwinGunReload(self)


class _BarrelReloadDesc(_SimpleReloadDesc):
    __slots__ = ('lastShellAlert', 'shellDuration', 'startLong', 'startLoop', 'stopLoop', 'loopShell', 'loopShellLast', 'ammoLow', 'caliber', 'shellDt', 'shellDtLast')

    def __init__(self, dataSection, eType):
        super(_BarrelReloadDesc, self).__init__(dataSection, eType)
        self.lastShellAlert = dataSection.readString('lastShellAlert', '')
        self.shellDuration = dataSection.readFloat('shellDuration', 0.0) / 1000.0
        self.startLong = dataSection.readString('startLong', '')
        self.startLoop = dataSection.readString('startLoop', '')
        self.stopLoop = dataSection.readString('stopLoop', '')
        self.loopShell = dataSection.readString('loopShell', '')
        self.loopShellLast = dataSection.readString('loopShellLast', '')
        self.ammoLow = dataSection.readString('ammoLow', '')
        self.caliber = dataSection.readString('caliber', '')
        self.shellDt = dataSection.readFloat('loopShellDt', 0.5)
        self.shellDtLast = dataSection.readFloat('loopShellLastDt', 0.5)
        intuitionOverrides = dataSection['intuition_overrides']
        if intuitionOverrides is not None:
            self._intuitionOverrides['loopShell'] = intuitionOverrides.readString('loopShell', self.loopShell)
            self._intuitionOverrides['loopShellLast'] = intuitionOverrides.readString('loopShellLast', self.loopShellLast)
            self._intuitionOverrides['loopShellLastDt'] = intuitionOverrides.readFloat('loopShellLastDt', self.shellDtLast)
            self._intuitionOverrides['startLong'] = intuitionOverrides.readString('startLong', self.startLong)
        return

    def create(self):
        return BarrelReload(self)

    def createIntuitionReload(self):
        descr = copy(self)
        descr.duration = self._intuitionOverrides['duration']
        descr.loopShell = self._intuitionOverrides['loopShell']
        descr.loopShellLast = self._intuitionOverrides['loopShellLast']
        descr.shellDtLast = self._intuitionOverrides['loopShellLastDt']
        descr.startLong = self._intuitionOverrides['startLong']
        return descr.create()


class _AutoReloadDesc(_ReloadDesc):
    __slots__ = ('duration', 'soundEvent', 'reloadStart', 'autoLoaderFull', 'lastShellAlert', 'shotFail', 'clipShellLoad', 'clipShellLoadT', 'ammoLow', 'caliber', 'almostComplete', 'almostCompleteT', 'effectType')

    def __init__(self, dataSection, eType):
        super(_AutoReloadDesc, self).__init__()
        self.duration = dataSection.readFloat('duration', 0.5) / 1000.0
        if self.duration < 0.5:
            self.duration = 0.5
        self.soundEvent = dataSection.readString('sound', '')
        self.reloadStart = dataSection.readString('reloadStart', '')
        self.autoLoaderFull = dataSection.readString('autoLoaderFull', '')
        self.lastShellAlert = dataSection.readString('lastShellAlert', '')
        self.ammoLow = dataSection.readString('ammoLow', '')
        self.caliber = dataSection.readString('caliber', '')
        self.clipShellLoad = dataSection.readString('clipShellLoad', '')
        self.clipShellLoadT = dataSection.readFloat('clipShellLoadDuration', 2000) / 1000.0
        if self.clipShellLoadT < 0.5:
            self.clipShellLoadT = 0.5
        self.almostComplete = dataSection.readString('almostComplete', '')
        self.almostCompleteT = dataSection.readFloat('almostCompleteDuration', 5000) / 1000.0
        if self.almostCompleteT < 0.5:
            self.almostCompleteT = 0.5
        self.shotFail = dataSection.readString('shotFail', '')
        self.effectType = eType
        intuitionOverrides = dataSection['intuition_overrides']
        if intuitionOverrides is not None:
            self._intuitionOverrides['reloadStart'] = intuitionOverrides.readString('reloadStart', self.reloadStart)
        return

    def create(self):
        return AutoReload(self)

    def createIntuitionReload(self):
        descr = copy(self)
        descr.reloadStart = self._intuitionOverrides['reloadStart']
        return AutoReload(descr)


class _ExtraShotClipReloadDesc(_BarrelReloadDesc):
    __slots__ = ('extraShellStart', 'extraShellFinish', 'extraShellDtLast', 'extraShellduration', 'extraShellCancel', 'extraShellStopUtility')

    def __init__(self, dataSection, eType, parentSection):
        barrelSection = dataSection.readString('barrel_reload', '')
        barrelSection = parentSection[barrelSection]
        super(_ExtraShotClipReloadDesc, self).__init__(barrelSection, eType)
        self.extraShellStart = dataSection.readString('extraShellStart', '')
        self.extraShellFinish = dataSection.readString('extraShellFinish', '')
        self.extraShellDtLast = dataSection.readFloat('extraShellFinishDt', 0.5)
        self.extraShellduration = dataSection.readFloat('extraShellduration', 0.5) / 1000.0
        self.extraShellCancel = dataSection.readString('extraShellCancel', '')
        self.extraShellStopUtility = dataSection.readString('extraShellStopUtility', '')

    def create(self):
        return ExtraShotClipReload(self)


class _ChargeableBurstReloadDesc(_SimpleReloadDesc):
    __slots__ = ('burstOneShellOffset', 'burstOneShell', 'burstLastShellOffset', 'burstLastShell', 'burstReady')

    def __init__(self, dataSection, eType):
        super(_ChargeableBurstReloadDesc, self).__init__(dataSection, eType)
        self.burstReady = dataSection.readString('burstReady', '')
        self.burstOneShellOffset = dataSection.readFloat('burstOneShellOffset', 0.0) / 1000.0
        self.burstOneShell = dataSection.readString('burstOneShell', '')
        self.burstLastShellOffset = dataSection.readFloat('burstLastShellOffset', 0.0) / 1000.0
        self.burstLastShell = dataSection.readString('burstLastShell', '')

    def create(self):
        return ChargeableBurstReload(self)

    def createIntuitionReload(self):
        decr = copy(self)
        decr.duration = self._intuitionOverrides.get('duration', self.duration)
        decr.soundEvent = self._intuitionOverrides.get('sound', self.soundEvent)
        return SimpleReload(decr)


class _StationaryReloadDesc(_BarrelReloadDesc):

    def __init__(self, dataSection, eType, parentSection):
        barrelSection = dataSection.readString('barrel_reload', '')
        barrelSection = parentSection[barrelSection]
        super(_StationaryReloadDesc, self).__init__(barrelSection, eType)

    def create(self):
        return StationaryReload(self)


def effectFromSection(section, parentSection):
    eType = section.readString('type', '')
    return _createReloadEffectDesc(eType, section, parentSection)


def isReplayPlayingWithTimeWarp():
    import BattleReplay
    replayCtrl = BattleReplay.g_replayCtrl
    return replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress


def playByName(soundName):
    if isReplayPlayingWithTimeWarp():
        return
    SoundGroups.g_instance.playSound2D(soundName)


def playByInstance(soundInstance):
    if isReplayPlayingWithTimeWarp():
        return
    soundInstance.play()


class _GunReload(CallbackDelayer):
    __slots__ = ('_desc',)

    def __init__(self, effectDesc):
        super(_GunReload, self).__init__()
        self._desc = effectDesc

    def getEffectType(self):
        return self._desc.effectType

    def calculateReloadFlags(self, reloadInProgress, timeLeft, baseTime, clipCapacity, mechanicState=None):
        return self._calculateReloadFlags(reloadInProgress, timeLeft, baseTime, clipCapacity, mechanicState)

    @classmethod
    def _calculateReloadFlags(cls, reloadInProgress, timeLeft, baseTime, _, __):
        return (True, fabs(timeLeft - baseTime) < 0.001 and not reloadInProgress)

    def _checkAndPlayGunRammerEffect(self, reloadTime):
        if _needGunRammerEffect():
            timeToPlayEffect = reloadTime - GUN_RAMMER_TIME
            if timeToPlayEffect > 0:
                self.delayCallback(timeToPlayEffect, _playGunRammerEffect)
            else:
                _logger.warning('Reload time(%s) is less than gun rammer effect time(GUN_RAMMER_TIME-%s)', reloadTime, GUN_RAMMER_TIME)

    def _stopGunRammerEffect(self):
        self.stopCallback(_playGunRammerEffect)


class SimpleReload(_GunReload):

    def __init__(self, effectDesc):
        _GunReload.__init__(self, effectDesc)
        self._sound = None
        self._startLoopT = 0.0
        return

    def __del__(self):
        if self._sound is not None:
            self._sound.stop()
            self._sound = None
        CallbackDelayer.destroy(self)
        return

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity, mechanicState=None):
        if gEffectsDisabled():
            return
        else:
            if self._sound is None:
                self._sound = SoundGroups.g_instance.getSound2D(self._desc.soundEvent)
            else:
                self._sound.stop()
            time = shellReloadTime - self._desc.duration
            if time < 0.0:
                time = 0.0
            self._checkAndPlayGunRammerEffect(shellReloadTime)
            self.delayCallback(time, self.__playSound)
            return

    def stop(self):
        if self._sound is not None:
            self._sound.stop()
            self._sound = None
        self.stopCallback(self.__playSound)
        self._stopGunRammerEffect()
        return

    def reloadEnd(self):
        self.stopCallback(self.__playSound)

    def onClipLoad(self, timeLeft, shellsInClip, lastShell, canBeFull):
        pass

    def onFull(self):
        pass

    def updateReloadTime(self, timeLeft, shellCount, lastShell, canBeFull):
        pass

    def shotFail(self):
        pass

    def __playSound(self):
        if self._sound is not None:
            self._sound.stop()
            if isReplayPlayingWithTimeWarp():
                return
            self._sound.play()
        return


class BarrelReload(SimpleReload):

    def __init__(self, effectDesc):
        SimpleReload.__init__(self, effectDesc)
        self.__reloadSequence = LoopSequence(self._desc)
        self._startLongSound = None
        return

    def __del__(self):
        self.stop()
        SimpleReload.__del__(self)

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity, mechanicState=None):
        if gEffectsDisabled():
            return
        else:
            SoundGroups.g_instance.setSwitch('SWITCH_ext_rld_automat_caliber', self._desc.caliber)
            currentTime = BigWorld.time()
            if shellCount == 0:
                self.stopCallback(self._startOneShoot)
                self.__reloadSequence.schedule(shellReloadTime, reloadShellCount)
                self._checkAndPlayGunRammerEffect(shellReloadTime)
                if reloadStart and shellReloadTime > self._desc.duration:
                    if self._startLongSound is not None:
                        self._startLongSound.stop()
                    self._startLongSound = SoundGroups.g_instance.getSound2D(self._desc.startLong)
                    self.__playStartLongSound()
                    if BARREL_DEBUG_ENABLED:
                        LOG_DEBUG('!!! Play Long  = {0} {1}'.format(currentTime, self._desc.startLong))
                if alert:
                    playByName(self._desc.ammoLow)
                    if BARREL_DEBUG_ENABLED:
                        LOG_DEBUG('!!! Play Ammo Low  = {0} {1}'.format(currentTime, self._desc.ammoLow))
            else:
                if shellCount == 1 and clipCapacity > 2:
                    if BARREL_DEBUG_ENABLED:
                        LOG_DEBUG('!!! Play Alert  = {0} {1}'.format(currentTime, self._desc.lastShellAlert))
                    playByName(self._desc.lastShellAlert)
                time = shellReloadTime - self._desc.shellDuration
                self.delayCallback(time, self._startOneShoot, currentTime + time)
            return

    def stop(self):
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('!!! Stop Loop = {0}'.format(self._desc.stopLoop))
        self.stopCallback(self._startOneShoot)
        self._stopGunRammerEffect()
        self.__reloadSequence.stop()

    def reloadEnd(self):
        self.stop()

    def onClipLoad(self, timeLeft, shellsInClip, lastShell, canBeFull):
        pass

    def onFull(self):
        pass

    def updateReloadTime(self, timeLeft, shellCount, lastShell, canBeFull):
        pass

    def shotFail(self):
        pass

    def _startOneShoot(self, invokeTime):
        if fabs(invokeTime - BigWorld.time()) < 0.1:
            if BARREL_DEBUG_ENABLED:
                LOG_DEBUG('!!!{0} Play One Shoot = {1}'.format(BigWorld.time(), self._desc.soundEvent))
            playByName(self._desc.soundEvent)

    def __playStartLongSound(self):
        if self._startLongSound is not None:
            self._startLongSound.stop()
            if isReplayPlayingWithTimeWarp():
                return
            self._startLongSound.play()
        return


class LoopSequence(CallbackDelayer):

    def __init__(self, desc):
        CallbackDelayer.__init__(self)
        self.lastShell = desc.loopShellLast
        self.shellTLast = desc.shellDtLast
        self.duration = desc.duration
        self.alignShellTime = 0.0
        self.__startLoop = desc.startLoop
        self.__stopLoop = desc.stopLoop
        self.__shell = desc.loopShell
        self.__shellT = desc.shellDt
        self.__sequence = []
        self.__inProgress = False

    def __del__(self):
        self.stop()
        CallbackDelayer.destroy(self)

    def schedule(self, reloadD, shellCount):
        self.stop()
        time = BigWorld.time()
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('LoopSequence::schedule time = {0} end time = {1} duration = {2}'.format(BigWorld.time(), time + reloadD, reloadD))
        loopDuration = self.duration
        if reloadD < self.duration:
            loopDuration = reloadD
            startLoopD = 0.0
            self.__inProgress = True
        else:
            startLoopD = reloadD - self.duration
            self.__inProgress = False
        self.__sequence = self.__generateTimeLine(startLoopD, loopDuration, shellCount)
        if BARREL_DEBUG_ENABLED:
            for item in self.__sequence:
                LOG_DEBUG('LoopSequence::schedule dt = {0} name = {1}'.format(item[0], item[1]))

        self.__start()

    def stop(self):
        self.stopCallback(self.__startCallback)
        if self.__inProgress:
            playByName(self.__stopLoop)
        self.__inProgress = False
        self.__sequence = []

    def isPlaying(self):
        return self.__inProgress

    def __start(self):
        if self.__sequence:
            callTime, _ = self.__sequence[0]
            dt = callTime - BigWorld.time()
            if dt < 0.0:
                dt = 0.0
            self.delayCallback(dt, self.__startCallback)

    def __startCallback(self):
        self.__inProgress = True
        if not self.__sequence:
            return None
        else:
            invokeTime, name = self.__sequence.pop(0)
            if fabs(invokeTime - BigWorld.time()) < 0.1 or not self.__sequence:
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('LoopSequence::__startCallback time = {0} {1}'.format(BigWorld.time(), name))
                playByName(name)
            if self.__sequence:
                callTime, _ = self.__sequence[0]
                dt = callTime - BigWorld.time()
                if dt < 0.0:
                    dt = 0.0
                return dt
            self.__inProgress = False
            return None
            return None

    def __generateTimeLine(self, loopStartDT, loopDuration, count):
        time = BigWorld.time()
        timeLine = []
        if not self.__inProgress and not self.alignShellTime:
            time += loopStartDT
            timeLine += [(time, self.__startLoop)]
        lastDt = loopDuration - self.shellTLast
        padding = max(0.0, self.alignShellTime - self.shellTLast)
        if lastDt <= 0.0:
            timeLine += [(time, self.lastShell)] * count
            timeLine.append((time + loopDuration, self.__stopLoop))
        else:
            if count > 1:
                dt = (lastDt - padding) / (count - 1)
                time += self.alignShellTime
                for i in xrange(0, count - 1):
                    timeLine.append((time, self.__shell))
                    if self.alignShellTime and i == count - 2:
                        timeLine.append((time, self.__startLoop))
                    time += dt

                time -= self.alignShellTime
                timeLine.append((time + padding, self.lastShell))
            else:
                if self.alignShellTime:
                    timeLine.append((time, self.__startLoop))
                time += lastDt
                timeLine.append((time, self.lastShell))
            timeLine.append((time + self.shellTLast, self.__stopLoop))
        return timeLine


class AutoReload(_GunReload):

    def __init__(self, effectDesc):
        _GunReload.__init__(self, effectDesc)
        self._sound = None
        self._almostCompleteSnd = None
        self._startLoopT = 0.0
        return

    def __del__(self):
        if self._sound is not None:
            self._sound.stop()
            self._sound = None
        CallbackDelayer.destroy(self)
        return

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity):
        if gEffectsDisabled():
            return
        else:
            if BARREL_DEBUG_ENABLED:
                LOG_DEBUG('AutoReload::start time = {0} {1} {2} {3} {4} {5} {6} '.format(BigWorld.time(), shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart))
            SoundGroups.g_instance.setSwitch(_CALIBER_RELOAD_SOUND_SWITCH, self._desc.caliber)
            self.stopCallback(self.__onShellInTheBarrel)
            self._almostCompleteSnd = None
            if self._sound is None:
                self._sound = SoundGroups.g_instance.getSound2D(self._desc.soundEvent)
            else:
                self._sound.stop()
            if reloadStart:
                if shellCount == 0:
                    playByName(self._desc.reloadStart)
                    if alert:
                        playByName(self._desc.ammoLow)
            time = shellReloadTime - self._desc.duration
            if time < 0.0:
                time = 0.0
            self.delayCallback(time, self.__onShellInTheBarrel, shellCount, reloadShellCount, BigWorld.time() + time)
            self._checkAndPlayGunRammerEffect(shellReloadTime)
            return

    def stop(self):
        if self._sound is not None:
            self._sound.stop()
            self._sound = None
        self.stopCallback(self.__onShellInTheBarrel)
        self.stopCallback(self.__onClipShellLoad)
        self.stopCallback(self.__onAlmostComplete)
        self._stopGunRammerEffect()
        self._almostCompleteSnd = None
        return

    def reloadEnd(self):
        self.stopCallback(self.__onShellInTheBarrel)

    def onClipLoad(self, timeLeft, shellCount, lastShell, canBeFull):
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('AutoReload::onClipLoad time = {0} {1} {2} {3}'.format(BigWorld.time(), timeLeft, shellCount, lastShell))
        self.stopCallback(self.__onAlmostComplete)
        self.stopCallback(self.__onClipShellLoad)
        self.updateReloadTime(timeLeft, shellCount, lastShell, canBeFull)

    def onFull(self):
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('AutoReload::onFull')
        playByName(self._desc.autoLoaderFull)
        self.stopCallback(self.__onAlmostComplete)

    def updateReloadTime(self, timeLeft, shellCount, lastShell, canBeFull):
        if shellCount > 0 and not lastShell:
            time = timeLeft - self._desc.clipShellLoadT
            if time < 0.0:
                time = 0.0
            self.delayCallback(time, self.__onClipShellLoad, BigWorld.time() + time)
        if lastShell and canBeFull:
            time = timeLeft - self._desc.almostCompleteT
            if time < 0.0:
                time = 0.0
            self.delayCallback(time, self.__onAlmostComplete, BigWorld.time() + time)

    def shotFail(self):
        playByName(self._desc.shotFail)

    def __onShellInTheBarrel(self, shellCount, reloadShellCount, time):
        if fabs(time - BigWorld.time()) > 0.1:
            return
        else:
            if self._sound is not None:
                self._sound.stop()
                if isReplayPlayingWithTimeWarp():
                    return
                self._sound.play()
                if shellCount == 1 and reloadShellCount > 2:
                    SoundGroups.g_instance.playSound2D(self._desc.lastShellAlert)
            return

    def __onClipShellLoad(self, time):
        if fabs(time - BigWorld.time()) > 0.1:
            return
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('AutoReload::__onClipShellLoad')
        playByName(self._desc.clipShellLoad)

    def __onAlmostComplete(self, time):
        if fabs(time - BigWorld.time()) > 0.1:
            return
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('AutoReload::__onAlmostComplete')
        self._almostCompleteSnd = SoundGroups.g_instance.getSound2D(self._desc.almostComplete)
        self._almostCompleteSnd.play()


class DualGunReload(_GunReload):

    def __init__(self, effectDesc):
        _GunReload.__init__(self, effectDesc)
        self.__sound = None
        self.__ammoLowSound = None
        return

    def __del__(self):
        self.stop()
        CallbackDelayer.destroy(self)

    def start(self, shellReloadTime, ammoLow, directTrigger=False):
        if gEffectsDisabled() or not directTrigger:
            return
        else:
            SoundGroups.g_instance.setSwitch(_CALIBER_RELOAD_SOUND_SWITCH, self._desc.caliber)
            self.stopCallback(self.__onReloadStart)
            timeToStart = shellReloadTime - self._desc.runTimeDelta
            if self.__sound is None:
                self.__sound = SoundGroups.g_instance.getSound2D(self._desc.soundEvent)
            if timeToStart > 0:
                self.delayCallback(timeToStart, self.__onReloadStart, BigWorld.time() + timeToStart)
            if ammoLow:
                timeToStart = shellReloadTime - self._desc.runTimeDeltaAmmoLow
                self.__ammoLowSound = SoundGroups.g_instance.getSound2D(self._desc.ammoLowSound)
                self.delayCallback(timeToStart, self.__onAmmoLow, BigWorld.time() + timeToStart)
            self._checkAndPlayGunRammerEffect(shellReloadTime)
            return

    def stop(self):
        for sound in (self.__sound, self.__ammoLowSound):
            if sound is not None:
                sound.stop()

        self.__sound = None
        self.__ammoLowSound = None
        self.stopCallback(self.__onReloadStart)
        self.stopCallback(self.__onAmmoLow)
        self._stopGunRammerEffect()
        return

    def reloadEnd(self):
        pass

    def __onReloadStart(self, time):
        if fabs(time - BigWorld.time()) > 0.1:
            return
        else:
            if self.__sound is not None:
                if isReplayPlayingWithTimeWarp():
                    return
                self.__sound.play()
            return

    def __onAmmoLow(self, time):
        if fabs(time - BigWorld.time()) > 0.1:
            return
        else:
            if self.__ammoLowSound is not None:
                if isReplayPlayingWithTimeWarp():
                    return
                self.__ammoLowSound.play()
            return


class TwinGunReload(_GunReload):

    def __init__(self, effectDesc):
        _GunReload.__init__(self, effectDesc)
        self.__sound = None
        return

    def __del__(self):
        self.stop()
        CallbackDelayer.destroy(self)

    def start(self, shellReloadTime, isTwinShot=False):
        if gEffectsDisabled():
            return
        SoundGroups.g_instance.setSwitch(_CALIBER_RELOAD_SOUND_SWITCH, self._desc.caliber)
        self.stopCallback(self.__onReloadStart)
        soundEvent = self._desc.soundEvent
        runTimeDelta = self._desc.runTimeDeltaOneGun
        if isTwinShot:
            soundEvent = self._desc.twinGunSound
            runTimeDelta = self._desc.runTimeDeltaTwinGun
        timeToStart = shellReloadTime - runTimeDelta
        if timeToStart > 0:
            self.__sound = SoundGroups.g_instance.getSound2D(soundEvent)
            self.delayCallback(timeToStart, self.__onReloadStart, BigWorld.time() + timeToStart)

    def stop(self):
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound = None
        self.stopCallback(self.__onReloadStart)
        return

    def reloadEnd(self):
        pass

    def __onReloadStart(self, time):
        if fabs(time - BigWorld.time()) > 0.1 or self.__sound is None:
            return
        else:
            playByInstance(self.__sound)
            return


class ExtraShotClipReload(SimpleReload):

    def __init__(self, effectDesc):
        SimpleReload.__init__(self, effectDesc)
        self.__reloadSequence = LoopSequence(self._desc)
        self._startLongSound = SoundGroups.g_instance.getSound2D(self._desc.startLong)
        self._extraStartSound = SoundGroups.g_instance.getSound2D(self._desc.extraShellStart)

    def __del__(self):
        self.stop()
        SimpleReload.__del__(self)

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity, mechanicState=None):
        isInnerShell = mechanicState == ExtraShotClipStates.NONE
        if gEffectsDisabled():
            return
        SoundGroups.g_instance.setSwitch('SWITCH_ext_rld_automat_caliber', self._desc.caliber)
        currentTime = BigWorld.time()
        if shellCount == 1:
            if isInnerShell:
                playByName(self._desc.lastShellAlert)
                time = shellReloadTime - self._desc.shellDuration
                self.delayCallback(time, self.__startOneShoot, currentTime + time)
            else:
                reloadShellCount = max(reloadShellCount - 1, 0)
                self.__reloadLongSound(alert, reloadShellCount, reloadStart, shellReloadTime, mechanicState, isClipFull=False)
        elif shellCount == 0:
            self.stopCallback(self.__startOneShoot)
            self.__reloadLongSound(alert, reloadShellCount, reloadStart, shellReloadTime, mechanicState, isClipFull=True)
        else:
            time = shellReloadTime - self._desc.shellDuration
            self.delayCallback(time, self.__startOneShoot, currentTime + time)

    def stop(self):
        self.reloadEnd()
        if self._extraStartSound is not None and self._extraStartSound.isPlaying:
            playByName(self._desc.extraShellStopUtility)
        return

    def reloadEnd(self):
        self.stopCallback(self.__startOneShoot)
        self._stopGunRammerEffect()
        self.__reloadSequence.stop()

    @classmethod
    def _calculateReloadFlags(cls, reloadInProgress, _, __, ___, mechanicState):
        reloadFromStart = not reloadInProgress if mechanicState else False
        reloadInProgress = mechanicState & ExtraShotClipStates.FULL_RELOAD_WITH_EXTRA_TIME
        return (reloadInProgress, reloadFromStart)

    def __startOneShoot(self, invokeTime):
        if fabs(invokeTime - BigWorld.time()) < 0.1:
            playByName(self._desc.soundEvent)

    def __reloadLongSound(self, alert, reloadShellCount, reloadStart, shellReloadTime, mechanicState, isClipFull):
        if isClipFull:
            self.__reloadSequence.lastShell = self._desc.loopShellLast
            self.__reloadSequence.shellTLast = self._desc.shellDtLast
            self.__reloadSequence.duration = self._desc.duration
        else:
            self.__reloadSequence.lastShell = self._desc.extraShellFinish
            self.__reloadSequence.shellTLast = self._desc.extraShellDtLast
            self.__reloadSequence.duration = self._desc.extraShellduration
        self.__reloadSequence.schedule(shellReloadTime, reloadShellCount)
        self._checkAndPlayGunRammerEffect(shellReloadTime)
        if isClipFull and mechanicState == ExtraShotClipStates.FULL_RELOAD_WITH_EXTRA_TIME | ExtraShotClipStates.EXTRA_FULL_RELOAD:
            playByName(self._desc.extraShellCancel)
        if reloadStart and shellReloadTime > self._desc.duration:
            self.__playStartLongSound(isClipFull=isClipFull)
        if alert:
            playByName(self._desc.ammoLow)

    def __playStartLongSound(self, isClipFull):
        if not isClipFull:
            playByInstance(self._extraStartSound)
        if self._startLongSound is not None:
            self._startLongSound.stop()
        playByInstance(self._startLongSound)
        return


class ChargeableBurstReload(SimpleReload):

    def __init__(self, effectDesc):
        SimpleReload.__init__(self, effectDesc)
        self.__isBurstActive = False
        self.__isBurstTriggered = False
        self.__shellReloadTime = 0.0
        self.__reloadShellCount = 0
        self._soundBurstReady = None
        self._soundBurstOneShell = None
        self._soundBurstLastShell = None
        return

    def __del__(self):
        self.stop()
        SimpleReload.__del__(self)

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity, extraShotState=None):
        if gEffectsDisabled():
            return
        self.__reloadShellCount = reloadShellCount
        hasCallback = self.hasDelayedCallback(self.__playOneShellSound) or self.hasDelayedCallback(self.__playLastShellSound)
        self.stopCallback(self.__playOneShellSound)
        self.stopCallback(self.__playLastShellSound)
        self.__shellReloadTime = BigWorld.serverTime() + shellReloadTime
        if self.__isBurstActive or self.__isBurstTriggered or hasCallback:
            self.__playDelayedBurstSounds()
            self.__isBurstTriggered = False
        else:
            SimpleReload.start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity, extraShotState)

    def stop(self):
        SimpleReload.stop(self)
        for sound in (self._soundBurstReady, self._soundBurstOneShell, self._soundBurstLastShell):
            if sound is not None:
                sound.stop()

        self.__shellReloadTime = 0.0
        self.stopCallback(self.__playOneShellSound)
        self.stopCallback(self.__playLastShellSound)
        return

    def reloadEnd(self):
        SimpleReload.reloadEnd(self)
        self.__shellReloadTime = 0.0
        self.stopCallback(self.__playOneShellSound)
        self.stopCallback(self.__playLastShellSound)

    def setBurstActive(self, isActive):
        if self.__isBurstActive != isActive:
            self.__isBurstActive = isActive
        else:
            return
        if not isActive:
            return
        self._soundBurstReady = SoundGroups.g_instance.getSound2D(self._desc.burstReady)
        self._soundBurstReady.play()
        if self.__shellReloadTime > BigWorld.serverTime():
            SimpleReload.stop(self)
            self.__playDelayedBurstSounds()
        else:
            self.__isBurstTriggered = True

    def __playDelayedBurstSounds(self):
        if isReplayPlayingWithTimeWarp():
            return
        shellReloadTime = self.__shellReloadTime - BigWorld.serverTime()
        if shellReloadTime > 0.0:
            self._checkAndPlayGunRammerEffect(shellReloadTime)
            lastShellReloadTime = shellReloadTime - self._desc.burstLastShellOffset
            if lastShellReloadTime > 0.0:
                self.delayCallback(lastShellReloadTime, self.__playLastShellSound)
            oneShellReloadTime = shellReloadTime - self._desc.burstOneShellOffset
            if oneShellReloadTime > 0.0 and self.__reloadShellCount > 1:
                self.delayCallback(oneShellReloadTime, self.__playOneShellSound)

    def __playOneShellSound(self):
        self._soundBurstOneShell = SoundGroups.g_instance.getSound2D(self._desc.burstOneShell)
        self._soundBurstOneShell.play()

    def __playLastShellSound(self):
        self._soundBurstLastShell = SoundGroups.g_instance.getSound2D(self._desc.burstLastShell)
        self._soundBurstLastShell.play()


class StationaryReload(SimpleReload):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, effectDesc):
        SimpleReload.__init__(self, effectDesc)
        self.reloadSequence = LoopSequence(self._desc)
        self.startLongSound = None
        return

    def __del__(self):
        self.stop()
        SimpleReload.__del__(self)

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity, mechanicState=None):
        if gEffectsDisabled():
            return
        else:
            SoundGroups.g_instance.setSwitch('SWITCH_ext_rld_automat_caliber', self._desc.caliber)
            currentTime = BigWorld.time()
            reloadShellCount = clipCapacity - shellCount
            if mechanicState.state == STATIONARY_RELOAD_STATE.RELOADING:
                if reloadShellCount:
                    self.stopCallback(self._startOneShoot)
                    self._checkAndPlayGunRammerEffect(shellReloadTime)
                    avgShellTime = shellReloadTime / reloadShellCount
                    self.reloadSequence.duration = shellReloadTime - 0.001
                    self.reloadSequence.alignShellTime = avgShellTime
                    if reloadStart or not (reloadShellCount == 1 and self.reloadSequence.isPlaying()):
                        self.reloadSequence.schedule(shellReloadTime, reloadShellCount)
                    if reloadStart and shellReloadTime > self._desc.duration:
                        if self.startLongSound is not None:
                            self.startLongSound.stop()
                        self.startLongSound = SoundGroups.g_instance.getSound2D(self._desc.startLong)
                        self.__playStartLongSound()
                    if alert:
                        playByName(self._desc.ammoLow)
            elif mechanicState.state == STATIONARY_RELOAD_STATE.FINISHING:
                self.stop()
            elif mechanicState.state == STATIONARY_RELOAD_STATE.IDLE and not reloadStart:
                if shellCount == 1 and clipCapacity > 2:
                    playByName(self._desc.lastShellAlert)
                time = shellReloadTime - self._desc.shellDuration
                self.delayCallback(time, self._startOneShoot, currentTime + time)
            return

    def stop(self):
        self.stopCallback(self._startOneShoot)
        self._stopGunRammerEffect()
        self.reloadSequence.stop()

    def reloadEnd(self):
        self.stop()

    @classmethod
    def _calculateReloadFlags(cls, reloadInProgress, timeLeft, baseTime, clipCapacity, mechanicState):
        ammoCtrl = cls.__sessionProvider.shared.ammo
        currentShellCD = ammoCtrl.getCurrentShellCD()
        shellsToLoad = clipCapacity - ammoCtrl.getShells(currentShellCD)[1]
        misAlignment = timeLeft - baseTime / clipCapacity * shellsToLoad
        inProgress = mechanicState.state == STATIONARY_RELOAD_STATE.RELOADING
        return (inProgress, fabs(misAlignment) < 0.001 and not reloadInProgress)

    def _startOneShoot(self, invokeTime):
        if fabs(invokeTime - BigWorld.time()) < 0.1:
            playByName(self._desc.soundEvent)

    def __playStartLongSound(self):
        if self.startLongSound is not None:
            self.startLongSound.stop()
            if isReplayPlayingWithTimeWarp():
                return
            self.startLongSound.play()
        return


class ReloadEffectStrategy(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__gunReloadEffect', '__intuitionReloadEffect', '__currentReloadEffect', '__reloadInProgress')

    def __init__(self, gunReloadEffectDesc):
        self.__gunReloadEffect = gunReloadEffectDesc.create()
        if gunReloadEffectDesc.hasUniqueIntuitionReload():
            self.__intuitionReloadEffect = gunReloadEffectDesc.createIntuitionReload()
        else:
            self.__intuitionReloadEffect = None
        self.__currentReloadEffect = self.__gunReloadEffect
        self.__reloadInProgress = False
        return

    def start(self, timeLeft, baseTime, clipCapacity, directTrigger=False, shotsAmount=-1, mechanicState=None):
        self.__reloadInProgress, reloadFromStart = self.__gunReloadEffect.calculateReloadFlags(self.__reloadInProgress, timeLeft, baseTime, clipCapacity, mechanicState)
        self.__reloadStartEffect(timeLeft, clipCapacity, reloadFromStart, directTrigger, shotsAmount, mechanicState)

    def stop(self):
        self.__reloadInProgress = False
        if self.__intuitionReloadEffect is not None:
            self.__intuitionReloadEffect.stop()
        self.__gunReloadEffect.stop()
        return

    def onClipLoad(self, timeLeft, shellsInClip, lastShell, canBeFull):
        if self.__currentReloadEffect is not None:
            self.__currentReloadEffect.onClipLoad(timeLeft, shellsInClip, lastShell, canBeFull)
        return

    def onFull(self):
        if self.__currentReloadEffect is not None:
            self.__currentReloadEffect.onFull()
        return

    def updateReloadTime(self, timeLeft, shellCount, lastShell, canBeFull):
        if self.__currentReloadEffect is not None:
            self.__currentReloadEffect.updateReloadTime(timeLeft, shellCount, lastShell, canBeFull)
        return

    def shotFail(self):
        if self.__currentReloadEffect is not None:
            self.__currentReloadEffect.shotFail()
        return

    def reloadEnd(self):
        self.__reloadInProgress = False
        if self.__currentReloadEffect is not None:
            self.__currentReloadEffect.reloadEnd()
        return

    def getGunReloadType(self):
        return self.__gunReloadEffect.getEffectType()

    def setBurstActive(self, isActive):
        if self.getGunReloadType() == ReloadEffectsType.CHARGEABLEBURST_RELOAD:
            self.__gunReloadEffect.setBurstActive(isActive)

    def __reloadStartEffect(self, timeLeft, clipCapacity, reloadFromStart, directTrigger=False, shotsAmount=1, mechanicState=None):
        ammoCtrl = self.__sessionProvider.shared.ammo
        currentShellCD = ammoCtrl.getCurrentShellCD()
        shellCounts = ammoCtrl.getShells(currentShellCD)
        shellsQuantityLeft = ammoCtrl.getShellsQuantityLeft()
        isIntuition = ammoCtrl.getIntuitionReloadInProcess()
        reloadShellCount = clipCapacity
        if isIntuition and self.__intuitionReloadEffect is not None:
            relloadEffect = self.__intuitionReloadEffect
        else:
            relloadEffect = self.__gunReloadEffect
        if self.__currentReloadEffect != relloadEffect:
            self.__currentReloadEffect.stop()
        self.__currentReloadEffect = relloadEffect
        if relloadEffect is not None:
            ammoLow = False
            gunReloadType = self.getGunReloadType()
            if gunReloadType == ReloadEffectsType.CHARGEABLEBURST_RELOAD:
                reloadShellCount = shellCounts[0]
            elif clipCapacity > shellCounts[0]:
                ammoLow = True
                reloadShellCount = shellCounts[0]
            if gunReloadType == ReloadEffectsType.DUALGUN_RELOAD:
                if shellsQuantityLeft == 1:
                    ammoLow = True
                relloadEffect.start(timeLeft, ammoLow, directTrigger)
            elif gunReloadType == ReloadEffectsType.TWINGUN_RELOAD:
                relloadEffect.start(timeLeft, shotsAmount > 1)
            elif gunReloadType == ReloadEffectsType.EXTRASHOTCLIP_RELOAD:
                relloadEffect.start(timeLeft, ammoLow, shellCounts[1], reloadShellCount, currentShellCD, reloadFromStart, clipCapacity, mechanicState=mechanicState)
            elif gunReloadType == ReloadEffectsType.STATIONARY_RELOAD:
                relloadEffect.start(timeLeft, ammoLow, shellCounts[1], reloadShellCount, currentShellCD, reloadFromStart, clipCapacity, mechanicState=mechanicState)
            else:
                relloadEffect.start(timeLeft, ammoLow, shellCounts[1], reloadShellCount, currentShellCD, reloadFromStart, clipCapacity)
        return


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def _needGunRammerEffect(sessionProvider=None):
    return sessionProvider.shared.optionalDevices.soundManager.needGunRammerEffect() if sessionProvider is not None else None


def _playGunRammerEffect():
    SoundGroups.g_instance.playSound2D(GUN_RAMMER_EFFECT_NAME)
