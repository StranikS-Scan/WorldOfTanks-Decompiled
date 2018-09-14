# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/BattleRibbonsPanel.py
from account_helpers.settings_core.settings_constants import GAME
from gui.battle_control import g_sessionProvider, avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from helpers import i18n
from debug_utils import LOG_ERROR
from account_helpers.settings_core.SettingsCore import g_settingsCore
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
_FEEDBACK_EVENT_TO_BATTLE_EFFICIENCY = {FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY: BATTLE_EFFICIENCY_TYPES.DESTRUCTION,
 FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY: BATTLE_EFFICIENCY_TYPES.DAMAGE,
 FEEDBACK_EVENT_ID.PLAYER_DAMAGED_DEVICE_ENEMY: BATTLE_EFFICIENCY_TYPES.CRITS,
 FEEDBACK_EVENT_ID.PLAYER_SPOTTED_ENEMY: BATTLE_EFFICIENCY_TYPES.DETECTION,
 FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY: BATTLE_EFFICIENCY_TYPES.ASSIST,
 FEEDBACK_EVENT_ID.PLAYER_USED_ARMOR: BATTLE_EFFICIENCY_TYPES.ARMOR,
 FEEDBACK_EVENT_ID.PLAYER_CAPTURED_BASE: BATTLE_EFFICIENCY_TYPES.CAPTURE,
 FEEDBACK_EVENT_ID.PLAYER_DROPPED_CAPTURE: BATTLE_EFFICIENCY_TYPES.DEFENCE}
_AIM_MODE_TO_RADIUS = {'arcade': 120,
 'strategic': 260,
 'sniper': 200,
 'postmortem': 230}
_RIBBON_SOUNDS_ENABLED = True
_SHOW_RIBBON_SOUND_NAME = 'show_ribbon'
_HIDE_RIBBON_SOUND_NAME = 'hide_ribbon'
_INC_COUNTER_SOUND_NAME = 'increment_ribbon_counter'
_POS_COEFF = (1.0, 1.0)

class BattleRibbonsPanel(object):

    def __init__(self, parentUI):
        self.__ui = parentUI
        self.__enabled = False

    def start(self):
        self.__flashObject = self.__ui.getMember('_level0.ribbonsPanel')
        self.__enabled = bool(g_settingsCore.getSetting(GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS))
        if self.__flashObject:
            self.__flashObject.resync()
            self.__flashObject.script = self
            self.__flashObject.setup(self.__enabled, _RIBBON_SOUNDS_ENABLED, *_POS_COEFF)
            self.__addListeners()
        else:
            LOG_ERROR('Display object is not found in the swf file.')

    def destroy(self):
        self.__removeListeners()
        self.__ui = None
        if self.__flashObject is not None:
            self.__flashObject.script = None
            self.__flashObject = None
        return

    def onShow(self, type, count):
        self.__playSound(_SHOW_RIBBON_SOUND_NAME)

    def onChange(self, type, count):
        self.__playSound(_SHOW_RIBBON_SOUND_NAME)

    def onIncCount(self, type, count):
        self.__playSound(_INC_COUNTER_SOUND_NAME)

    def onHide(self, type):
        self.__playSound(_HIDE_RIBBON_SOUND_NAME)

    def __playSound(self, eventName):
        if not _RIBBON_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __addListeners(self):
        feedback = g_sessionProvider.getFeedback()
        if feedback:
            feedback.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
            feedback.onAimPositionUpdated += self.__onAimPositionUpdated
            props = feedback.getAimProps()
            if props and len(props) > 2:
                self.__onAimPositionUpdated(*props[:3])
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged

    def __removeListeners(self):
        feedback = g_sessionProvider.getFeedback()
        if feedback:
            feedback.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
            feedback.onAimPositionUpdated -= self.__onAimPositionUpdated
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def __onAimPositionUpdated(self, mode, x, y):
        if not self.__ui:
            return
        if mode not in _AIM_MODE_TO_RADIUS:
            LOG_ERROR('Value of radius is not defined', mode)
            return
        radius = _AIM_MODE_TO_RADIUS[mode]
        bounds = [x - radius,
         y - radius,
         x + radius,
         y + radius]
        self.__ui.call('battle.aimVisibleSizeChanged', bounds)

    def __onPlayerFeedbackReceived(self, eventID, series):
        if self.__enabled and eventID in _FEEDBACK_EVENT_TO_BATTLE_EFFICIENCY:
            effType = _FEEDBACK_EVENT_TO_BATTLE_EFFICIENCY[eventID]
            effShortDesc = i18n.makeString('#ingame_gui:efficiencyRibbons/{0:>s}'.format(effType))
            self.__flashObject.addBattleEfficiencyEvent(effType, effShortDesc, series)

    def __onSettingsChanged(self, diff):
        key = GAME.SHOW_BATTLE_EFFICIENCY_RIBBONS
        if key in diff and self.__flashObject:
            self.__enabled = bool(diff[key])
            self.__flashObject.setup(self.__enabled, _RIBBON_SOUNDS_ENABLED, *_POS_COEFF)
