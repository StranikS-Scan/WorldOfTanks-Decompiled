# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_battle_hint.py
from functools import partial
import BigWorld
import GUI
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import i18n
from shared_utils import BoundMethodWeakref
from gui.Scaleform.locale.EVENT import EVENT
from gui.Scaleform.genConsts.EVENT_BATTLE_HINT_TYPES import EVENT_BATTLE_HINT_TYPES
from gui.Scaleform.daapi.view.meta.EventBattleHintMeta import EventBattleHintMeta
from gui.battle_control.controllers.battle_hints_ctrl import IBattleHintComponent

class EventBattleHint(IBattleHintComponent, EventBattleHintMeta):

    def __init__(self):
        super(EventBattleHint, self).__init__()
        self.__hideCallback = None
        self.__hintHandlers = {EVENT_BATTLE_HINT_TYPES.POINTS_LOST: partial(BoundMethodWeakref(self._showHeaderMessageHint), EVENT_BATTLE_HINT_TYPES.POINTS_LOST, 5.0, 1.5, i18n.makeString(EVENT.BATTLEHINT_YOUDIED), i18n.makeString(EVENT.BATTLEHINT_POINTSLOST), {BATTLE_VIEW_ALIASES.EVENT_POINT_CURRENT,
                                               BATTLE_VIEW_ALIASES.EVENT_HEALTH_BAR,
                                               BATTLE_VIEW_ALIASES.EVENT_HOT_KEYS_INFO,
                                               BATTLE_VIEW_ALIASES.EVENT_OBJECTIVES,
                                               BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
                                               BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
                                               BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL,
                                               BATTLE_VIEW_ALIASES.RADIAL_MENU}, 'halloween_souls_lost'),
         EVENT_BATTLE_HINT_TYPES.POINTS_SAVED: partial(BoundMethodWeakref(self._showSimpleHint), EVENT_BATTLE_HINT_TYPES.POINTS_SAVED, 5.0, i18n.makeString(EVENT.BATTLEHINT_POINTSSAVED), 'halloween_souls_saved'),
         EVENT_BATTLE_HINT_TYPES.TOTAL_POINTS_SAVED: partial(BoundMethodWeakref(self._showHeaderMessageHint), EVENT_BATTLE_HINT_TYPES.TOTAL_POINTS_SAVED, 0.0, 1.5, i18n.makeString(EVENT.BATTLEHINT_TIMEISUP), i18n.makeString(EVENT.BATTLEHINT_TOTALPOINTSSAVED), {BATTLE_VIEW_ALIASES.EVENT_POINT_CURRENT,
                                                      BATTLE_VIEW_ALIASES.EVENT_HEALTH_BAR,
                                                      BATTLE_VIEW_ALIASES.EVENT_HOT_KEYS_INFO,
                                                      BATTLE_VIEW_ALIASES.EVENT_OBJECTIVES,
                                                      BATTLE_VIEW_ALIASES.BATTLE_TIMER,
                                                      BATTLE_VIEW_ALIASES.EVENT_POINT_COUNTER,
                                                      BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
                                                      BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
                                                      BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL,
                                                      BATTLE_VIEW_ALIASES.RADIAL_MENU}, None)}
        self.__visibilityHelper = _VisibilityHelper()
        return

    def closeHint(self):
        if self.__hideCallback:
            BigWorld.cancelCallback(self.__hideCallback)
        self.__hideHint()
        self.as_closeHintS()

    def _getHintHandler(self, hintType):
        return self.__hintHandlers.get(hintType)

    def _showSimpleHint(self, hintType, duration, message, soundName, data):
        vo = {'message': message,
         'count': str(data.get('count', 0))}
        self.app.soundManager.playEffectSound(soundName)
        self.__showHint(hintType, duration, vo)

    def _showHeaderMessageHint(self, hintType, duration, hideComponentsDelay, header, message, hideComponents, soundName, data):
        vo = {'header': header,
         'message': message,
         'count': str(data.get('count', 0))}
        self.app.soundManager.playEffectSound(soundName)
        self.__showHint(hintType, duration, vo)
        self.__visibilityHelper.hideComponents(hideComponents, hideComponentsDelay)

    def __showHint(self, hintType, duration, vo):
        if self.__hideCallback:
            BigWorld.cancelCallback(self.__hideCallback)
            self.__hideHint()
        self.as_showHintS(hintType, vo)
        if duration > 0.0:
            self.__hideCallback = BigWorld.callback(duration, self.__hideHint)

    def __hideHint(self):
        self.as_hideHintS()
        self.__visibilityHelper.resetComponents()
        self.__hideCallback = None
        return


class _VisibilityHelper(object):

    def __init__(self):
        self.__components = None
        self.__hideCallback = None
        self.__isHidden = False
        return

    def hideComponents(self, components, waitTime):
        self.resetComponents()
        self.__components = components
        self.__hideCallback = BigWorld.callback(waitTime, self.__hide)

    def resetComponents(self):
        if self.__isHidden:
            self.__show()
        elif self.__hideCallback:
            BigWorld.cancelCallback(self.__hideCallback)
            self.__hideCallback = None
            self.__components = None
        return

    def __hide(self):
        GUI.WGUIBackgroundBlur().enable = True
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.HIDE_HUD_COMPONENTS, ctx=self.__components), scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.HIDE_EXTERNAL_COMPONENTS), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__hideCallback = None
        self.__isHidden = True
        return

    def __show(self):
        GUI.WGUIBackgroundBlur().enable = False
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.SHOW_HUD_COMPONENTS, ctx=self.__components), scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.SHOW_EXTERNAL_COMPONENTS), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__components = None
        self.__isHidden = False
        return
