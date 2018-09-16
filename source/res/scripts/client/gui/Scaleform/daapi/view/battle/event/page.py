# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
import BigWorld
import SoundGroups
from constants import CURRENT_REALM
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage, DynamicAliases
from gui.Scaleform.daapi.view.battle.event import football_audio, football_goal_celebration
from gui.Scaleform.daapi.view.battle.event.football_vehicle_state import FootballVehiclesWatcher
from gui.Scaleform.daapi.view.battle.shared.drone_music_player import DroneMusicPlayer
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.period_music_listener import PeriodMusicListener
from gui.Scaleform.daapi.view.meta.FootballEventBattlePageMeta import FootballEventBattlePageMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from shared_utils import CONST_CONTAINER

class _Commentators(object):
    IT = 'it'
    RU = 'ru'
    EN = 'en'


def _determineCommentator(arenaID):
    isBuffonCommentator = arenaID % 2 > 0
    if isBuffonCommentator:
        return _Commentators.IT
    return _Commentators.RU if CURRENT_REALM == 'RU' else _Commentators.EN


class _FootballDynamicAliases(CONST_CONTAINER):
    GOAL_PROXIMITY_SOUND_PLAYER = 'goalProximitySoundPlayer'
    EVENTS_SOUND_PLAYER = 'footballEventsSound'
    GOAL_CELEBRATION = 'goalCelebration'
    FIELD_POSITION_VO_SOUND_PLAYER = 'fieldPositionVOSoundPlayer'
    FOOTBALL_VEHICLES_WATCHER = 'FootballVehiclesWatcher'


class EventBattlePage(ClassicPage):

    def _populate(self):
        super(EventBattlePage, self)._populate()
        LOG_DEBUG('Event battle page is created.')

    def _dispose(self):
        super(EventBattlePage, self)._dispose()
        LOG_DEBUG('Event battle page is destroyed.')


class _FootballComponentConfig(ComponentsConfig):

    def __init__(self):
        super(_FootballComponentConfig, self).__init__(((BATTLE_CTRL_ID.FOOTBALL_CTRL, (BATTLE_VIEW_ALIASES.FOOTBALL_FRAG_CORRELATION_BAR,
           BATTLE_VIEW_ALIASES.FOOTBALL_FULL_STATS,
           BATTLE_VIEW_ALIASES.FOOTBALL_OVERTIME_BAR,
           BATTLE_VIEW_ALIASES.FOOTBALL_BATTLE_ANIMATION_TIMER,
           BATTLE_VIEW_ALIASES.FOOTBALL_FADE_OVERLAY,
           _FootballDynamicAliases.GOAL_PROXIMITY_SOUND_PLAYER,
           _FootballDynamicAliases.EVENTS_SOUND_PLAYER,
           _FootballDynamicAliases.GOAL_CELEBRATION,
           _FootballDynamicAliases.FOOTBALL_VEHICLES_WATCHER)),
         (BATTLE_CTRL_ID.FOOTBALL_PERIOD_CTRL, (BATTLE_VIEW_ALIASES.FOOTBALL_OVERTIME_BAR,
           BATTLE_VIEW_ALIASES.FOOTBALL_OVERTIME_TIMER,
           BATTLE_VIEW_ALIASES.FOOTBALL_PREBATTLE_TIMER,
           BATTLE_VIEW_ALIASES.FOOTBALL_START_TIMER,
           BATTLE_VIEW_ALIASES.FOOTBALL_BATTLE_ANIMATION_TIMER,
           _FootballDynamicAliases.EVENTS_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.FOOTBALL_BATTLE_ANIMATION_TIMER,
           BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
           BATTLE_VIEW_ALIASES.FOOTBALL_PREBATTLE_TIMER,
           BATTLE_VIEW_ALIASES.FOOTBALL_OVERTIME_TIMER,
           BATTLE_VIEW_ALIASES.FOOTBALL_START_TIMER,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           _FootballDynamicAliases.EVENTS_SOUND_PLAYER,
           DynamicAliases.DRONE_MUSIC_PLAYER,
           DynamicAliases.PERIOD_MUSIC_LISTENER)),
         (BATTLE_CTRL_ID.FOOTBALL_ENTITIES_CTRL, (_FootballDynamicAliases.GOAL_PROXIMITY_SOUND_PLAYER, _FootballDynamicAliases.FIELD_POSITION_VO_SOUND_PLAYER, _FootballDynamicAliases.FOOTBALL_VEHICLES_WATCHER)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,))), viewsConfig=((_FootballDynamicAliases.GOAL_PROXIMITY_SOUND_PLAYER, football_audio.GoalProximitySoundPlayer),
         (_FootballDynamicAliases.EVENTS_SOUND_PLAYER, football_audio.FootballEventsSound),
         (_FootballDynamicAliases.GOAL_CELEBRATION, football_goal_celebration.FootballGoalCelebration),
         (_FootballDynamicAliases.FIELD_POSITION_VO_SOUND_PLAYER, football_audio.FieldPositionVOSoundPlayer),
         (_FootballDynamicAliases.FOOTBALL_VEHICLES_WATCHER, FootballVehiclesWatcher),
         (DynamicAliases.DRONE_MUSIC_PLAYER, DroneMusicPlayer),
         (DynamicAliases.PERIOD_MUSIC_LISTENER, PeriodMusicListener)))


