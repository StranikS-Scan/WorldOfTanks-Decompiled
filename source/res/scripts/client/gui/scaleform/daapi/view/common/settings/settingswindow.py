# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/SettingsWindow.py
import functools
import VOIP
from account_helpers.settings_core.settings_constants import SETTINGS_GROUP
from debug_utils import *
from gui.GraphicsPresets import GraphicsPresets
from gui.Scaleform.daapi.view.common.settings.new_settings_counter import getNewSettings, invalidateSettings
from gui.Scaleform.locale.SETTINGS import SETTINGS
from Vibroeffects import VibroManager
from gui import DialogsInterface, g_guiResetters
from gui.shared.utils import flashObject2Dict, decorators
from gui.Scaleform.daapi.view.meta.SettingsWindowMeta import SettingsWindowMeta
from gui.Scaleform.daapi.view.common.settings.SettingsParams import SettingsParams
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.options import APPLY_METHOD
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
_PAGES = (SETTINGS.GAMETITLE,
 SETTINGS.GRAFICTITLE,
 SETTINGS.SOUNDTITLE,
 SETTINGS.KEYBOARDTITLE,
 SETTINGS.CURSORTITLE,
 SETTINGS.MARKERTITLE,
 SETTINGS.FEEDBACK,
 SETTINGS.OTHERTITLE)
_PAGES_INDICES = dict(((v, k) for k, v in enumerate(_PAGES)))
_g_lastTabIdx = 0

def _getLastTabIndex():
    global _g_lastTabIdx
    return _g_lastTabIdx


def _setLastTabIndex(idx):
    global _g_lastTabIdx
    _g_lastTabIdx = idx


