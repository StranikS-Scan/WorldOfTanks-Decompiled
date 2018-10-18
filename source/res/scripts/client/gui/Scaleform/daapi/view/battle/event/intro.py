# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/intro.py
from gui.Scaleform.daapi.view.meta.EventIntroMeta import EventIntroMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE

class EventIntro(EventIntroMeta, IAbstractPeriodView):

    def __init__(self):
        super(EventIntro, self).__init__()
        self.__isVisible = False
        self.__isMapVisible = False
        self.__isHelpVisible = False

    def setState(self, state):
        if not self.__isVisible and state in COUNTDOWN_STATE.VISIBLE:
            self.__hideHud()
            self.__isVisible = True
            self.__updateIntroVisibility()
        elif self.__isVisible and state not in COUNTDOWN_STATE.VISIBLE:
            self.__showHud()
            self.__isVisible = False
            self.__updateIntroVisibility()

    def _populate(self):
        super(EventIntro, self)._populate()
        add = g_eventBus.addListener
        add(events.IngameHelpWindowEvent.POPULATE_WINDOW, self.__onHelpPopulate)
        add(events.IngameHelpWindowEvent.DISPOSE_WINDOW, self.__onHelpDispose)
        add(events.GameEvent.EVENT_MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        remove = g_eventBus.removeListener
        remove(events.IngameHelpWindowEvent.POPULATE_WINDOW, self.__onHelpPopulate)
        remove(events.IngameHelpWindowEvent.DISPOSE_WINDOW, self.__onHelpDispose)
        remove(events.GameEvent.EVENT_MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        super(EventIntro, self)._dispose()

    def __hideHud(self):
        handle = g_eventBus.handleEvent
        handle(events.GameEvent(events.GameEvent.HIDE_HUD_COMPONENTS, {BATTLE_VIEW_ALIASES.EVENT_POINT_CURRENT,
         BATTLE_VIEW_ALIASES.EVENT_HEALTH_BAR,
         BATTLE_VIEW_ALIASES.EVENT_HOT_KEYS_INFO,
         BATTLE_VIEW_ALIASES.EVENT_OBJECTIVES,
         BATTLE_VIEW_ALIASES.EVENT_POINT_COUNTER,
         BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
         BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL}), scope=EVENT_BUS_SCOPE.BATTLE)
        handle(events.GameEvent(events.GameEvent.HIDE_EXTERNAL_COMPONENTS), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __showHud(self):
        handle = g_eventBus.handleEvent
        handle(events.GameEvent(events.GameEvent.SHOW_HUD_COMPONENTS, {BATTLE_VIEW_ALIASES.EVENT_POINT_CURRENT,
         BATTLE_VIEW_ALIASES.EVENT_HEALTH_BAR,
         BATTLE_VIEW_ALIASES.EVENT_HOT_KEYS_INFO,
         BATTLE_VIEW_ALIASES.EVENT_OBJECTIVES,
         BATTLE_VIEW_ALIASES.EVENT_POINT_COUNTER,
         BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
         BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL}), scope=EVENT_BUS_SCOPE.BATTLE)
        handle(events.GameEvent(events.GameEvent.SHOW_EXTERNAL_COMPONENTS), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __onHelpPopulate(self, _):
        self.__isHelpVisible = True
        self.__updateIntroVisibility()

    def __onHelpDispose(self, _):
        self.__isHelpVisible = False
        self.__updateIntroVisibility()

    def __handleMinimapCmd(self, event):
        self.__isMapVisible = event.ctx['isDown']
        self.__updateIntroVisibility()

    def __updateIntroVisibility(self):
        if self.__isVisible and not self.__isMapVisible and not self.__isHelpVisible:
            self.as_showS()
        else:
            self.as_hideS()
