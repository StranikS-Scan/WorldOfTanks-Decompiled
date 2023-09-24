# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/status_notifications/panel.py
import logging
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
_logger = logging.getLogger(__name__)

class _EventHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_EventHighPriorityGroup, self).__init__((sn_items.FireSN,), updateCallback)


class EventStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_EventHighPriorityGroup, sn_items.StaticDeathZoneSN, sn_items.StunSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(EventStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        link = _LINKS.STATUS_NOTIFICATION_TIMER
        self._addNotificationTimerSetting(data, _TYPES.SECTOR_AIRSTRIKE, _LINKS.AIRSTRIKE_ICON, link, iconSmallName='secondaryAirStrikeUI', color=_COLORS.YELLOW, descriptionFontSize=24, descriptionOffsetY=10)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.STUN_ICON, link)
        return data
