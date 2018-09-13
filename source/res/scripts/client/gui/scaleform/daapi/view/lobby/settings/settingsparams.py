# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/settings/SettingsParams.py
import BigWorld
from account_helpers.settings_core import settings_constants, options
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.shared.utils import graphics
from gui.shared.utils.graphics import g_monitorSettings
from gui.Scaleform.daapi import AppRef
_DEFERRED_RENDER_IDX = 0

class SettingsParams(AppRef):

    def __init__(self):
        super(SettingsParams, self).__init__()
        self.SETTINGS = g_settingsCore.options

    def __settingsDiffPreprocessing(self, diff):
        if settings_constants.GRAPHICS.SMOOTHING in diff:
            rppSetting = graphics.GRAPHICS_SETTINGS.RENDER_PIPELINE
            renderOptions = graphics.getGraphicsSetting(rppSetting)
            isAdvancedRender = renderOptions.value == _DEFERRED_RENDER_IDX
            if rppSetting in diff:
                isAdvancedRender = diff[rppSetting] == _DEFERRED_RENDER_IDX
            if isAdvancedRender:
                diff[settings_constants.GRAPHICS.CUSTOM_AA] = diff[settings_constants.GRAPHICS.SMOOTHING]
            else:
                diff[settings_constants.GRAPHICS.MULTISAMPLING] = diff[settings_constants.GRAPHICS.SMOOTHING]
        return diff

    def getGameSettings(self):
        settings_pack = self.SETTINGS.pack(settings_constants.GAME.ALL())
        return settings_pack

    def getSoundSettings(self):
        return self.SETTINGS.pack(settings_constants.SOUND.ALL())

    def getGraphicsSettings(self):
        return self.SETTINGS.pack(settings_constants.GRAPHICS.ALL())

    def getMarkersSettings(self):
        return self.SETTINGS.pack(settings_constants.MARKERS.ALL())

    def getOtherSettings(self):
        return self.SETTINGS.pack(settings_constants.OTHER.ALL())

    def getAimSettings(self):
        return self.SETTINGS.pack(settings_constants.AIM.ALL())

    def getControlsSettings(self):
        return self.SETTINGS.pack(settings_constants.CONTROLS.ALL())

    def getMonitorSettings(self):
        return self.SETTINGS.pack((settings_constants.GRAPHICS.MONITOR,
         settings_constants.GRAPHICS.FULLSCREEN,
         settings_constants.GRAPHICS.WINDOW_SIZE,
         settings_constants.GRAPHICS.RESOLUTION,
         settings_constants.GRAPHICS.REFRESH_RATE,
         settings_constants.GRAPHICS.DYNAMIC_RENDERER))

    def preview(self, settingName, value):
        setting = self.SETTINGS.getSetting(settingName)
        if setting is not None:
            setting.preview(value)
        return

    def revert(self):
        self.SETTINGS.revert()
        g_settingsCore.clearStorages()

    def apply(self, diff, restartApproved):
        diff = self.__settingsDiffPreprocessing(diff)
        applyMethod = self.getApplyMethod(diff)
        self.SETTINGS.apply(diff)
        confirmators = g_settingsCore.applyStorages(restartApproved)
        g_settingsCore.confirmChanges(confirmators)
        if len(set(graphics.GRAPHICS_SETTINGS.ALL()) & set(diff.keys())):
            BigWorld.commitPendingGraphicsSettings()
        return applyMethod == options.APPLY_METHOD.RESTART

    def getApplyMethod(self, diff):
        newMonitorIndex = diff.get(settings_constants.GRAPHICS.MONITOR)
        isFullscreen = g_monitorSettings.isFullscreen or diff.get(settings_constants.GRAPHICS.FULLSCREEN)
        isMonitorChanged = g_monitorSettings.isMonitorChanged or newMonitorIndex is not None and g_monitorSettings.currentMonitor != int(newMonitorIndex)
        if isFullscreen and isMonitorChanged:
            return options.APPLY_METHOD.RESTART
        else:
            return self.SETTINGS.getApplyMethod(diff)
