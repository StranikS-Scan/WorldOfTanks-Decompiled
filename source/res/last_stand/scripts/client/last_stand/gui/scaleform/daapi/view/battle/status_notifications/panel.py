# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/status_notifications/panel.py
import logging
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from last_stand.gui.scaleform.genConsts.LS_BATTLE_NOTIFICATIONS_TIMER_TYPES import LS_BATTLE_NOTIFICATIONS_TIMER_TYPES as _LSTYPES
from last_stand.gui.scaleform.genConsts.LS_NOTIFICATION_TIMER_ALIASES import LS_NOTIFICATION_TIMER_ALIASES as _LSLINKS
from last_stand.gui.scaleform.daapi.view.battle.status_notifications import sn_items as _LS_SW_ITEMS
_logger = logging.getLogger(__name__)

class _LSHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_LSHighPriorityGroup, self).__init__((_LS_SW_ITEMS.LSStaticDeathZoneSN, sn_items.FireSN, sn_items.DrownSN), updateCallback)


class LSStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_LSHighPriorityGroup,
         _LS_SW_ITEMS.LSPersonalDeathZoneSN,
         _LS_SW_ITEMS.LSHalfOverturnedSN,
         sn_items.StunSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(LSStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _LSTYPES.LS_DEATH_ZONE, _LSLINKS.LS_DEATH_ZONE, link, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.STUN_ICON, link, _COLORS.ORANGE, noiseVisible=True)
        link = _LINKS.STATUS_NOTIFICATION_TIMER
        self._addNotificationTimerSetting(data, _LSTYPES.LS_PERSONAL_DEATH_ZONE, _LSLINKS.LS_PERSONAL_DEATH_ZONE, link, iconOffsetY=-8, iconSmallName=_LSLINKS.LS_PERSONAL_DEATH_ZONE_SMALL, color=_COLORS.ORANGE_WARNING, descriptionFontSize=16, descriptionOffsetY=-2)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, _LINKS.HALF_OVERTURNED_ICON, link, iconOffsetY=-8, iconSmallName=_LSLINKS.LS_HALF_OVERTURN_SMALL, color=_COLORS.GREEN, descriptionFontSize=16, descriptionOffsetY=-2)
        return data
