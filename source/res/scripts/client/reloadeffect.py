# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ReloadEffect.py
import logging
from copy import copy
from math import fabs
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
MIN_RELOAD_TIME = 1

class ReloadEffectsType(object):
    SIMPLE_RELOAD = 'SimpleReload'
    BARREL_RELOAD = 'BarrelReload'
    AUTO_RELOAD = 'AutoReload'
    DUALGUN_RELOAD = 'DualGunReload'


def _createReloadEffectDesc(eType, dataSection):
    if not dataSection.values():
        return None
    elif eType == ReloadEffectsType.SIMPLE_RELOAD:
        return _SimpleReloadDesc(dataSection, eType)
    elif eType == ReloadEffectsType.BARREL_RELOAD:
        return _BarrelReloadDesc(dataSection, eType)
    elif eType == ReloadEffectsType.AUTO_RELOAD:
        return _AutoReloadDesc(dataSection, eType)
    else:
        return _DualGunReloadDesc(dataSection, eType) if eType == ReloadEffectsType.DUALGUN_RELOAD else None


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


def effectFromSection(section):
    eType = section.readString('type', '')
    return _createReloadEffectDesc(eType, section)


def playByName(soundName):
    import BattleReplay
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
        return
    SoundGroups.g_instance.playSound2D(soundName)


class _GunReload(CallbackDelayer):
    __slots__ = ('_desc',)

    def __init__(self, effectDesc):
        super(_GunReload, self).__init__()
        self._desc = effectDesc

    def getEffectType(self):
        return self._desc.effectType

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

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity):
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
            if shellReloadTime >= MIN_RELOAD_TIME:
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

    def shotFail(self):
        pass

    def __playSound(self):
        if self._sound is not None:
            self._sound.stop()
            import BattleReplay
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
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

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart, clipCapacity):
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
            import BattleReplay
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
                return
            self._startLongSound.play()
        return


class LoopSequence(CallbackDelayer):

    def __init__(self, desc):
        CallbackDelayer.__init__(self)
        self.__startLoop = desc.startLoop
        self.__stopLoop = desc.stopLoop
        self.__shell = desc.loopShell
        self.__lastShell = desc.loopShellLast
        self.__duration = desc.duration
        self.__shellT = desc.shellDt
        self.__shellTLast = desc.shellDtLast
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
        loopDuration = self.__duration
        if reloadD < self.__duration:
            loopDuration = reloadD
            startLoopD = 0.0
            self.__inProgress = True
        else:
            startLoopD = reloadD - self.__duration
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
        if not self.__inProgress:
            time += loopStartDT
            timeLine += [(time, self.__startLoop)]
        lastDt = loopDuration - self.__shellTLast
        if lastDt <= 0.0:
            timeLine += [(time, self.__lastShell)] * count
            timeLine.append((time + loopDuration, self.__stopLoop))
        else:
            if count > 1:
                dt = lastDt / (count - 1)
                for _ in xrange(0, count - 1):
                    timeLine.append((time, self.__shell))
                    time += dt

                timeLine.append((time, self.__lastShell))
            else:
                time += lastDt
                timeLine.append((time, self.__lastShell))
            timeLine.append((time + self.__shellTLast, self.__stopLoop))
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

    def onFull(self):
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('AutoReload::onFull')
        playByName(self._desc.autoLoaderFull)

    def shotFail(self):
        playByName(self._desc.shotFail)

    def __onShellInTheBarrel(self, shellCount, reloadShellCount, time):
        if fabs(time - BigWorld.time()) > 0.1:
            return
        else:
            if self._sound is not None:
                self._sound.stop()
                import BattleReplay
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
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
                import BattleReplay
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
                    return
                self.__sound.play()
            return

    def __onAmmoLow(self, time):
        if fabs(time - BigWorld.time()) > 0.1:
            return
        else:
            if self.__ammoLowSound is not None:
                import BattleReplay
                replayCtrl = BattleReplay.g_replayCtrl
                if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
                    return
                self.__ammoLowSound.play()
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

    def start(self, timeLeft, baseTime, clipCapacity, directTrigger=False):
        reloadFromStart = fabs(timeLeft - baseTime) < 0.001 if not self.__reloadInProgress else False
        self.__reloadInProgress = True
        self.__reloadStartEffect(timeLeft, clipCapacity, reloadFromStart, directTrigger)

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

    def __reloadStartEffect(self, timeLeft, clipCapacity, reloadFromStart, directTrigger=False):
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
            if clipCapacity > shellCounts[0]:
                ammoLow = True
                reloadShellCount = shellCounts[0]
            if self.getGunReloadType() == ReloadEffectsType.DUALGUN_RELOAD:
                if shellsQuantityLeft == 1:
                    ammoLow = True
                relloadEffect.start(timeLeft, ammoLow, directTrigger)
            else:
                relloadEffect.start(timeLeft, ammoLow, shellCounts[1], reloadShellCount, currentShellCD, reloadFromStart, clipCapacity)
        return


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def _needGunRammerEffect(sessionProvider=None):
    return sessionProvider.shared.optionalDevices.soundManager.needGunRammerEffect() if sessionProvider is not None else None


def _playGunRammerEffect():
    SoundGroups.g_instance.playSound2D(GUN_RAMMER_EFFECT_NAME)
