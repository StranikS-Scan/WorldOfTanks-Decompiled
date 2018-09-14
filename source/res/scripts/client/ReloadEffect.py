# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ReloadEffect.py
from helpers.CallbackDelayer import CallbackDelayer
from helpers import gEffectsDisabled
from debug_utils import LOG_DEBUG
from functools import partial
from math import fabs
import SoundGroups
import BigWorld
BARREL_DEBUG_ENABLED = False

def _createReloadEffectDesc(type, dataSection):
    if len(dataSection.values()) == 0:
        return None
    elif type == 'SimpleReload':
        return _SimpleReloadDesc(dataSection)
    else:
        return _BarrelReloadDesc(dataSection) if type == 'BarrelReload' else None


class _ReloadDesc(object):

    def __init__(self):
        pass

    def create(self):
        return None


class _SimpleReloadDesc(_ReloadDesc):

    def __init__(self, dataSection):
        super(_SimpleReloadDesc, self).__init__()
        self.duration = dataSection.readFloat('duration', 0.0) / 1000.0
        self.soundEvent = dataSection.readString('sound', '')

    def create(self):
        return SimpleReload(self)


class _BarrelReloadDesc(_SimpleReloadDesc):

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


class SimpleReload(CallbackDelayer):

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
            if time > 0.0:
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

    def _playByName(self, soundName):
        import BattleReplay
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isTimeWarpInProgress:
            return
        SoundGroups.g_instance.playSound2D(soundName)


class BarrelReload(SimpleReload):

    def __init__(self, effectDesc):
        SimpleReload.__init__(self, effectDesc)
        self.__shellDt = 0.0
        self.__reloadCount = 0

    def __del__(self):
        self.stop()
        SimpleReload.__del__(self)

    def start(self, shellReloadTime, alert, shellCount, reloadShellCount, shellID, reloadStart):
        if gEffectsDisabled():
            return
        SoundGroups.g_instance.setSwitch('SWITCH_ext_rld_automat_caliber', self._desc.caliber)
        if shellCount == 0:
            self.stopCallback(self._startLoopEvent)
            self.stopCallback(self._loopOneShoot)
            time = shellReloadTime - self._desc.duration
            self.delayCallback(time, partial(self._startLoopEvent, BigWorld.time() + time))
            if reloadShellCount != 0:
                self.__shellDt = self._desc.duration / reloadShellCount
            else:
                self.__shellDt = self._desc.duration
            self.__reloadCount = reloadShellCount
            if reloadStart:
                self._playByName(self._desc.stopLoop)
                self._playByName(self._desc.startLong)
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('!!! Play Long  = {0} {1}'.format(BigWorld.time(), self._desc.startLong))
            if alert:
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('!!! Play Ammo Low  = {0} {1}'.format(BigWorld.time(), self._desc.ammoLow))
                self._playByName(self._desc.ammoLow)
        else:
            if shellCount == 1:
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('!!! Play Alert  = {0} {1}'.format(BigWorld.time(), self._desc.lastShellAlert))
                self._playByName(self._desc.lastShellAlert)
            time = shellReloadTime - self._desc.shellDuration
            self.delayCallback(time, partial(self._startOneShoot, BigWorld.time() + time))

    def stop(self):
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('!!! Stop Loop = {0}'.format(self._desc.stopLoop))
        self.__reloadCount = 0
        self.stopCallback(self._startLoopEvent)
        self.stopCallback(self._loopOneShoot)
        self.stopCallback(self._startOneShoot)
        self._playByName(self._desc.stopLoop)

    def __getShellDt(self):
        if self.__reloadCount > 1:
            dt = self.__shellDt
        elif self.__reloadCount > 0:
            dt = self.__shellDt + self._desc.shellDt - self._desc.shellDtLast
        else:
            dt = self._desc.shellDtLast
        dt = dt if dt > 0.0 else 0.0
        return dt

    def _startLoopEvent(self, invokeTime):
        if fabs(invokeTime - BigWorld.time()) < 0.1:
            if BARREL_DEBUG_ENABLED:
                LOG_DEBUG('!!! {0} Start Loop = {1}'.format(BigWorld.time(), self._desc.startLoop))
                LOG_DEBUG('!!!Shell DT = {0}'.format(self.__shellDt))
            self._playByName(self._desc.startLoop)
            self._startLoopT = BigWorld.time()
            self.delayCallback(self.__getShellDt() - self._desc.shellDt, self._loopOneShoot)

    def _startOneShoot(self, invokeTime):
        if fabs(invokeTime - BigWorld.time()) < 0.1:
            if BARREL_DEBUG_ENABLED:
                LOG_DEBUG('!!!{0} Play One Shoot = {1}'.format(BigWorld.time(), self._desc.soundEvent))
            self._playByName(self._desc.soundEvent)

    def _loopOneShoot(self):
        if self.__reloadCount > 0:
            self.__reloadCount -= 1
            if self.__reloadCount == 0:
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('!!! {0} Play In Loop One Shoot Last= {1}'.format(BigWorld.time() - self._startLoopT, self._desc.loopShellLast))
                self._playByName(self._desc.loopShellLast)
                return self.__getShellDt()
            else:
                if BARREL_DEBUG_ENABLED:
                    LOG_DEBUG('!!! {0}Play In Loop One Shoot = {1}'.format(BigWorld.time() - self._startLoopT, self._desc.loopShell))
                self._playByName(self._desc.loopShell)
                return self.__getShellDt()
        if BARREL_DEBUG_ENABLED:
            LOG_DEBUG('!!!{0} Stop Loop = {1}'.format(BigWorld.time() - self._startLoopT, self._desc.stopLoop))
        self._playByName(self._desc.stopLoop)
        return None
