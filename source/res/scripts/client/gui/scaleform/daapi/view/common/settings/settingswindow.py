# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/SettingsWindow.py
import functools
import BattleReplay
import BigWorld
import WGC
import VOIP
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COLOR_SETTINGS_TAB_IDX
from account_helpers.settings_core.ServerSettingsManager import LIMITED_UI_KEY
from account_helpers.settings_core.settings_constants import SETTINGS_GROUP
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from account_helpers.counter_settings import getNewSettings, invalidateSettings
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.SETTINGS import SETTINGS
from gui import DialogsInterface, g_guiResetters
from gui.limited_ui.lui_rules_storage import LuiRuleTypes
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils import flashObject2Dict, decorators, graphics
from gui.Scaleform.daapi.view.meta.SettingsWindowMeta import SettingsWindowMeta
from gui.Scaleform.daapi.view.common.settings.SettingsParams import SettingsParams
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.options import APPLY_METHOD
from helpers import dependency
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from gui.Scaleform.genConsts.SETTINGS_DIALOGS import SETTINGS_DIALOGS
from gui.shared.formatters import icons
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IAnonymizerController, ILimitedUIController, IEventBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.battle_hints.newbie_battle_hints_controller import INewbieBattleHintsController
from uilogging.limited_ui.constants import LimitedUILogItem, LimitedUILogScreenParent
from uilogging.limited_ui.loggers import LimitedUILogger
from uilogging.newbie_hints.loggers import NewbieHintsSettingsUILogger, NewbieHintsSettingsTooltipsUILogger
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


def _delayCall(delay, function):
    if BattleReplay.g_replayCtrl.isPaused:
        function()
    else:
        BigWorld.callback(delay, function)


