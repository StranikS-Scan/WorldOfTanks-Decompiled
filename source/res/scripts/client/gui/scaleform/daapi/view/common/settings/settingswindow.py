# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/SettingsWindow.py
import functools
import BigWorld
import VOIP
import SoundGroups
from debug_utils import *
from gui.GraphicsPresets import GraphicsPresets
from gui.Scaleform.locale.SETTINGS import SETTINGS
from Vibroeffects import VibroManager
from gui import DialogsInterface, g_guiResetters
from gui.battle_control import g_sessionProvider
from gui.shared.utils import flashObject2Dict, decorators
from gui.Scaleform.daapi.view.meta.SettingsWindowMeta import SettingsWindowMeta
from gui.Scaleform.daapi.view.common.settings.SettingsParams import SettingsParams
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.options import APPLY_METHOD

class SettingsWindow(SettingsWindowMeta):

    def __init__(self, ctx = None):
        super(SettingsWindow, self).__init__()
        self.__redefinedKeyModeEnabled = ctx.get('redefinedKeyMode', True)
        self.__initialTabIdx = ctx.get('tabIndex', -1)
        self.params = SettingsParams()

    def __getSettings(self):
        settings = {'GameSettings': self.params.getGameSettings(),
         'GraphicSettings': self.params.getGraphicsSettings(),
         'SoundSettings': self.params.getSoundSettings(),
         'ControlsSettings': self.params.getControlsSettings(),
         'AimSettings': self.params.getAimSettings(),
         'MarkerSettings': self.params.getMarkersSettings(),
         'OtherSettings': self.params.getOtherSettings()}
        reformatted_settings = {}
        for key, value in settings.iteritems():
            reformatted_keys = []
            reformatted_values = []
            reformatted_settings[key] = {'keys': reformatted_keys,
             'values': reformatted_values}
            for key, value in value.iteritems():
                reformatted_keys.append(key)
                reformatted_values.append(value)

        return reformatted_settings

    def __commitSettings(self, settings = None, restartApproved = False, isCloseWnd = False):
        if settings is None:
            settings = {}
        self.__apply(settings, restartApproved, isCloseWnd)
        return

    def __apply(self, settings, restartApproved = False, isCloseWnd = False):
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
        BigWorld.restartGame()

    def _populate(self):
        super(SettingsWindow, self)._populate()
        self.__currentSettings = self.params.getMonitorSettings()
        self._update()
        VibroManager.g_instance.onConnect += self.onVibroManagerConnect
        VibroManager.g_instance.onDisconnect += self.onVibroManagerDisconnect
        g_guiResetters.add(self.onRecreateDevice)
        BigWorld.wg_setAdapterOrdinalNotifyCallback(self.onRecreateDevice)
        SoundGroups.g_instance.enableVoiceSounds(True)

    def _update(self):
        self.as_setDataS(self.__getSettings())
        self.as_updateVideoSettingsS(self.__currentSettings)
        self.as_openTabS(self.__initialTabIdx)

    def _dispose(self):
        if not g_sessionProvider.getCtx().isInBattle:
            SoundGroups.g_instance.enableVoiceSounds(False)
        g_guiResetters.discard(self.onRecreateDevice)
        BigWorld.wg_setAdapterOrdinalNotifyCallback(None)
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
            self.app.voiceChatManager.checkForInitialization()

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

    def useRedifineKeysMode(self, isUse):
        if self.__redefinedKeyModeEnabled:
            BigWorld.wg_setRedefineKeysMode(isUse)

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
        yield self.app.voiceChatManager.requestCaptureDevices()
        opt = g_settingsCore.options.getSetting(settings_constants.SOUND.CAPTURE_DEVICES)
        self.as_setCaptureDevicesS(opt.get(), opt.getOptions())

    def altVoicesPreview(self):
        setting = g_settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        if setting is not None:
            setting.playPreviewSound()
        return

    def isSoundModeValid(self):
        setting = g_settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        if setting is not None:
            return setting.isSoundModeValid()
        else:
            return False

    def showWarningDialog(self, dialogID, settings, isCloseWnd):

        def callback(isOk):
            if isOk:
                self.applySettings(settings, False)
            self.as_confirmWarningDialogS(isOk, dialogID)
            if isCloseWnd and isOk:
                self.onWindowClose()

        DialogsInterface.showI18nConfirmDialog(dialogID, callback)

    def __updateInterfaceScale(self):
        self.as_setDataS(self.__getSettings())
        self.as_updateVideoSettingsS(self.params.getMonitorSettings())

    def __isGraphicsPresetApplied(self, settings):
        isGraphicsQualitySettings = False
        for settingKey in settings.iterkeys():
            if settingKey in GraphicsPresets.GRAPHICS_QUALITY_SETTINGS:
                isGraphicsQualitySettings = True
                break

        if isGraphicsQualitySettings:
            return self.as_isPresetAppliedS()
        return True
