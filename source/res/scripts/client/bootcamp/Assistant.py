# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/Assistant.py
import BigWorld
from debug_utils_bootcamp import LOG_CURRENT_EXCEPTION_BOOTCAMP
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from hints.HintsSystem import HintSystem
from BootCampEvents import g_bootcampEvents
from BootcampSettings import getBattleSettings
from BootcampConstants import UI_STATE
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

class BaseAssistant(object):
    ASSISTANT_TICK_LENGTH = 0.2

    def __init__(self, hintSystem):
        super(BaseAssistant, self).__init__()
        self._hintSystem = hintSystem
        self._updateTimerId = None
        return

    def start(self):
        self._hintSystem.start()
        self._updateTimerId = BigWorld.callback(BaseAssistant.ASSISTANT_TICK_LENGTH, self._update)
        self._doStart()

    def stop(self):
        self._doStop()
        if self._updateTimerId is not None:
            BigWorld.cancelCallback(self._updateTimerId)
            self._updateTimerId = None
        self._hintSystem.stop()
        return

    def onAction(self, actionId, actionParams):
        self._hintSystem.onAction(actionId, actionParams)

    def getHintSystem(self):
        return self._hintSystem

    def _update(self):
        try:
            self._hintSystem.update()
        except Exception:
            LOG_CURRENT_EXCEPTION_BOOTCAMP()

        self._updateTimerId = BigWorld.callback(BaseAssistant.ASSISTANT_TICK_LENGTH, self._update)

    def _doStart(self):
        pass

    def _doStop(self):
        pass


class BattleAssistant(BaseAssistant):
    ASSISTANT_TIMEOUT_HIGHLIGHT = 10.0
    ASSISTANT_CLOSE_PREBATTLE = 3.0
    HIGHLIGHTED_GUI_DICT = {'Minimap': BATTLE_VIEW_ALIASES.MINIMAP,
     'MinimapAppear': BATTLE_VIEW_ALIASES.MINIMAP,
     'FragCorrelationBar': BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR,
     'ConsumableSlot4': BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
     'ConsumableSlot5': BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
     'ConsumableSlot6': BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
     'ConsumablesAppear': BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL}

    def __init__(self, avatar, lessonId, entities, bootcampGui, soundAssistant):
        lessonSettings = getBattleSettings(lessonId)
        super(BattleAssistant, self).__init__(HintSystem(avatar, lessonSettings.hints))
        self.__idHighlight = None
        self.__lessonId = lessonId
        self.__idClosePrebattleTimer = None
        self.__soundAssistant = soundAssistant
        self.__highlightedElements = set()
        for animationName, panelName in BattleAssistant.HIGHLIGHTED_GUI_DICT.iteritems():
            curPanels = lessonSettings.visiblePanels
            if lessonId > 0:
                prevPanels = getBattleSettings(lessonId - 1).visiblePanels
                if panelName not in prevPanels and panelName in curPanels:
                    self.__highlightedElements.add(animationName)
            if panelName in curPanels:
                self.__highlightedElements.add(animationName)

        markers = {}
        if hasattr(avatar, 'arenaExtraData'):
            if 'markers' in avatar.arenaExtraData:
                markers = avatar.arenaExtraData['markers']
        from BootcampMarkers import BootcampMarkersManager
        self._markerManager = BootcampMarkersManager()
        self._markerManager.init(entities, markers, bootcampGui)
        g_bootcampEvents.onUIStateChanged += self._onUIStateChanged
        return

    @property
    def combatSound(self):
        return self.__soundAssistant

    def getMarkers(self):
        return self._markerManager

    def _update(self):
        super(BattleAssistant, self)._update()
        try:
            self._markerManager.update()
            g_bootcampEvents.onUIStateChanged(UI_STATE.UPDATE)
        except Exception:
            LOG_CURRENT_EXCEPTION_BOOTCAMP()

    def _doStart(self):
        self._markerManager.start()

    def __doHighlight(self):
        for name in self.__highlightedElements:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_ADD_HIGHLIGHT), ctx=name), EVENT_BUS_SCOPE.BATTLE)
            g_bootcampEvents.onHighlightAdded(self.HIGHLIGHTED_GUI_DICT[name])

        self.__idHighlight = None
        self.__highlightedElements.clear()
        return

    def _onUIStateChanged(self, state):
        if state == UI_STATE.START:
            self.__idHighlight = BigWorld.callback(BattleAssistant.ASSISTANT_TIMEOUT_HIGHLIGHT, self.__doHighlight)
            prebattle = getBattleSettings(self.__lessonId).prebattle
            if prebattle.has_key('visible_hints'):
                g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_PREBATTLE_HITNS), ctx=prebattle), EVENT_BUS_SCOPE.BATTLE)
                self.__idClosePrebattleTimer = BigWorld.callback(prebattle['timeout'], self.__onClosePrebattle)
        elif state == UI_STATE.STOP:
            self.stop()

    def _doStop(self):
        self._markerManager.stop()
        self._markerManager.clear()
        g_bootcampEvents.onUIStateChanged -= self._onUIStateChanged
        if self.__idHighlight is not None:
            BigWorld.cancelCallback(self.__idHighlight)
            self.__idHighlight = None
        if self.__idClosePrebattleTimer is not None:
            BigWorld.cancelCallback(self.__idClosePrebattleTimer)
            self.__idClosePrebattleTimer = None
        return

    def __onClosePrebattle(self):
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_CLOSE_PREBATTLE)), EVENT_BUS_SCOPE.BATTLE)
        self.__idClosePrebattleTimer = None
        return


class LobbyAssistant(BaseAssistant):

    def __init__(self, hints):
        super(LobbyAssistant, self).__init__(HintSystem(hintsInfo=hints))
