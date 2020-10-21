# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EnvironmentSwitcher.py
import functools
import BigWorld
import BattleReplay
from helpers import dependency
from constants import IS_DEVELOPMENT
from skeletons.gui.battle_session import IBattleSessionProvider
from ArenaType import EnvSwitcherSettings
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from helpers import newFakeModel
from debug_utils import LOG_DEBUG

class CustomCallbackDelayer(object):

    def __init__(self):
        self.__callbacks = {}

    def destroy(self):
        self.clearCallbacks()

    def clearCallbacks(self):
        for _, callbackId in self.__callbacks.iteritems():
            if callbackId is not None:
                BigWorld.cancelCallback(callbackId)

        self.__callbacks = {}
        return

    def __funcWrapper(self, func, *args, **kwargs):
        hashValue = self.__getCallbackHash(func, *args, **kwargs)
        if hashValue in self.__callbacks:
            del self.__callbacks[hashValue]
        desiredDelay = func(*args, **kwargs)
        if desiredDelay is not None and desiredDelay >= 0:
            curId = BigWorld.callback(desiredDelay, functools.partial(self.__funcWrapper, func, *args, **kwargs))
            self.__callbacks[hashValue] = curId
        return

    def delayCallback(self, seconds, func, *args, **kwargs):
        hashValue = self.__getCallbackHash(func, *args, **kwargs)
        curId = self.__callbacks.get(hashValue)
        if curId is not None:
            BigWorld.cancelCallback(curId)
            del self.__callbacks[hashValue]
        curId = BigWorld.callback(seconds, functools.partial(self.__funcWrapper, func, *args, **kwargs))
        self.__callbacks[hashValue] = curId
        return

    def stopCallback(self, func, *args, **kwargs):
        hashValue = self.__getCallbackHash(func, *args, **kwargs)
        curId = self.__callbacks.get(hashValue)
        if curId is not None:
            BigWorld.cancelCallback(curId)
            del self.__callbacks[hashValue]
        return

    def hasDelayedCallback(self, func, *args, **kwargs):
        hashValue = self.__getCallbackHash(func, *args, **kwargs)
        return hashValue in self.__callbacks

    def __getCallbackHash(self, func, *args, **kwargs):
        hashValue = 0
        for arg in args:
            hashValue += hash(arg)

        for _, arg in kwargs.items():
            hashValue += hash(arg)

        hashValue += hash(func)
        return hashValue


