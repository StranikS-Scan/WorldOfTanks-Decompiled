# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/SettingsParams.py
import BigWorld
from account_helpers.settings_core import settings_constants, options
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.shared.utils import graphics
from gui.shared.utils.graphics import g_monitorSettings
_DEFERRED_RENDER_IDX = 0

class SettingsParams(object):

    def __settingsDiffPreprocessing(self, diff):
        """
        This method will be invoked before any settings processing.
        Prepare settings to apply (splitting or concatenating and etc.)
        
        :param diff: [dict(settingName->settingValue)] new settings values
        :return: the same input dict with some modifications
        """
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
        """
        Returns GAME settings.
        
        :return: [dict(settingName->settingValue)] current game settings values
        """
        return g_settingsCore.packSettings(settings_constants.GAME.ALL())

    def getSoundSettings(self):
        """
        Returns SOUND settings.
        
        :return: [dict(settingName->settingValue)] current sound settings values
        """
        return g_settingsCore.packSettings(settings_constants.SOUND.ALL())

    def getGraphicsSettings(self):
        """
        Returns GRAPHICS settings.
        
        :return: [dict(settingName->settingValue)] current graphics settings values
        """
        return g_settingsCore.packSettings(settings_constants.GRAPHICS.ALL())

    def getMarkersSettings(self):
        """
        Returns MARKERS settings.
        
        :return: [dict(settingName->settingValue)] current markers settings values
        """
        return g_settingsCore.packSettings(settings_constants.MARKERS.ALL())

    def getFeedbackSettings(self):
        """
        Returns all feedback settings.
        
        :return: [dict(settingName->settingValue)] feedback settings values
        """
        return {settings_constants.FEEDBACK.DAMAGE_LOG: self.getDamageLogSettings(),
         settings_constants.FEEDBACK.DAMAGE_INDICATOR: self.getDamageIndicatorSettings(),
         settings_constants.FEEDBACK.BATTLE_EVENTS: self.getBattleEventsSettings()}

    def getOtherSettings(self):
        """
        Returns OTHER settings.
        
        :return: [dict(settingName->settingValue)] other settings values
        """
        return g_settingsCore.packSettings(settings_constants.OTHER.ALL())

    def getDamageLogSettings(self):
        """
        Returns damage log settings.
        
        :return: [dict(settingName->settingValue)] damage log settings values
        """
        return g_settingsCore.packSettings(settings_constants.DAMAGE_LOG.ALL())

    def getDamageIndicatorSettings(self):
        """
        Returns damage indicator settings.
        
        :return: [dict(settingName->settingValue)] damage indicator settings values
        """
        return g_settingsCore.packSettings(settings_constants.DAMAGE_INDICATOR.ALL())

    def getBattleEventsSettings(self):
        """
        Returns battle events settings.
        
        :return: [dict(settingName->settingValue)] damage battle events values
        """
        return g_settingsCore.packSettings(settings_constants.BATTLE_EVENTS.ALL())

    def getAimSettings(self):
        """
        Returns AIM settings.
        
        :return: [dict(settingName->settingValue)] current aim settings values
        """
        return g_settingsCore.packSettings(settings_constants.AIM.ALL())

    def getControlsSettings(self):
        """
        Returns CONTROLS settings.
        
        :return: [dict(settingName->settingValue)] current controls settings values
        """
        return g_settingsCore.packSettings(settings_constants.CONTROLS.ALL())

    def getMonitorSettings(self):
        """
        Returns monitor related settings.
        
        :return: [dict(settingName->settingValue)] current monitor settings values
        """
        return g_settingsCore.packSettings((settings_constants.GRAPHICS.MONITOR,
         settings_constants.GRAPHICS.FULLSCREEN,
         settings_constants.GRAPHICS.WINDOW_SIZE,
         settings_constants.GRAPHICS.RESOLUTION,
         settings_constants.GRAPHICS.REFRESH_RATE,
         settings_constants.GRAPHICS.DYNAMIC_RENDERER,
         settings_constants.GRAPHICS.INTERFACE_SCALE))

    def preview(self, settingName, value):
        """
        Preview settings with given value. Preview setting can be reverted to the original
        value by settingObj.revert() call.
        
        :param settingName: setting name to preview
        :param value: setting value to preview
        """
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
        """
        Reverts all available settings to the original values
        """
        g_settingsCore.revertSettings()
        g_settingsCore.clearStorages()

    def apply(self, diff, restartApproved):
        """
        Applies given settings diff
        
        :param diff: [dict(settingName->settingValue)] settings values
        :param restartApproved: was restart approved
        :return: restart needed flag
        """
        diff = self.__settingsDiffPreprocessing(diff)
        applyMethod = self.getApplyMethod(diff)
        g_settingsCore.applySettings(diff)
        confirmators = g_settingsCore.applyStorages(restartApproved)
        g_settingsCore.confirmChanges(confirmators)
        if len(set(graphics.GRAPHICS_SETTINGS.ALL()) & set(diff.keys())):
            BigWorld.commitPendingGraphicsSettings()
        return applyMethod == options.APPLY_METHOD.RESTART

    def getApplyMethod(self, diff):
        """
        Check settings for apply method
        
        :param diff: [dict(settingName->settingValue)] settings values
        :return: [options.APPLY_METHOD.*] settings apply method
        """
        newMonitorIndex = diff.get(settings_constants.GRAPHICS.MONITOR)
        isFullscreen = g_monitorSettings.isFullscreen or diff.get(settings_constants.GRAPHICS.FULLSCREEN)
        isMonitorChanged = g_monitorSettings.isMonitorChanged or newMonitorIndex is not None and g_monitorSettings.currentMonitor != int(newMonitorIndex)
        return options.APPLY_METHOD.RESTART if isFullscreen and isMonitorChanged else g_settingsCore.getApplyMethod(diff)
