# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/status_notifications/panel.py
import typing
from gui.Scaleform.daapi.view.battle.pve_base.status_notifications.panel import PveStatusNotificationTimerPanel
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS as _COLORS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKAGES
from story_mode.gui.scaleform.daapi.view.battle.status_notifications.sn_items import ReconAbilitySN, DisableShotSN
from story_mode.gui.scaleform.genConsts.STORY_MODE_NOTIFICATIONS_TIMER_TYPES import STORY_MODE_NOTIFICATIONS_TIMER_TYPES as _SM_TYPES
_ENGINE_ICON = 'reconTimerEngineUI'
_DESTROY_TIMER_LINKAGE = 'StoryModeDestroyTimerUI'

class StoryModeStatusNotificationTimerPanel(PveStatusNotificationTimerPanel):

    def _generateItems(self):
        items = super(StoryModeStatusNotificationTimerPanel, self)._generateItems()
        items.extend([ReconAbilitySN, DisableShotSN])
        return items

    def _generateNotificationTimerSettings(self):
        data = super(StoryModeStatusNotificationTimerPanel, self)._generateNotificationTimerSettings()
        self._addNotificationTimerSetting(data, _SM_TYPES.RECON_ABILITY, _ENGINE_ICON, _DESTROY_TIMER_LINKAGE, color=_COLORS.GREEN)
        self._addNotificationTimerSetting(data, _SM_TYPES.SCC_DISABLE_SHOT, _LINKAGES.THUNDER_STRIKE_ICON, _LINKAGES.SECONDARY_TIMER_UI, _COLORS.ORANGE, noiseVisible=True)
        return data
