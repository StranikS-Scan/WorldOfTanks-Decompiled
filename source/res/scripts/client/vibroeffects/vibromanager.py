# Embedded file name: scripts/client/Vibroeffects/VibroManager.py
import copy
from EffectsSettings import EffectsSettings
from VibroEffect import VibroEffect
import Settings
from debug_utils import *
import Event
from PlayerEvents import g_playerEvents
g_instance = None

class VibroManager:

    class GroupSettings:
        pass

    def __init__(self):
        self.__effects = {}
        self.__quickEffects = {}
        self.__vibrationObject = BigWorld.WGVibration()
        self.__vibrationObject.reset()
        g_playerEvents.onAccountShowGUI += self.__onAccountShowGUI
        self.__eventManager = Event.EventManager()
        self.onConnect = Event.Event(self.__eventManager)
        self.onDisconnect = Event.Event(self.__eventManager)
        self.__runningEffects = {}
        self.__topEffect = None
        self.__groupsSettings = {}
        for groupName in EffectsSettings.Groups.AllGroupNames:
            self.__groupsSettings[groupName] = VibroManager.GroupSettings()
            self.__groupsSettings[groupName].enabled = True
            self.__groupsSettings[groupName].gain = 1.0

        EffectsSettings.loadSettings()
        self.__gain = 1.0
        self.__isEnabledByUser = True
        self.loadUserPrefs()
        self.__isConnected = False
        self.connect()
        self.launchQuickEffect('startup_veff')
        return

    def start(self):
        from gui.app_loader import g_appLoader
        g_appLoader.onGUISpaceChanged += self.__onGUISpaceChanged

    def __onGUISpaceChanged(self, spaceID):
        from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID
        if spaceID == GUI_GLOBAL_SPACE_ID.LOGIN:
            self.stopAllEffects()

    def __onAccountShowGUI(self, ctx):
        self.connect()

    def playButtonClickEffect(self, buttonType):
        if not self.__isConnected:
            return
        self.launchQuickEffect('button_click_veff')

    def clearEffects(self):
        for effect in self.__effects.values():
            effect.destroy()

        for effectPool in self.__quickEffects.values():
            for effect in effectPool:
                effect.destroy()

    def destroy(self):
        from gui.app_loader import g_appLoader
        g_appLoader.onGUISpaceChanged -= self.__onGUISpaceChanged
        self.clearEffects()
        self.__effects = None
        self.__quickEffects = None
        self.__runningEffects = None
        self.__vibrationObject = None
        self.saveUserPrefs()
        self.__eventManager.clear()
        g_playerEvents.onAccountShowGUI -= self.__onAccountShowGUI
        return

    def loadUserPrefs(self):
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_VIBRATION):
            self.saveUserPrefs()
        ds = userPrefs[Settings.KEY_VIBRATION]
        self.setGain(ds.readFloat('gain', 1.0))
        self.setEnabledByUser(ds.readBool('enabled_by_user', True))
        groupsSettingsSection = ds['groups']
        if groupsSettingsSection is None:
            return
        else:
            for groupName in EffectsSettings.Groups.AllGroupNames:
                groupSection = groupsSettingsSection[groupName]
                if groupSection is not None:
                    self.__groupsSettings[groupName].enabled = groupSection.readBool('enabled', True)
                    self.__groupsSettings[groupName].gain = groupSection.readFloat('gain', 1.0)

            return

    def saveUserPrefs(self):
        userPrefs = Settings.g_instance.userPrefs
        if not userPrefs.has_key(Settings.KEY_VIBRATION):
            userPrefs.write(Settings.KEY_VIBRATION, '')
        ds = userPrefs[Settings.KEY_VIBRATION]
        ds.writeFloat('gain', self.getGain())
        ds.writeBool('enabled_by_user', self.isEnabledByUser())
        for groupName in EffectsSettings.Groups.AllGroupNames:
            ds.writeBool('groups/%s/enabled' % groupName, self.__groupsSettings[groupName].enabled)
            ds.writeFloat('groups/%s/gain' % groupName, self.__groupsSettings[groupName].gain)

    def getGroupsSettings(self):
        return copy.deepcopy(self.__groupsSettings)

    def __clampGain(self, gain):
        if gain > 1.0:
            return 1.0
        if gain < 0.0:
            return 0.0
        return gain

    def setGroupsSettings(self, settings):
        self.__groupsSettings = copy.deepcopy(settings)
        for groupSettings in self.__groupsSettings.values():
            groupSettings.gain = self.__clampGain(groupSettings.gain)

    def isGroupEnabled(self, groupName):
        if groupName in self.__groupsSettings:
            return self.__groupsSettings[groupName].enabled
        LOG_DEBUG('group not found: ' + groupName)
        return False

    def getGroupGain(self, groupName, default = 1.0):
        if groupName in self.__groupsSettings:
            return self.__groupsSettings[groupName].gain
        return default

    def setGroupGain(self, groupName, value):
        if groupName in self.__groupsSettings:
            groupSettings = self.__groupsSettings[groupName]
            groupSettings.gain = self.__clampGain(value)

    def isEnabledByUser(self):
        return self.__isEnabledByUser

    def setEnabledByUser(self, enable):
        if not enable:
            for effect in self.__runningEffects.values():
                self.stopEffect(effect)

            self.__runningEffects.clear()
        self.__isEnabledByUser = enable

    def connect(self):
        wasConnected = self.__isConnected
        if not wasConnected:
            self.clearEffects()
            self.__quickEffects.clear()
            self.__runningEffects.clear()
        self.__isConnected = self.__vibrationObject.connect()
        if self.__isConnected and not wasConnected:
            self.onConnect()
            for effect in self.__effects.values():
                effect.reInit(self.loadEffectFromFile(effect.name))
                self.stopEffect(effect)

        if not self.__isConnected and wasConnected:
            self.onDisconnect()
        return self.__isConnected

    def canWork(self):
        return self.__isEnabledByUser and self.__isConnected

    def setGain(self, gain):
        if gain < 0.0:
            gain = 0.0
        if gain > 1.0:
            gain = 1.0
        self.__gain = gain
        self.__vibrationObject.setGain(self.__gain)

    def getGain(self):
        return self.__gain

    def getStatus(self):
        result = {}
        result['constant'] = self.__effects
        result['quick'] = self.__quickEffects
        result['running'] = self.__runningEffects
        return result

    def getOverlappedGainMultiplier(self):
        return EffectsSettings.getOverlappedGainMultiplier()

    def loadEffectFromFile(self, effectName, priority = 0):
        if not self.__isConnected:
            return VibroEffect(effectName, None, EffectsSettings.getEffectPriority(effectName), self.__vibrationObject, EffectsSettings.getGroupForEffect(effectName))
        else:
            effectHandle = self.__vibrationObject.createEffect()
            fileName = EffectsSettings.CFG_FOLDER + effectName + '.uwv'
            self.__vibrationObject.loadEffectFromFile(effectHandle, fileName)
            effect = VibroEffect(effectName, effectHandle, EffectsSettings.getEffectPriority(effectName), self.__vibrationObject, EffectsSettings.getGroupForEffect(effectName))
            return effect

    def getEffect(self, effectName):
        if effectName in self.__effects:
            return self.__effects[effectName]
        effect = self.loadEffectFromFile(effectName)
        self.__effects[effectName] = effect
        return effect

    def launchQuickEffect(self, effectName, count = 1, gain = 100):
        if not self.canWork():
            return
        elif count is None:
            return
        else:
            sourceEffect = None
            if effectName in self.__quickEffects:
                effectsPool = self.__quickEffects[effectName]
                for effect in effectsPool:
                    if not effect.isRunning():
                        effect.setRelativeGain(gain)
                        self.startEffect(effect, count)
                        return
                    sourceEffect = effect

            if sourceEffect is None:
                effectToLaunch = self.loadEffectFromFile(effectName)
                self.__quickEffects[effectName] = [effectToLaunch]
            else:
                effectToLaunch = VibroEffect(effectName, self.__vibrationObject.cloneEffect(sourceEffect.handle), sourceEffect.getPriority(), self.__vibrationObject, sourceEffect.group)
                self.__quickEffects[effectName].append(effectToLaunch)
            effectToLaunch.setRelativeGain(gain)
            self.startEffect(effectToLaunch, count)
            return

    def startEffect(self, vibroEffect, count = None):
        if not self.canWork() or not self.isGroupEnabled(vibroEffect.group):
            return
        elif vibroEffect.isRunning() or vibroEffect.handle is None:
            return
        else:
            vibroEffect.onStart(count)
            self.__runningEffects[vibroEffect.handle] = vibroEffect
            if self.__topEffect is None or vibroEffect.getPriority() >= self.__topEffect.getPriority():
                if self.__topEffect is not None:
                    self.__drownEffect(self.__topEffect)
                self.__topEffect = vibroEffect
                self.__topEffect.setRelativeGain(self.__topEffect.getRelativeGain())
            self.update()
            return

    def stopEffect(self, vibroEffect):
        if vibroEffect.handle is None:
            return
        else:
            vibroEffect.onStop()
            return

    def stopAllEffects(self):
        for effect in self.__runningEffects.values():
            self.stopEffect(effect)

        self.update()

    def __drownEffect(self, vibroEffect):
        effectGain = self.getGroupGain(vibroEffect.group) * self.getOverlappedGainMultiplier() * vibroEffect.getRelativeGain()
        self.__vibrationObject.setEffectGain(vibroEffect.handle, effectGain)

    def update(self):
        if not self.canWork():
            return
        else:
            curTopEffect = None
            for vibroEffect in self.__runningEffects.values()[:]:
                if not vibroEffect.isRunning():
                    del self.__runningEffects[vibroEffect.handle]
                elif curTopEffect is None or curTopEffect.getPriority() < vibroEffect.getPriority():
                    curTopEffect = vibroEffect

            shouldRecalcGain = self.__topEffect is None or not self.__topEffect.isRunning()
            if shouldRecalcGain:
                self.__topEffect = curTopEffect
            for vibroEffect in self.__runningEffects.values():
                if (shouldRecalcGain or vibroEffect.requiresGainChange()) and vibroEffect != self.__topEffect:
                    self.__drownEffect(vibroEffect)
                elif vibroEffect.requiresGainChange() or shouldRecalcGain:
                    self.__vibrationObject.setEffectGain(vibroEffect.handle, self.getGroupGain(vibroEffect.group) * vibroEffect.getRelativeGain())

            return
