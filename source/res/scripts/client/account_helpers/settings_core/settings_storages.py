# Embedded file name: scripts/client/account_helpers/settings_core/settings_storages.py
import functools
import weakref
import math
import BigWorld
from AvatarInputHandler.cameras import FovExtended
from adisp import async
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import TimerConfirmDialogMeta
from gui.shared.utils.graphics import g_monitorSettings
from helpers import isPlayerAccount
from messenger import g_settings as messenger_settings

class ISettingsStorage(object):

    def __init__(self, manager, core):
        self._manager = weakref.proxy(manager)
        self._core = weakref.proxy(core)
        self._settings = {}

    def store(self, setting):
        settingOption = setting['option']
        settingValue = setting['value']
        self._settings[settingOption] = settingValue

    def extract(self, settingOption, default = None):
        return self._settings.get(settingOption, default)

    def apply(self, restartApproved):
        return (None, lambda : None)

    def clear(self):
        self._settings.clear()


class VideoSettingsStorage(ISettingsStorage):

    @property
    def fullscreen(self):
        return self._settings.get('isFullscreen', g_monitorSettings.isFullscreen)

    @fullscreen.setter
    def fullscreen(self, value):
        self.store({'option': 'isFullscreen',
         'value': value})

    @property
    def resolution(self):
        resolution = (None, None)
        current = g_monitorSettings.currentVideoMode
        if current is not None:
            resolution = (current.width, current.height)
        return self._settings.get('resolution', resolution)

    @resolution.setter
    def resolution(self, value):
        self.store({'option': 'resolution',
         'value': value})

    @property
    def refreshRate(self):
        refreshRate = None
        current = g_monitorSettings.currentVideoMode
        if current is not None:
            refreshRate = current.refreshRate
        return self._settings.get('refreshRate', refreshRate)

    @refreshRate.setter
    def refreshRate(self, value):
        self.store({'option': 'refreshRate',
         'value': value})

    @property
    def videoMode(self):
        width, height = self.resolution
        refreshRate = self.refreshRate
        for mode in g_monitorSettings.videoModes:
            if mode.width == width and mode.height == height and mode.refreshRate == refreshRate:
                return mode

        return g_monitorSettings.currentVideoMode

    @property
    def windowSize(self):
        size = (None, None)
        current = g_monitorSettings.currentWindowSize
        if current is not None:
            size = (current.width, current.height)
        return self._settings.get('windowSize', size)

    @windowSize.setter
    def windowSize(self, value):
        self.store({'option': 'windowSize',
         'value': value})

    @property
    def monitor(self):
        return self._settings.get('monitor', g_monitorSettings.activeMonitor)

    @monitor.setter
    def monitor(self, value):
        self.store({'option': 'monitor',
         'value': value})

    def apply(self, restartApproved):
        if self._settings:
            LOG_DEBUG('Applying video settings: ', self._settings)
            cWindowSize = g_monitorSettings.currentWindowSize
            windowSizeWidth, windowSizeHeight = self.windowSize
            cIsFullScreen = g_monitorSettings.isFullscreen
            isFullscreen = self.fullscreen
            cVideoMode = g_monitorSettings.currentVideoMode
            videoMode = self.videoMode
            monitor = self.monitor
            cMonitor = g_monitorSettings.activeMonitor
            windowSizeChanged = cWindowSize is not None and windowSizeWidth is not None and windowSizeHeight is not None and (windowSizeWidth != cWindowSize.width or windowSizeHeight != cWindowSize.height)
            monitorChanged = monitor != cMonitor
            videModeChanged = cVideoMode is not None and videoMode is not None and videoMode.index != cVideoMode.index
            fullScreenChanged = isFullscreen != cIsFullScreen
            deviseRecreated = False
            if monitorChanged:
                g_monitorSettings.changeMonitor(monitor)
                deviseRecreated = isFullscreen or cIsFullScreen
            if windowSizeChanged and not isFullscreen:
                deviseRecreated = True
                g_monitorSettings.changeWindowSize(windowSizeWidth, windowSizeHeight)
            elif (not monitorChanged or restartApproved) and (videModeChanged or fullScreenChanged):
                deviseRecreated = True
                BigWorld.changeVideoMode(videoMode.index, not isFullscreen)
            self.clear()
            self._core.isDeviseRecreated = deviseRecreated
            if deviseRecreated:

                def wrapper(monitorChanged, windowSizeChanged, cMonitor, cWindowSize, cVideoMode, cIsFullScreen):

                    def revert():
                        if monitorChanged:
                            g_monitorSettings.changeMonitor(cMonitor)
                        if windowSizeChanged and not cIsFullScreen:
                            g_monitorSettings.changeWindowSize(cWindowSize.width, cWindowSize.height)
                        elif not monitorChanged and (videModeChanged or fullScreenChanged):
                            BigWorld.changeVideoMode(cVideoMode.index, not cIsFullScreen)

                    return revert

                if isPlayerAccount():

                    @async
                    def confirmator(callback = None):
                        BigWorld.callback(0.0, lambda : DialogsInterface.showI18nConfirmDialog('graphicsChangeConfirmation', callback, TimerConfirmDialogMeta('graphicsChangeConfirmation', timer=15)))

                else:
                    confirmator = 'graphicsChangeConfirmation'
                return (confirmator, wrapper(monitorChanged, windowSizeChanged, cMonitor, cWindowSize, cVideoMode, cIsFullScreen))
        return super(VideoSettingsStorage, self).apply(restartApproved)


class GameSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setGameSettings(self._settings)
        return super(GameSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getGameSetting(settingOption, default)
        return self._settings.get(settingOption, default)


class ExtendedGameSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setExtendedGameSettings(self._settings)
        return super(ExtendedGameSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getExtendedGameSetting(settingOption, default)
        return self._settings.get(settingOption, default)


class TutorialStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setTutorialSetting(self._settings)
        return super(TutorialStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getTutorialSetting(settingOption, default)
        return self._settings.get(settingOption, default)


class GameplaySettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setGameplaySettings(self._settings)
        return super(GameplaySettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getGameplaySetting(settingOption, default)
        return self._settings.get(settingOption, default)


class MessengerSettingsStorage(object):

    def __init__(self, proxy = None):
        self._proxy = weakref.proxy(proxy)
        self._settings = {}

    def store(self, setting):
        settingOption = setting['option']
        settingValue = setting['value']
        self._settings[settingOption] = settingValue
        self._proxy.store(setting)

    def extract(self, settingOption, default = None):
        return self._proxy.extract(settingOption, default)

    def apply(self, restartApproved):
        messenger_settings.saveUserPreferences(self._settings)
        return (None, lambda : None)

    def clear(self):
        self._settings.clear()


class GraphicsSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setGraphicsSettings(self._settings)
        return super(GraphicsSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getGraphicsSetting(settingOption, default)
        return self._settings.get(settingOption, default)


class SoundSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setSoundSettings(self._settings)
        return super(SoundSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getSoundSetting(settingOption, default)
        return self._settings.get(settingOption, default)


class KeyboardSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setSettings(self._settings)
        return super(KeyboardSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getSetting(settingOption, default)
        return self._settings.get(settingOption, default)


class ControlsSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setControlsSettings(self._settings)
        return super(ControlsSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getControlsSetting(settingOption, default)
        return self._settings.get(settingOption, default)


class AimSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setAimSettings(self._settings)
        return super(AimSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, key = None, default = None):
        default = self._manager.getAimSetting(settingOption, key, default)
        return self._settings.get(settingOption, {}).get(key, default)


class MarkersSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setMarkersSettings(self._settings)
        return super(MarkersSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, key = None, default = None):
        default = self._manager.getMarkersSetting(settingOption, key, default)
        return self._settings.get(settingOption, {}).get(key, default)


class MarksOnGunSettingsStorage(ISettingsStorage):

    def apply(self, restartApproved):
        if self._settings:
            self._manager.setMarksOnGunSettings(self._settings)
        return super(MarksOnGunSettingsStorage, self).apply(restartApproved)

    def extract(self, settingOption, default = None):
        default = self._manager.getMarksOnGunSetting(settingOption, default)
        return self._settings.get(settingOption, default)


class FOVSettingsStorage(ISettingsStorage):

    def __init__(self, manager = None, core = None):
        super(FOVSettingsStorage, self).__init__(manager, core)
        self.__dynamicFOVEnabled = None
        self.__FOV = None
        return

    def proxyDynamicFOVEnabled(self, option):
        self.__dynamicFOVEnabled = weakref.proxy(option)

    @property
    def dynamicFOVEnabled(self):
        value = self.__dynamicFOVEnabled.get() if self.__dynamicFOVEnabled is not None else None
        return self._settings.get('dynamicFOVEnabled', value)

    @dynamicFOVEnabled.setter
    def dynamicFOVEnabled(self, value):
        self.store({'option': 'dynamicFOVEnabled',
         'value': value})

    def proxyFOV(self, option):
        self.__FOV = weakref.proxy(option)

    @property
    def FOV(self):
        value = self.__FOV.get() if self.__dynamicFOVEnabled is not None else None
        return self._settings.get('FOV', value)

    @FOV.setter
    def FOV(self, value):
        self.store({'option': 'FOV',
         'value': value})

    def apply(self, restartApproved, forceApply = False):
        if self._settings or forceApply:
            staticFOV, dynamicFOVLow, dynamicFOVTop = self.FOV
            dynamicFOVEnabled = self.dynamicFOVEnabled

            def setFov(value, multiplier, dynamicFOVEnabled):
                if not dynamicFOVEnabled:
                    FovExtended.instance().resetFov()
                FovExtended.instance().defaultHorizontalFov = value

            if dynamicFOVEnabled:
                multiplier = float(dynamicFOVLow) / dynamicFOVTop
                defaultHorizontalFov = math.radians(dynamicFOVTop)
            else:
                multiplier = 1.0
                defaultHorizontalFov = math.radians(staticFOV)
            BigWorld.callback(0.0, functools.partial(setFov, defaultHorizontalFov, multiplier, dynamicFOVEnabled))
        return super(FOVSettingsStorage, self).apply(restartApproved)
