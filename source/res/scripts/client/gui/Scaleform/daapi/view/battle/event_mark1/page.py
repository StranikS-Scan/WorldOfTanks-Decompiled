# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/page.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.classic import ClassicPage
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control import g_sessionProvider
from gui.Scaleform.daapi.view.battle.event_mark1.delivery_direction import DeliveryDirection
_MARK1_COMPONENTS_TO_CTRLS = ((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
   BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MARK1_BONUS, (BATTLE_VIEW_ALIASES.FLAG_NOTIFICATION,)),
 (BATTLE_CTRL_ID.MARK1_EVENT_NOTS, (BATTLE_VIEW_ALIASES.EVENT_NOTIFICATION_PANEL,)))

class EventMark1Page(ClassicPage):

    def __init__(self, components=_MARK1_COMPONENTS_TO_CTRLS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        super(EventMark1Page, self).__init__(components=components, fullStatsAlias=fullStatsAlias)
        self.__markIDirection = None
        return

    def __del__(self):
        LOG_DEBUG('EventMark1Page is deleted')

    def _populate(self):
        super(EventMark1Page, self)._populate()
        self.__markIDirection = DeliveryDirection()
        vehicleCtrl = g_sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onRespawnBaseMoving += self.__onRrespawnBaseMoving
        return

    def _dispose(self):
        vehicleCtrl = g_sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onRespawnBaseMoving -= self.__onRrespawnBaseMoving
        if self.__markIDirection is not None:
            self.__markIDirection.clear()
            self.__markIDirection = None
        super(EventMark1Page, self)._dispose()
        return

    def __onRrespawnBaseMoving(self):
        self._toggleRadialMenu(False)
