# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/battle/status_notifications/panel.py
import logging
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.status_notifications import sn_items
from gui.Scaleform.daapi.view.battle.shared.status_notifications import components
from gui.Scaleform.daapi.view.battle.shared.status_notifications.panel import StatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TYPES
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import PROGRESS_CIRCLE_TYPE
from gui.Scaleform.daapi.view.battle.epic.status_notifications.sn_items import ResupplyTimerSN
_logger = logging.getLogger(__name__)

class _FunRandomHighPriorityGroup(components.StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(_FunRandomHighPriorityGroup, self).__init__((sn_items.OverturnedSN,
         sn_items.HalfOverturnedSN,
         sn_items.DrownSN,
         sn_items.UnderFireSN,
         sn_items.FireSN), updateCallback)


class FunRandomStatusNotificationTimerPanel(StatusNotificationTimerPanel):

    def _generateItems(self):
        items = [_FunRandomHighPriorityGroup,
         FunRandomResupplyTimer,
         sn_items.StunSN,
         sn_items.StunFlameSN]
        return items

    def _generateNotificationTimerSettings(self):
        data = super(FunRandomStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        liftOverEnabled = ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arenaBonusType, ARENA_BONUS_TYPE_CAPS.LIFT_OVER)
        if liftOverEnabled:
            overturnedIcon = _LINKS.OVERTURNED_GREEN_ICON
            overturnedColor = _COLORS.GREEN
            iconOffsetY = 1
        else:
            overturnedIcon = _LINKS.OVERTURNED_ICON
            overturnedColor = _COLORS.ORANGE
            iconOffsetY = 0
        link = _LINKS.DESTROY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.DROWN, _LINKS.DROWN_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        self._addNotificationTimerSetting(data, _TYPES.FIRE, _LINKS.FIRE_ICON, link)
        self._addNotificationTimerSetting(data, _TYPES.HALF_OVERTURNED, overturnedIcon, link, color=overturnedColor, iconOffsetY=iconOffsetY)
        link = _LINKS.SECONDARY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.STUN, _LINKS.STUN_ICON, link, _COLORS.ORANGE, noiseVisible=True, text=INGAME_GUI.STUN_INDICATOR)
        self._addNotificationTimerSetting(data, _TYPES.STUN_FLAME, _LINKS.STUN_FLAME_ICON, link, _COLORS.ORANGE, noiseVisible=True, text=INGAME_GUI.STUNFLAME_INDICATOR)
        link = _LINKS.RESUPPLY_TIMER_UI
        self._addNotificationTimerSetting(data, _TYPES.RESUPPLY, _LINKS.RESUPPLY_TIMER_UI, link)
        return data


class FunRandomResupplyTimer(ResupplyTimerSN):

    def _onVehicleEntered(self, circleType, pointIdx, state):
        self._setVisible(True)
        super(FunRandomResupplyTimer, self)._onVehicleEntered(circleType, pointIdx, state)

    def _getTitle(self, _):
        return backport.text(R.strings.fun_random.battle.timer.title())

    def _onProgressUpdate(self, circleType, _, value):
        if circleType is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        valueStr = str(value)
        titleText = backport.text(R.strings.fun_random.battle.timer.repairing())
        additionalInfoText = backport.text(R.strings.fun_random.battle.timer.repairingPercentage(), amount=valueStr)
        super(FunRandomResupplyTimer, self)._applyText(titleText, additionalInfoText)
        self._sendUpdate()

    def _applyText(self, title='', additionalInfoText=''):
        state = self._vo['additionalState']
        additionalInfoText = additionalInfoText
        titleText = self._getTitle(None)
        if state == EPIC_CONSTS.RESUPPLY_FULL:
            additionalInfoText = backport.text(R.strings.fun_random.battle.timer.repairingDone())
        elif state == EPIC_CONSTS.RESUPPLY_BLOCKED:
            additionalInfoText = backport.text(R.strings.fun_random.battle.timer.repairingBlocked())
        elif state == EPIC_CONSTS.RESUPPLY_READY:
            additionalInfoText = backport.text(R.strings.fun_random.battle.timer.repairing())
        super(FunRandomResupplyTimer, self)._applyText(titleText, additionalInfoText)
        return