FOOTBALL_CONFIG = _FootballComponentConfig()

class FootballEventBattlePage(FootballEventBattlePageMeta):

    def __init__(self, components=None, external=None):
        if components is None:
            components = FOOTBALL_CONFIG
        super(FootballEventBattlePage, self).__init__(components=components, external=external)
        self._fullStatsAlias = BATTLE_VIEW_ALIASES.FOOTBALL_FULL_STATS
        self.__commentatorTimerID = None
        self.__commentatorType = None
        self.__wasCommentatorShown = False
        return

    def _destroy(self):
        super(FootballEventBattlePage, self)._destroy()
        self.__cancelCommentatorTimer()

    def _onBattleLoadingStart(self):
        super(FootballEventBattlePage, self)._onBattleLoadingStart()
        self.__commentatorType = _determineCommentator(avatar_getter.getArenaUniqueID())
        SoundGroups.g_instance.setSwitch('SWITCH_ext_ev_football_voice_over', 'SWITCH_ext_ev_football_voice_over_{}'.format(self.__commentatorType))

    def _onBattleLoadingFinish(self):
        super(FootballEventBattlePage, self)._onBattleLoadingFinish()
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.FOOTBALL_OVERTIME_TIMER,
         BATTLE_VIEW_ALIASES.FOOTBALL_OVERTIME_BAR,
         BATTLE_VIEW_ALIASES.FOOTBALL_FULL_STATS,
         BATTLE_VIEW_ALIASES.FOOTBALL_START_TIMER,
         BATTLE_VIEW_ALIASES.FOOTBALL_FADE_OVERLAY,
         BATTLE_VIEW_ALIASES.MINIMAP}, visible={BATTLE_VIEW_ALIASES.FOOTBALL_PREBATTLE_TIMER})
        self.__cancelCommentatorTimer()
        if not self.__wasCommentatorShown:
            self.__commentatorTimerID = BigWorld.callback(2.0, self.__showCommentatorPanel)

    def __cancelCommentatorTimer(self):
        if self.__commentatorTimerID is not None:
            BigWorld.cancelCallback(self.__commentatorTimerID)
            self.__commentatorTimerID = None
        return

    def __showCommentatorPanel(self):
        self.__commentatorTimerID = None
        self.__wasCommentatorShown = True
        SoundGroups.g_instance.playSound2D('ev_football_commenter_presentation')
        self.as_setCommentatorPanelVisibleS(FOOTBALL2018.getCommentatorNameText(self.__commentatorType), FOOTBALL2018.getCommentatorRoleNameText(self.__commentatorType), RES_ICONS.getFB18Commentator(self.__commentatorType))
        return
