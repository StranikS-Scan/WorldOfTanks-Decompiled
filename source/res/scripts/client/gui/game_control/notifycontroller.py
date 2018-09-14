# Embedded file name: scripts/client/gui/game_control/NotifyController.py
import cPickle
import base64
from collections import namedtuple
import BigWorld
import Settings
from adisp import async, process
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.decorators import sf_lobby
from gui.game_control.controllers import Controller
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.utils import graphics
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
_GRAPHICS_SETTINGS_TAB_IDX = 1
_Settings = namedtuple('_Settings', ['presetChangingVersion', 'lastBattleAvgFps'])

class NotifyController(Controller):
    LOW_FPS_VALUE = 20
    CURRENT_LOW_FPS_WARNING_VERSION = 1
    MIN_BATTLE_LENGHT = 180

    def __init__(self, proxy):
        super(NotifyController, self).__init__(proxy)
        self.__graphicsResetShown = False
        self.__settings = _Settings(0, None)
        return

    @sf_lobby
    def app(self):
        return None

    def init(self):
        self.__readSettings()
        self._startUIListening()
        self._startPlayingTimeListening()

    def fini(self):
        self._stopUIListening()
        self._stopPlayingTimeListening()
        self.__writeSettings()
        super(NotifyController, self).fini()

    def updateBattleFpsInfo(self, avgBattleFps, battlePlayingTime):
        LOG_DEBUG('Updating battle fps info', avgBattleFps, battlePlayingTime)
        if battlePlayingTime >= self.MIN_BATTLE_LENGHT:
            self.__settings = self.__settings._replace(lastBattleAvgFps=avgBattleFps)

    def _startUIListening(self):
        g_eventBus.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleUiUpdated, scope=EVENT_BUS_SCOPE.LOBBY)

    def _startPlayingTimeListening(self):
        g_eventBus.addListener(events.GameEvent.PLAYING_TIME_ON_ARENA, self.__handlePlayingTimeOnArena, scope=EVENT_BUS_SCOPE.BATTLE)

    def _stopUIListening(self):
        g_eventBus.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleUiUpdated, scope=EVENT_BUS_SCOPE.LOBBY)

    def _stopPlayingTimeListening(self):
        g_eventBus.removeListener(events.GameEvent.PLAYING_TIME_ON_ARENA, self.__handlePlayingTimeOnArena, scope=EVENT_BUS_SCOPE.BATTLE)

    @process
    def __handleUiUpdated(self, _):
        self._stopUIListening()
        yield lambda callback: callback(True)
        from gui.battle_control import g_sessionProvider
        if g_sessionProvider.getCtx().wasInBattle:
            return
        graphicsStatus = graphics.getStatus()
        if not self.__graphicsResetShown and graphicsStatus.isReset():
            isOk = yield self.__showI18nDialog('resetGraphics')
            self.__graphicsResetShown = True
            if isOk:
                self.__showSettingsWindow(_GRAPHICS_SETTINGS_TAB_IDX)
        elif graphicsStatus.isShowWarning():
            self.__showSettingsWindow(_GRAPHICS_SETTINGS_TAB_IDX)
            isOk = yield self.__showI18nDialog('changeGraphics')
            if isOk:
                self.__updatePresetSetting()
        elif self.__isNeedToShowPresetChangingDialog():
            self.__showSettingsWindow(_GRAPHICS_SETTINGS_TAB_IDX)
            isOk = yield self.__showI18nDialog('lowFpsWarning')
            if isOk:
                BigWorld.callback(0.001, lambda : self.__downgradePresetIndex())
            else:
                self.__updateLowFpsDialogVersion()
        graphicsStatus.markProcessed()
        self.__clearCurrentFpsInfo()

    def __handlePlayingTimeOnArena(self, event):
        ctx = event.ctx
        if 'time' in ctx:
            playingTime = ctx['time']
        else:
            LOG_ERROR('Playing time is not found', event.ctx)
            return
        avgBattleFps = BigWorld.getBattleFPS()[2]
        LOG_DEBUG('Updating battle fps info', avgBattleFps, playingTime)
        if playingTime >= self.MIN_BATTLE_LENGHT:
            self.__settings = self.__settings._replace(lastBattleAvgFps=avgBattleFps)

    @async
    def __showI18nDialog(self, key, callback):
        from gui import DialogsInterface
        return DialogsInterface.showI18nConfirmDialog(key, callback)

    @classmethod
    def __showSettingsWindow(cls, tabIdx = 0):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.SETTINGS_WINDOW, ctx={'redefinedKeyMode': False,
         'tabIndex': tabIdx}))

    def __getSettingsWindow(self):
        from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
        windowContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        return windowContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.SETTINGS_WINDOW})

    def __closeSettingsWindow(self):
        window = self.__getSettingsWindow()
        if window is not None:
            window.onWindowClose()
        return

    def __updatePresetSetting(self, presetIdx = None):
        window = self.__getSettingsWindow()
        if window is not None:
            if presetIdx is None:
                presetIdx = window.autodetectQuality()
            window.as_setGraphicsPresetS(presetIdx)
        return

    @classmethod
    def __getGraphicsPresetSetting(cls):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        from account_helpers.settings_core.settings_constants import GRAPHICS
        return g_settingsCore.options.getSetting(GRAPHICS.PRESETS)

    def __downgradePresetIndex(self):
        presetSetting = self.__getGraphicsPresetSetting()
        nextPresetToApply = presetSetting.get() + 1
        if nextPresetToApply < len(graphics.getGraphicsPresetsIndices()):
            self.__updatePresetSetting(nextPresetToApply)
            window = self.__getSettingsWindow()
            if window is not None:
                for opt in presetSetting.getOptions():
                    if opt['index'] == nextPresetToApply:
                        return window._applySettings(opt['settings'], True)

        return

    def __isNeedToShowPresetChangingDialog(self):
        avgFps = self.__settings.lastBattleAvgFps
        presetSetting = self.__getGraphicsPresetSetting()
        isCustomPreset = presetSetting.isCustom()
        canToDowngradePreset = presetSetting.get() < len(graphics.getGraphicsPresetsIndices()) - 1
        return avgFps and avgFps <= self.LOW_FPS_VALUE and not isCustomPreset and canToDowngradePreset and self.__settings.presetChangingVersion < self.CURRENT_LOW_FPS_WARNING_VERSION

    def __clearCurrentFpsInfo(self):
        self.__settings = self.__settings._replace(lastBattleAvgFps=None)
        self.__writeSettings()
        return

    def __updateLowFpsDialogVersion(self):
        self.__settings = self.__settings._replace(presetChangingVersion=self.CURRENT_LOW_FPS_WARNING_VERSION)
        self.__writeSettings()

    def __readSettings(self):
        try:
            self.__settings = self.__settings._replace(**cPickle.loads(base64.b64decode(Settings.g_instance.userPrefs[Settings.KEY_GUI_NOTIFY_INFO].readString(''))))
        except Exception as msg:
            LOG_DEBUG('There is error while reading gui notifying settings', msg)

    def __writeSettings(self):
        Settings.g_instance.userPrefs.write(Settings.KEY_GUI_NOTIFY_INFO, base64.b64encode(cPickle.dumps(self.__settings._asdict())))
