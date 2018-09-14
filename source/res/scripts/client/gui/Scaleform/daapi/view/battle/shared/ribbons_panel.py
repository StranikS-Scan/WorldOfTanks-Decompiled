# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ribbons_panel.py
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.settings_constants import GAME
from gui.Scaleform.daapi.view.meta.RibbonsPanelMeta import RibbonsPanelMeta
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from helpers import i18n
_FEEDBACK_EVENT_TO_BATTLE_EFFICIENCY = {FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY: BATTLE_EFFICIENCY_TYPES.DESTRUCTION,
 FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY: BATTLE_EFFICIENCY_TYPES.DAMAGE,
 FEEDBACK_EVENT_ID.PLAYER_DAMAGED_DEVICE_ENEMY: BATTLE_EFFICIENCY_TYPES.CRITS,
 FEEDBACK_EVENT_ID.PLAYER_SPOTTED_ENEMY: BATTLE_EFFICIENCY_TYPES.DETECTION,
 FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY: BATTLE_EFFICIENCY_TYPES.ASSIST,
 FEEDBACK_EVENT_ID.PLAYER_USED_ARMOR: BATTLE_EFFICIENCY_TYPES.ARMOR,
 FEEDBACK_EVENT_ID.PLAYER_CAPTURED_BASE: BATTLE_EFFICIENCY_TYPES.CAPTURE,
 FEEDBACK_EVENT_ID.PLAYER_DROPPED_CAPTURE: BATTLE_EFFICIENCY_TYPES.DEFENCE}
_RIBBON_SOUNDS_ENABLED = True
_SHOW_RIBBON_SOUND_NAME = 'show_ribbon'
_HIDE_RIBBON_SOUND_NAME = 'hide_ribbon'
_INC_COUNTER_SOUND_NAME = 'increment_ribbon_counter'

class BattleRibbonsPanel(RibbonsPanelMeta):

    def __init__(self):
        super(BattleRibbonsPanel, self).__init__()
        self.__enabled = False
        self.__offsetX = 0

    def onShow(self):
        self.__playSound(_SHOW_RIBBON_SOUND_NAME)

    def onChange(self):
        self.__playSound(_SHOW_RIBBON_SOUND_NAME)

    def onIncCount(self):
        self.__playSound(_INC_COUNTER_SOUND_NAME)

    def onHide(self):
        self.__playSound(_HIDE_RIBBON_SOUND_NAME)

    def _populate(self):
        super(BattleRibbonsPanel, self)._populate()
        self.__enabled = bool(g_settingsCore.getSetting(GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS))
        self.as_setupS(self.__enabled, _RIBBON_SOUNDS_ENABLED)
        self.__addListeners()

    def _dispose(self):
        self.__removeListeners()
        super(BattleRibbonsPanel, self)._dispose()

    def __playSound(self, eventName):
        if not _RIBBON_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __addListeners(self):
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
        ctrl = g_sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
            self.__onCrosshairPositionChanged(*ctrl.getPosition())
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        return

    def __removeListeners(self):
        ctrl = g_sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
        ctrl = g_sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairPositionChanged -= self.__onCrosshairPositionChanged
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        return

    def __onCrosshairPositionChanged(self, x, y):
        xOffset = int(x)
        if self.__offsetX != xOffset:
            self.__offsetX = xOffset
            self.as_setOffsetXS(xOffset)

    def __onPlayerFeedbackReceived(self, eventID, series):
        if self.__enabled and eventID in _FEEDBACK_EVENT_TO_BATTLE_EFFICIENCY:
            effType = _FEEDBACK_EVENT_TO_BATTLE_EFFICIENCY[eventID]
            effShortDesc = i18n.makeString('#ingame_gui:efficiencyRibbons/{0:>s}'.format(effType))
            self.as_addBattleEfficiencyEventS(effType, effShortDesc, series)

    def __onSettingsChanged(self, diff):
        key = GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS
        if key in diff:
            self.__enabled = bool(diff[key])
            self.as_setupS(self.__enabled, _RIBBON_SOUNDS_ENABLED)