class SettingsWindow(SettingsWindowMeta):

    def __init__(self, ctx=None):
        super(SettingsWindow, self).__init__()
        self.__redefinedKeyModeEnabled = ctx.get('redefinedKeyMode', True)
        if 'tabIndex' in ctx and ctx['tabIndex'] is not None:
            _setLastTabIndex(ctx['tabIndex'])
        self.params = SettingsParams()
        return

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        """
        Returns instance of chat plugin to have access to VOIP Controller
        :return: instance of chat plugin
        """
        return None

    def __getSettingsParam(self):
        """Read settings from SettingsParam
        """
        settings = {SETTINGS_GROUP.GAME_SETTINGS: self.params.getGameSettings(),
         SETTINGS_GROUP.GRAPHICS_SETTINGS: self.params.getGraphicsSettings(),
         SETTINGS_GROUP.SOUND_SETTINGS: self.params.getSoundSettings(),
         SETTINGS_GROUP.CONTROLS_SETTINGS: self.params.getControlsSettings(),
         SETTINGS_GROUP.AIM_SETTINGS: self.params.getAimSettings(),
         SETTINGS_GROUP.MARKERS_SETTINGS: self.params.getMarkersSettings(),
         SETTINGS_GROUP.OTHER_SETTINGS: self.params.getOtherSettings(),
         SETTINGS_GROUP.FEEDBACK_SETTINGS: self.params.getFeedbackSettings()}
        return settings

    def __getSettings(self):
        """Create dict of settings divided by groups
        :return: dict { settingsGroup :  {keys: [settingsName], values: [settingsValues] }}
        """
        settings = self.__getSettingsParam()
        reformatted_settings = {}
        for key, value in settings.iteritems():
            reformatted_keys = []
            reformatted_values = []
            reformatted_settings[key] = {'keys': reformatted_keys,
             'values': reformatted_values}
            for settingName, settingValue in value.iteritems():
                reformatted_keys.append(settingName)
                reformatted_values.append(settingValue)

        return reformatted_settings

    def __commitSettings(self, settings=None, restartApproved=False, isCloseWnd=False):
        if settings is None:
            settings = {}
        self.__apply(settings, restartApproved, isCloseWnd)
        return

    def __apply(self, settings, restartApproved=False, isCloseWnd=False):
        LOG_DEBUG('Settings window: apply settings', restartApproved, settings)
        g_settingsCore.isDeviseRecreated = False
        g_settingsCore.isChangesConfirmed = True
        isRestart = self.params.apply(settings, restartApproved)
        if settings_constants.GRAPHICS.INTERFACE_SCALE in settings:
            self.__updateInterfaceScale()
        isPresetApplied = self.__isGraphicsPresetApplied(settings)
        if g_settingsCore.isChangesConfirmed and isCloseWnd:
            self.onWindowClose()
        if isRestart:
            BigWorld.savePreferences()
            if restartApproved:
                BigWorld.callback(0.3, self.__restartGame)
            elif g_settingsCore.isDeviseRecreated:
                self.onRecreateDevice()
                g_settingsCore.isDeviseRecreated = False
            else:
                BigWorld.callback(0.0, functools.partial(BigWorld.changeVideoMode, -1, BigWorld.isVideoWindowed()))
        elif not isPresetApplied:
            DialogsInterface.showI18nInfoDialog('graphicsPresetNotInstalled', None)
        return

    def __restartGame(self):
        BigWorld.savePreferences()
        BigWorld.worldDrawEnabled(False)
        BigWorld.restartGame()

    def _populate(self):
        super(SettingsWindow, self)._populate()
        if self.__redefinedKeyModeEnabled:
            BigWorld.wg_setRedefineKeysMode(True)
        self.__currentSettings = self.params.getMonitorSettings()
        self._update()
        VibroManager.g_instance.onConnect += self.onVibroManagerConnect
        VibroManager.g_instance.onDisconnect += self.onVibroManagerDisconnect
        g_guiResetters.add(self.onRecreateDevice)
        BigWorld.wg_setAdapterOrdinalNotifyCallback(self.onRecreateDevice)

    def _update(self):
        self.as_setDataS(self.__getSettings())
        newSettings = getNewSettings()
        if len(newSettings):
            self.as_setCountersDataS(newSettings)
        self.as_updateVideoSettingsS(self.__currentSettings)
        self.as_openTabS(_getLastTabIndex())

    def _dispose(self):
        if self.__redefinedKeyModeEnabled:
            BigWorld.wg_setRedefineKeysMode(False)
        g_guiResetters.discard(self.onRecreateDevice)
        BigWorld.wg_setAdapterOrdinalNotifyCallback(None)
        self.stopVoicesPreview()
        self.stopAltBulbPreview()
        VibroManager.g_instance.onConnect -= self.onVibroManagerConnect
        VibroManager.g_instance.onDisconnect -= self.onVibroManagerDisconnect
        super(SettingsWindow, self)._dispose()
        return

    def onVibroManagerConnect(self):
        self.as_onVibroManagerConnectS(True)

    def onVibroManagerDisconnect(self):
        self.as_onVibroManagerConnectS(False)

    def onTabSelected(self, tabId):
        if tabId == SETTINGS.SOUNDTITLE:
            self.bwProto.voipController.invalidateInitialization()
        if tabId in _PAGES_INDICES:
            _setLastTabIndex(_PAGES_INDICES[tabId])
        else:
            LOG_WARNING("Unknown settings window's page id", tabId)

    def onCounterTargetVisited(self, tabName):
        """Notify that user visited tab
        """
        invalidateSettings(tabName)

    def onSettingsChange(self, settingName, settingValue):
        settingValue = flashObject2Dict(settingValue)
        LOG_DEBUG('onSettingsChange', settingName, settingValue)
        self.params.preview(settingName, settingValue)

    def applySettings(self, settings, isCloseWnd):
        self._applySettings(flashObject2Dict(settings), isCloseWnd)

    def _applySettings(self, settings, isCloseWnd):
        applyMethod = self.params.getApplyMethod(settings)

        def confirmHandler(isOk):
            self.as_ConfirmationOfApplicationS(isOk)
            if isOk:
                self.__commitSettings(settings, isOk, isCloseWnd)
            else:
                self.params.revert()
                self._update()

        if applyMethod == APPLY_METHOD.RESTART:
            DialogsInterface.showI18nConfirmDialog('graphicsPresetRestartConfirmation', confirmHandler)
        elif applyMethod == APPLY_METHOD.DELAYED:
            DialogsInterface.showI18nConfirmDialog('graphicsPresetDelayedConfirmation', confirmHandler)
        else:
            confirmHandler(True)

    def onWindowClose(self):
        self.params.revert()
        self.startVOIPTest(False)
        self.destroy()

    def onRecreateDevice(self):
        actualSettings = self.params.getMonitorSettings()
        if self.__currentSettings and self.__currentSettings != actualSettings:
            curDrr = self.__currentSettings[settings_constants.GRAPHICS.DYNAMIC_RENDERER]
            actualDrr = actualSettings[settings_constants.GRAPHICS.DYNAMIC_RENDERER]
            self.__currentSettings = actualSettings
            result = self.__currentSettings.copy()
            if curDrr == actualDrr:
                result[settings_constants.GRAPHICS.DYNAMIC_RENDERER] = None
            self.as_updateVideoSettingsS(result)
        return

    def autodetectQuality(self):
        result = BigWorld.autoDetectGraphicsSettings()
        self.onRecreateDevice()
        return result

    def startVOIPTest(self, isStart):
        LOG_DEBUG('Vivox test: %s' % str(isStart))
        rh = VOIP.getVOIPManager()
        rh.enterTestChannel() if isStart else rh.leaveTestChannel()
        return False

    @decorators.process('__updateCaptureDevices')
    def updateCaptureDevices(self):
        yield self.bwProto.voipController.requestCaptureDevices()
        opt = g_settingsCore.options.getSetting(settings_constants.SOUND.CAPTURE_DEVICES)
        self.as_setCaptureDevicesS(opt.get(), opt.getOptions())

    def altVoicesPreview(self):
        setting = g_settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        setting.playPreviewSound()

    def altBulbPreview(self, sampleID):
        setting = g_settingsCore.options.getSetting(settings_constants.SOUND.DETECTION_ALERT_SOUND)
        setting.playPreviewSound(sampleID)

    def stopVoicesPreview(self):
        setting = g_settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        setting.clearPreviewSound()

    def stopAltBulbPreview(self):
        setting = g_settingsCore.options.getSetting(settings_constants.SOUND.DETECTION_ALERT_SOUND)
        setting.clearPreviewSound()

    def isSoundModeValid(self):
        setting = g_settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        return setting.isSoundModeValid()

    def showWarningDialog(self, dialogID, settings, isCloseWnd):

        def callback(isOk):
            if isOk:
                self.applySettings(settings, False)
            self.as_confirmWarningDialogS(isOk, dialogID)
            if isCloseWnd and isOk:
                self.onWindowClose()

        DialogsInterface.showI18nConfirmDialog(dialogID, callback)

    def onRecreateDevice(self):
        actualSettings = self.params.getMonitorSettings()
        curDrr = self.__currentSettings[settings_constants.GRAPHICS.DYNAMIC_RENDERER]
        actualDrr = actualSettings[settings_constants.GRAPHICS.DYNAMIC_RENDERER]
        self.__currentSettings = actualSettings
        result = self.__currentSettings.copy()
        if curDrr == actualDrr:
            result[settings_constants.GRAPHICS.DYNAMIC_RENDERER] = None
        self.as_updateVideoSettingsS(result)
        return

    def __updateInterfaceScale(self):
        self.as_setDataS(self.__getSettings())
        self.as_updateVideoSettingsS(self.params.getMonitorSettings())

    def __isGraphicsPresetApplied(self, settings):
        isGraphicsQualitySettings = False
        for settingKey in settings.iterkeys():
            if settingKey in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS:
                isGraphicsQualitySettings = True
                break

        return self.as_isPresetAppliedS() if isGraphicsQualitySettings else True
