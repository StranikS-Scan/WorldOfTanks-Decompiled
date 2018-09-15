# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ReloadEffect.py
from helpers.CallbackDelayer import CallbackDelayer
from helpers import gEffectsDisabled
from debug_utils import LOG_DEBUG
from math import fabs
import SoundGroups
import BigWorld
BARREL_DEBUG_ENABLED = False

def _createReloadEffectDesc(type, dataSection):
    if not dataSection.values():
        return None
    elif type == 'SimpleReload':
        return _SimpleReloadDesc(dataSection)
    else:
        return _BarrelReloadDesc(dataSection) if type == 'BarrelReload' else None


class _ReloadDesc(object):
    __slots__ = ()

    def __init__(self):
        pass

    def create(self):
        return None


class _SimpleReloadDesc(_ReloadDesc):
    __slots__ = ('duration', 'soundEvent')

    def __init__(self, dataSection):
        super(_SimpleReloadDesc, self).__init__()
        self.duration = dataSection.readFloat('duration', 0.0) / 1000.0
        self.soundEvent = dataSection.readString('sound', '')

    def create(self):
        return SimpleReload(self)


class _BarrelReloadDesc(_SimpleReloadDesc):
    __slots__ = ('lastShellAlert', 'shellDuration', 'startLong', 'startLoop', 'stopLoop', 'loopShell', 'loopShellLast', 'ammoLow', 'caliber', 'shellDt', 'shellDtLast')

    def __init__(self, dataSection):
        super(_BarrelReloadDesc, self).__init__(dataSection)
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

    def create(self):
        return BarrelReload(self)


def effectFromSection(section):
    type = section.readString('type', '')
    return _createReloadEffectDesc(type, section)


def playByName(soundName):
    import BattleReplay
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
        return
    SoundGroups.g_instance.playSound2D(soundName)


class SimpleReload(CallbackDelayer):
    __slots__ = ('_desc', '_sound', '_startLoopT')

    def __init__(self, effectDesc):
        CallbackDelayer.__init__(self)
        self._desc = effectDesc
        self._sound = None
        self._startLoopT = 0.0
        return

    def __del__(self):
        if self._sound is not None:
            self._sound.stop()
            self._sound = None
        CallbackDelayer.destroy(self)
        return

    def start(self, shellReloadTime, alert, lastShell, reloadShellCount, shellID, reloadStart):
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
            self.delayCallback(time, self.__playSound)
            return

    def stop(self):
        if self._sound is not None:
            self._sound.stop()
            self._sound = None
        self.stopCallback(self.__playSound)
        return

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
    __slots__ = ('__reloadSequence',)

    def __init__(self, effectDesc):
        SimpleReload.__init__(self, effectDesc)
        self.__reloadSequence = LoopSequence(self._desc)

    def __del__(self):
        self.stop()
        SimpleReload.__del__(self)

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart):
        if gEffectsDisabled():
            return
        SoundGroups.g_instance.setSwitch('SWITCH_ext_rld_automat_caliber', self._desc.caliber)
        currentTime = BigWorld.time()
        if shellCount == 0:
            self.__reloadSequence.schedule(shellReloadTime, reloadShellCount)
            if reloadStart:
                playByName(self._desc.startLong)
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('!!! Play Long  = {0} {1}'.format(currentTime, self._desc.startLong))
            if alert:
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('!!! Play Ammo Low  = {0} {1}'.format(currentTime, self._desc.ammoLow))
        else:
            if shellCount == 1:
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('!!! Play Alert  = {0} {1}'.format(currentTime, self._desc.lastShellAlert))
                playByName(self._desc.lastShellAlert)
            time = shellReloadTime - self._desc.shellDuration
            self.delayCallback(time, self._startOneShoot, currentTime + time)

    def stop(self):
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('!!! Stop Loop = {0}'.format(self._desc.stopLoop))
        self.stopCallback(self._startOneShoot)
        self.__reloadSequence.stop()

    def _startOneShoot(self, invokeTime):
        if fabs(invokeTime - BigWorld.time()) < 0.1:
            if BARREL_DEBUG_ENABLED:
                LOG_DEBUG('!!!{0} Play One Shoot = {1}'.format(BigWorld.time(), self._desc.soundEvent))
            playByName(self._desc.soundEvent)


class LoopSequence(CallbackDelayer):
    __slots__ = ('__startLoop', '__stopLoop', '__shell', '__lastShell', '__duration', '__shellT', '__shellTLast', '__sequence')

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

    def __del__(self):
        self.stop()
        CallbackDelayer.destroy(self)

    def schedule(self, reloadD, shellCount):
        time = BigWorld.time()
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('LoopSequence::schedule time = {0} end time = {1} duration = {2}'.format(BigWorld.time(), time + reloadD, reloadD))
        loopDuration = self.__duration
        if reloadD < self.__duration:
            loopDuration = reloadD
            startLoopD = 0.0
            inProgress = True
        else:
            startLoopD = reloadD - self.__duration
            inProgress = False
        self.__sequence = self.__generateTimeLine(startLoopD, loopDuration, inProgress, shellCount)
        if BARREL_DEBUG_ENABLED:
            for item in self.__sequence:
                LOG_DEBUG('LoopSequence::schedule dt = {0} name = {1}'.format(item[0], item[1]))

        self.__start()

    def stop(self):
        self.stopCallback(self.__start)
        playByName(self.__stopLoop)
        self.__sequence = []

    def __start(self):
        if self.__sequence:
            callTime, _ = self.__sequence[0]
            dt = callTime - BigWorld.time()
            if dt < 0.0:
                dt = 0.0
            self.delayCallback(dt, self.__startCallback)

    def __startCallback(self):
        if not self.__sequence:
            return None
        else:
            invokeTime, name = self.__sequence.pop(0)
            if fabs(invokeTime - BigWorld.time()) > 0.1:
                return None
            if BARREL_DEBUG_ENABLED:
                LOG_DEBUG('LoopSequence::__startCallback time = {0} {1}'.format(BigWorld.time(), name))
            playByName(name)
            if self.__sequence:
                callTime, _ = self.__sequence[0]
                dt = callTime - BigWorld.time()
                if dt < 0.0:
                    dt = 0.0
                return dt
            return None
            return None

    def __generateTimeLine(self, loopStartDT, loopDuration, inProgress, count):
        time = BigWorld.time()
        timeLine = []
        if not inProgress:
            time += loopStartDT
            timeLine += [(time, self.__startLoop)]
        lastDt = loopDuration - self.__shellTLast
        if lastDt <= 0.0:
            timeLine += [(time, self.__lastShell)] * count
            timeLine.append((time + loopDuration, self.__stopLoop))
        else:
            if count > 1:
                dt = lastDt / (count - 1)
                for i in xrange(0, count - 1):
                    timeLine.append((time, self.__shell))
                    time += dt

                timeLine.append((time, self.__lastShell))
            else:
                time += lastDt
                timeLine.append((time, self.__lastShell))
            timeLine.append((time + self.__shellTLast, self.__stopLoop))
        return timeLine
