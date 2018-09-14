# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/SettingsParams.py
import BigWorld
from account_helpers.settings_core import settings_constants, options
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.shared.utils import graphics
from gui.shared.utils.graphics import g_monitorSettings
_DEFERRED_RENDER_IDX = 0

class SettingsParams(object):

    def __settingsDiffPreprocessing(self, diff):
        smoothing = diff.pop('smoothing', None)
        if smoothing is not None:
            rppSetting = graphics.GRAPHICS_SETTINGS.RENDER_PIPELINE
            renderOptions = graphics.getGraphicsSetting(rppSetting)
            isAdvancedRender = renderOptions.value == _DEFERRED_RENDER_IDX
            if rppSetting in diff:
                isAdvancedRender = diff[rppSetting] == _DEFERRED_RENDER_IDX
            if isAdvancedRender:
                diff[settings_constants.GRAPHICS.CUSTOM_AA] = smoothing
            else:
                diff[settings_constants.GRAPHICS.MULTISAMPLING] = smoothing
        return diff

    def getGameSettings(self):
        return g_settingsCore.packSettings(settings_constants.GAME.ALL())

    def getSoundSettings(self):
        return g_settingsCore.packSettings(settings_constants.SOUND.ALL())

    def getGraphicsSettings(self):
        return g_settingsCore.packSettings(settings_constants.GRAPHICS.ALL())

    def getMarkersSettings(self):
        return g_settingsCore.packSettings(settings_constants.MARKERS.ALL())

    def getOtherSettings(self):
        return g_settingsCore.packSettings(settings_constants.OTHER.ALL())

    def getAimSettings(self):
        return g_settingsCore.packSettings(settings_constants.AIM.ALL())

    def getControlsSettings(self):
        return g_settingsCore.packSettings(settings_constants.CONTROLS.ALL())

    def getMonitorSettings(self):
        return g_settingsCore.packSettings((settings_constants.GRAPHICS.MONITOR,
         settings_constants.GRAPHICS.FULLSCREEN,
         settings_constants.GRAPHICS.WINDOW_SIZE,
         settings_constants.GRAPHICS.RESOLUTION,
         settings_constants.GRAPHICS.REFRESH_RATE,
         settings_constants.GRAPHICS.DYNAMIC_RENDERER,
         settings_constants.GRAPHICS.INTERFACE_SCALE))

    def preview(self, settingName, value):
        if settingName == 'smoothing':
            rppSetting = graphics.GRAPHICS_SETTINGS.RENDER_PIPELINE
            renderOptions = graphics.getGraphicsSetting(rppSetting)
            isAdvancedRender = renderOptions.value == _DEFERRED_RENDER_IDX
            if isAdvancedRender:
                g_settingsCore.previewSetting(settings_constants.GRAPHICS.CUSTOM_AA, value)
            else:
                g_settingsCore.previewSetting(settings_constants.GRAPHICS.MULTISAMPLING, value)
            return
        g_settingsCore.previewSetting(settingName, value)

    def revert(self):
        g_settingsCore.revertSettings()
        g_settingsCore.clearStorages()

    def apply(self, diff, restartApproved):
        diff = self.__settingsDiffPreprocessing(diff)
        applyMethod = self.getApplyMethod(diff)
        g_settingsCore.applySettings(diff)
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
            return g_settingsCore.getApplyMethod(diff)