class EnvironmentSwitcher(BigWorld.Entity, CustomCallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    debugEnvironmentID = 0

    class SwitcherCallback(object):

        def __init__(self, pSettings, pMethod):
            self.settings = pSettings
            self.currentValue = pSettings.direction.x
            self.method = pMethod

    def __init__(self):
        CustomCallbackDelayer.__init__(self)
        self.__arenaECPComponent = None
        self.__renderEnv = BigWorld.CustomizationEnvironment()
        self.__runningCallbacks = {}
        self.__fakeModel = None
        self.__effectsPlayer = None
        self.setConfig(BigWorld.player().arena.arenaType.envSwitcherSettings)
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.setDataCallback(BattleReplay.CallbackDataNames.SWITCH_ENVIRONMENT, self.startSwitch)
        return

    def onEnterWorld(self, prereqs):
        envData = self._getEnvironmentData()
        if envData:
            envData.onEnvironmentEventIDUpdate += self._onEnvironmentUpdated
            self.startSwitch(envData.getCurrentEnvironmentID())

    def onLeaveWorld(self):
        self.__onFadeEnd()
        envData = self._getEnvironmentData()
        if envData:
            envData.onEnvironmentEventIDUpdate -= self._onEnvironmentUpdated

    def setConfig(self, settings):
        self.__settings = settings

    def start(self, envSettingID, setting):
        if not isinstance(setting, EnvSwitcherSettings.EnvSetting):
            return
        else:
            if setting.funcName is not None and hasattr(self.__renderEnv, setting.funcName):
                method = getattr(self.__renderEnv, setting.funcName)
                callback = EnvironmentSwitcher.SwitcherCallback(setting, method)
                self.__runningCallbacks[envSettingID] = callback
                self.delayCallback(0.0, self.__update, envSettingID)
            if setting.fader is not None:
                self.__getArenaECPComponent().fadeOut(setting.fader)
            if setting.faderPlayer is not None:
                self.__fadeOutPlayer(setting.faderPlayer)
            return

    def startSwitch(self, switcherID):
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.serializeCallbackData(BattleReplay.CallbackDataNames.SWITCH_ENVIRONMENT, (switcherID,))
        if self.__settings:
            switcher = self.__settings.getSwitcherByID(switcherID)
            if switcher is None:
                EnvironmentSwitcher.debugEnvironmentID = 0
                switcher = self.__settings.getSwitcherByID(0)
            if switcher:
                self.switch(switcher.envName)
                if switcher.settings:
                    for envSettingID in switcher.settings:
                        self.start(envSettingID, self.__settings.getEnvSettingByID(envSettingID))

        return

    def switch(self, envName):
        if envName is not None:
            self.__renderEnv.enable(True, envName)
        else:
            self.__renderEnv.enable(False)
        return

    def __update(self, settingID):
        callback = self.__runningCallbacks.get(settingID)
        if callback:
            if callback.settings.direction.y < callback.settings.direction.x:
                callback.currentValue -= callback.settings.speed
            else:
                callback.currentValue += callback.settings.speed
            if callback.method is not None:
                callback.method(callback.currentValue)
            if abs(callback.settings.direction.y - callback.currentValue) < callback.settings.speed:
                self.stopCallback(self.__update, settingID)
                del self.__runningCallbacks[settingID]
            else:
                self.delayCallback(callback.settings.timeout, self.__update, settingID)
        return

    def _getEnvironmentData(self):
        gameEventStorage = self._getGameEventComponent()
        return None if gameEventStorage is None else gameEventStorage.getEnvironmentData()

    def _getGameEventComponent(self):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        return None if componentSystem is None else getattr(componentSystem, 'gameEventComponent', None)

    def _onEnvironmentUpdated(self, envID):
        self.startSwitch(envID)

    def __getArenaECPComponent(self):
        if not self.__arenaECPComponent:
            cs = BigWorld.player().arena.componentSystem
            self.__arenaECPComponent = getattr(cs, 'ecp')
        return self.__arenaECPComponent

    def __fadeOutPlayer(self, section):
        effects = effectsFromSection(section)
        if effects is None:
            return
        else:
            self.__fakeModel = newFakeModel()
            BigWorld.player().addModel(self.__fakeModel)
            self.__effectsPlayer = EffectsListPlayer(effects.effectsList, effects.keyPoints, debugParent=self)
            self.__effectsPlayer.play(self.__fakeModel, callbackFunc=self.__onFadeEnd)
            return

    def __onFadeEnd(self):
        if self.__effectsPlayer:
            self.__effectsPlayer.stop()
            self.__effectsPlayer = None
        if self.__fakeModel:
            BigWorld.player().delModel(self.__fakeModel)
            self.__fakeModel = None
        return


def debugSwitchEnvironment(switcherID):
    if not IS_DEVELOPMENT:
        return
    for e in BigWorld.entities.values():
        if isinstance(e, EnvironmentSwitcher):
            if switcherID < 0:
                EnvironmentSwitcher.debugEnvironmentID -= 1
                EnvironmentSwitcher.debugEnvironmentID = max(0, EnvironmentSwitcher.debugEnvironmentID)
            else:
                EnvironmentSwitcher.debugEnvironmentID += 1
            LOG_DEBUG('debugSwitchEnvironment fired with ID:', EnvironmentSwitcher.debugEnvironmentID)
            e.startSwitch(EnvironmentSwitcher.debugEnvironmentID)
            break
