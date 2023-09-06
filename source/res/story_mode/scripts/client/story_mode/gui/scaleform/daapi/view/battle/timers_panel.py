# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/timers_panel.py
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.impl import backport
from gui.impl.gen import R
_OVERTURNED_LINKAGE = 'StoryModeDestroyTimerUI'
_OVERTURNED_ICON = 'StoryModeOverturnIconUI'
_OVERTURNED_ICON_OFFSET = -20

class StoryModelTimersPanel(TimersPanel):

    def _generateMainTimersData(self):
        return [self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.DROWN, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DROWN_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.DESTROY_TIMER_UI), self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.OVERTURNED, _OVERTURNED_ICON, _OVERTURNED_LINKAGE, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, text=backport.text(R.strings.sm_battle.timersPanel.overturned()), iconOffsetY=_OVERTURNED_ICON_OFFSET)]