class SettingsWindow(SettingsWindowMeta):
    anonymizerController = dependency.descriptor(IAnonymizerController)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    limitedUIController = dependency.descriptor(ILimitedUIController)
    eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self, ctx=None):
        super(SettingsWindow, self).__init__()
        self.__redefinedKeyModeEnabled = ctx.get('redefinedKeyMode', True)
        self.__isBattleSettings = ctx.get('isBattleSettings', False)
        self.__uiNewbieHintsTooltipLogger = NewbieHintsSettingsTooltipsUILogger()
        self.__uiNewbieHintsLogger = NewbieHintsSettingsUILogger()
        if 'tabIndex' in ctx and ctx['tabIndex'] is not None:
            _setLastTabIndex(ctx['tabIndex'])
        self.params = SettingsParams()
        return

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def __getSettingsParam(self):
        settings = {SETTINGS_GROUP.GAME_SETTINGS: self.params.getGameSettings(),
         SETTINGS_GROUP.GRAPHICS_SETTINGS: self.params.getGraphicsSettings(),
         SETTINGS_GROUP.SOUND_SETTINGS: self.params.getSoundSettings(),
         SETTINGS_GROUP.CONTROLS_SETTINGS: self.params.getControlsSettings(),
         SETTINGS_GROUP.AIM_SETTINGS: self.params.getAimSettings(),
         SETTINGS_GROUP.MARKERS_SETTINGS: self.params.getMarkersSettings(),
         SETTINGS_GROUP.FEEDBACK_SETTINGS: self.params.getFeedbackSettings()}
        return settings

    def __getSettings(self):
        settings = self.__getSettingsParam()
        return {key:{'keys': value.keys(),
         'values': value.values()} for key, value in settings.iteritems()}

    def __commitSettings(self, settings=None, restartApproved=False, isCloseWnd=False):
        if settings is None:
            settings = {}
        self.__apply(settings, restartApproved, isCloseWnd)
        return

    def __apply(self, settings, restartApproved=False, isCloseWnd=False):
        LOG_DEBUG('Settings window: apply settings', restartApproved, settings)
        self.settingsCore.isDeviseRecreated = False
        self.settingsCore.isChangesConfirmed = True
        isRestart = self.params.apply(settings, restartApproved)
        if settings_constants.GRAPHICS.INTERFACE_SCALE in settings:
            self.__updateInterfaceScale()
        isPresetApplied = self.__isGraphicsPresetApplied(settings)
        if self.settingsCore.isChangesConfirmed and isCloseWnd:
            self.onWindowClose()
        if isRestart:
            BigWorld.savePreferences()
            if restartApproved:
                _delayCall(0.3, self.__restartGame)
            elif self.settingsCore.isDeviseRecreated:
                self.onRecreateDevice()
                self.settingsCore.isDeviseRecreated = False
            else:
                _delayCall(0.0, functools.partial(BigWorld.changeVideoMode, -1, BigWorld.getWindowMode()))
        elif not isPresetApplied:
            DialogsInterface.showI18nInfoDialog('graphicsPresetNotInstalled', None)
        return

    def __restartGame(self):
        BigWorld.savePreferences()
        WGC.notifyRestart()
        BigWorld.worldDrawEnabled(False)
        BigWorld.restartGame()

    def _populate(self):
        super(SettingsWindow, self)._populate()
        dataVO = [{'label': SETTINGS.FEEDBACK_TAB_DAMAGEINDICATOR,
          'linkage': VIEW_ALIAS.FEEDBACK_DAMAGE_INDICATOR},
         {'label': SETTINGS.FEEDBACK_TAB_EVENTSINFO,
          'linkage': VIEW_ALIAS.FEEDBACK_BATTLE_EVENTS},
         {'label': SETTINGS.FEEDBACK_TAB_DAMAGELOGPANEL,
          'linkage': VIEW_ALIAS.FEEDBACK_DAMAGE_LOG},
         {'label': SETTINGS.FEEDBACK_TAB_BATTLEBORDERMAP,
          'linkage': VIEW_ALIAS.FEEDBACK_BATTLE_BORDER_MAP},
         {'label': SETTINGS.FEEDBACK_TAB_QUESTSPROGRESS,
          'linkage': VIEW_ALIAS.FEEDBACK_QUESTS_PROGRESS}]
        self.as_setFeedbackDataProviderS(dataVO)
        if self.__redefinedKeyModeEnabled:
            BigWorld.wg_setRedefineKeysMode(True)
        self.__currentSettings = self.params.getMonitorSettings()
        self._update()
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.anonymizerController.onStateChanged += self.__refreshSettings
        g_guiResetters.add(self.onRecreateDevice)
        BigWorld.wg_setAdapterOrdinalNotifyCallback(self.onRecreateDevice)
        self.__uiNewbieHintsTooltipLogger.initialize()

    def _update(self):
        self.as_setDataS(self.__getSettings())
        newSettings = getNewSettings()
        if newSettings:
            self.as_setCountersDataS(newSettings)
        self.as_updateVideoSettingsS(self.params.getMonitorSettings())
        self.as_openTabS(_getLastTabIndex())
        self.__setColorGradingTechnique()
        self.__setLimitedUISettingVisibility()
        self.__setEventSettingVisibility()

    def _dispose(self):
        if self.__redefinedKeyModeEnabled:
            BigWorld.wg_setRedefineKeysMode(False)
        g_guiResetters.discard(self.onRecreateDevice)
        BigWorld.wg_setAdapterOrdinalNotifyCallback(None)
        self.stopVoicesPreview()
        self.stopAltBulbPreview()
        self.stopArtyBulbPreview()
        self.anonymizerController.onStateChanged -= self.__refreshSettings
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__uiNewbieHintsTooltipLogger.finalize()
        super(SettingsWindow, self)._dispose()
        return

    def onTabSelected(self, tabId):
        if tabId == SETTINGS.SOUNDTITLE:
            self.bwProto.voipController.invalidateInitialization()
        if tabId in _PAGES_INDICES:
            _setLastTabIndex(_PAGES_INDICES[tabId])
        else:
            LOG_WARNING("Unknown settings window's page id", tabId)

    def onCounterTargetVisited(self, tabName, subTabName, controlsIDs):
        isSettingsChanged = invalidateSettings(tabName, subTabName, controlsIDs)
        if isSettingsChanged:
            newSettings = getNewSettings()
            self.as_setCountersDataS(newSettings)

    def onSettingsChange(self, settingName, settingValue):
        settingValue = flashObject2Dict(settingValue)
        LOG_DEBUG('onSettingsChange', settingName, settingValue)
        self.params.preview(settingName, settingValue)

    def applySettings(self, settings, isCloseWnd):
        self._applySettings(flashObject2Dict(settings), isCloseWnd)

    def _applySettings(self, settings, isCloseWnd):
        applyMethod = self.params.getApplyMethod(settings)

        def confirmHandler(isOk):
            if not self.isDisposed():
                self.as_ConfirmationOfApplicationS(isOk)
                if isOk:
                    self.__commitSettings(settings, isOk, isCloseWnd)
                else:
                    self.params.revert()
                if not isCloseWnd:
                    self._update()

        if applyMethod == APPLY_METHOD.RESTART:
            DialogsInterface.showI18nConfirmDialog('graphicsPresetRestartConfirmation', confirmHandler)
        elif applyMethod == APPLY_METHOD.DELAYED:
            DialogsInterface.showI18nConfirmDialog('graphicsPresetDelayedConfirmation', confirmHandler)
        elif applyMethod == APPLY_METHOD.NEXT_BATTLE and self.__isBattleSettings:
            DialogsInterface.showI18nConfirmDialog('nextBattleOptionConfirmation', confirmHandler)
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

    def autodetectAcousticType(self):
        option = self.settingsCore.options.getSetting(settings_constants.SOUND.SOUND_SPEAKERS)
        return option.getSystemPreset()

    def canSelectAcousticType(self, index):
        index = int(index)
        option = self.settingsCore.options.getSetting(settings_constants.SOUND.SOUND_SPEAKERS)
        if not option.isPresetSupportedByIndex(index):

            def _apply(result):
                if not self.isDisposed():
                    LOG_DEBUG('Player result', result)
                    self.as_onSoundSpeakersPresetApplyS(result)

            DialogsInterface.showI18nConfirmDialog('soundSpeakersPresetDoesNotMatch', callback=_apply)
            return False
        return True

    def startVOIPTest(self, isStart):
        LOG_DEBUG('Vivox test: %s' % str(isStart))
        rh = VOIP.getVOIPManager()
        if isStart:
            rh.enterTestChannel()
        else:
            rh.leaveTestChannel()
        return False

    @decorators.adisp_process('updateCaptureDevices')
    def updateCaptureDevices(self):
        yield self.bwProto.voipController.requestCaptureDevices()
        opt = self.settingsCore.options.getSetting(settings_constants.SOUND.CAPTURE_DEVICES)
        self.as_setCaptureDevicesS(opt.get(), opt.getOptions())

    def altVoicesPreview(self):
        setting = self.settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        setting.playPreviewSound()

    def altBulbPreview(self, sampleID):
        setting = self.settingsCore.options.getSetting(settings_constants.SOUND.DETECTION_ALERT_SOUND)
        setting.playPreviewSound(sampleID)

    def artyBulbPreview(self, sampleID):
        setting = self.settingsCore.options.getSetting(settings_constants.SOUND.ARTY_SHOT_ALERT_SOUND)
        setting.playPreviewSound(sampleID)

    def stopVoicesPreview(self):
        setting = self.settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        setting.clearPreviewSound()

    def stopAltBulbPreview(self):
        setting = self.settingsCore.options.getSetting(settings_constants.SOUND.DETECTION_ALERT_SOUND)
        setting.clearPreviewSound()

    def stopArtyBulbPreview(self):
        setting = self.settingsCore.options.getSetting(settings_constants.SOUND.ARTY_SHOT_ALERT_SOUND)
        setting.clearPreviewSound()

    def isSoundModeValid(self):
        setting = self.settingsCore.options.getSetting(settings_constants.SOUND.ALT_VOICES)
        return setting.isSoundModeValid()

    def showWarningDialog(self, dialogID, settings, isCloseWnd):
        ctx = None
        applyMethod = functools.partial(self.applySettings, settings, False)
        if dialogID == SETTINGS_DIALOGS.MINIMAP_ALPHA_NOTIFICATION:
            ctx = {'icon': icons.alert(),
             'alert': makeHtmlString('html_templates:lobby/dialogs', 'minimapAlphaNotification', {'message': backport.text(R.strings.dialogs.minimapAlphaNotification.message.alert())})}
        elif dialogID == SETTINGS_DIALOGS.LIMITED_UI_OFF_NOTIFICATION:
            ctx = {'icon': icons.alert(),
             'alert': makeHtmlString('html_templates:lobby/dialogs', 'limitedUIOffNotification', {'message': backport.text(R.strings.dialogs.limitedUIOffNotification.message.alert())})}
            applyMethod = self.__applyLimitedUISetting

        def callback(isOk):
            if not self.isDisposed():
                if isOk:
                    applyMethod()
                self.as_confirmWarningDialogS(isOk, dialogID)
                if isCloseWnd and isOk:
                    self.onWindowClose()

        DialogsInterface.showI18nConfirmDialog(dialogID, callback, ctx)
        return

    def openGammaWizard(self, x, y, size):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.GAMMA_WIZARD), ctx={'x': x,
         'y': y,
         'size': size}), EVENT_BUS_SCOPE.DEFAULT)

    def openColorSettings(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.COLOR_SETTING)), EVENT_BUS_SCOPE.DEFAULT)

    def restartNewbieBattleHints(self):
        dependency.instance(INewbieBattleHintsController).resetHistory()
        self.__uiNewbieHintsLogger.resetButtonClicked()

    def __updateInterfaceScale(self):
        self.as_updateVideoSettingsS(self.params.getMonitorSettings())

    def __isGraphicsPresetApplied(self, settings):
        allsettings = BigWorld.getGraphicsPresetPropertyNames()
        isGraphicsQualitySettings = False
        for settingKey in settings.iterkeys():
            if settingKey in allsettings:
                isGraphicsQualitySettings = True
                break

        return self.as_isPresetAppliedS() if isGraphicsQualitySettings else True

    def __onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.COLOR_GRADING_TECHNIQUE in diff:
            self.__setColorGradingTechnique(diff.get(settings_constants.GRAPHICS.COLOR_GRADING_TECHNIQUE, None))
        if LIMITED_UI_KEY in diff:
            self.__setLimitedUISettingVisibility()
        self.__uiNewbieHintsLogger.onSettingsChanged(diff)
        return

    def __refreshSettings(self, **_):
        self._update()

    def __setColorGradingTechnique(self, value=None):
        colorSettingsSelectedTab = AccountSettings.getSettings(COLOR_SETTINGS_TAB_IDX)
        if colorSettingsSelectedTab is None or not graphics.isRendererPipelineDeferred():
            colorSettingsSelectedTab = 0
        label = SETTINGS.GRAPHICSSETTINGSOPTIONS_NONE
        image = RES_ICONS.MAPS_ICONS_SETTINGS_COLOR_GRADING_TECHNIQUE_NONE
        if colorSettingsSelectedTab == 2:
            label = SETTINGS.COLORSETTINGS_TAB_CUSTOMSETTINGS
            image = RES_ICONS.MAPS_ICONS_SETTINGS_COLOR_GRADING_TECHNIQUE_RANDOM
        elif colorSettingsSelectedTab == 1:
            setting = self.settingsCore.options.getSetting(settings_constants.GRAPHICS.COLOR_GRADING_TECHNIQUE)
            images = graphics.getGraphicSettingImages(settings_constants.GRAPHICS.COLOR_GRADING_TECHNIQUE)
            label = SETTINGS.GRAPHICSSETTINGSOPTIONS_NONE
            image = None
            filterIdx = setting.get() if value is None else value
            if setting is not None:
                for option in setting.getOptions():
                    currentIdx = option.get('data', 0)
                    if currentIdx == filterIdx:
                        label = option.get('label')
                        image = images.get(option.get('data', 0))
                        break

            if image is None:
                image = RES_ICONS.MAPS_ICONS_SETTINGS_COLOR_GRADING_TECHNIQUE_NONE
        self.as_setColorGradingTechniqueS(image, label)
        return

    def __setLimitedUISettingVisibility(self):
        self.as_showLimitedUISettingS(self.limitedUIController.isUserSettingsMayShow)

    def __setEventSettingVisibility(self):
        self.as_setIsEventS(self.eventBattlesCtrl.isEventBattleActive())

    def __applyLimitedUISetting(self):
        self.limitedUIController.completeAllRulesByTypes(LuiRuleTypes.NOVICE)
        LimitedUILogger().handleClickOnce(LimitedUILogItem.DISABLE_LIMITED_UI_BUTTON, LimitedUILogScreenParent.SETTINGS_WINDOW)
