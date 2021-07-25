# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/page.py
import WWISE
from shared_utils import CONST_CONTAINER
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.shared import drone_music_player, finish_sound_player
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.daapi.view.battle.maps_training import markers2d, arena_time_notificator
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class DynamicAliases(CONST_CONTAINER):
    PREBATTLE_TIMER_SOUND_PLAYER = 'prebattleTimerSoundPlayer'
    FINISH_SOUND_PLAYER = 'finishSoundPlayer'
    DRONE_MUSIC_PLAYER = 'droneMusicPlayer'
    TIME_NOTIFIER = 'arenaTimeNotificator'


MAPS_TRAINING_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
   DynamicAliases.TIME_NOTIFIER,
   BATTLE_VIEW_ALIASES.HINT_PANEL,
   DynamicAliases.DRONE_MUSIC_PLAYER,
   DynamicAliases.FINISH_SOUND_PLAYER)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER, DynamicAliases.FINISH_SOUND_PLAYER)),
 (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
 (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.MAPS_TRAINING_GOALS,))), viewsConfig=((DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer),
 (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),
 (DynamicAliases.FINISH_SOUND_PLAYER, finish_sound_player.FinishSoundPlayer),
 (DynamicAliases.TIME_NOTIFIER, arena_time_notificator.MapsTrainingArenaTimeNotificator)))
_MAPS_TRAINING_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, markers2d.MapsTrainingMarkersManager)

class MapsTrainingPage(ClassicPage):

    def __init__(self, components=MAPS_TRAINING_CONFIG, external=_MAPS_TRAINING_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        super(MapsTrainingPage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)

    def _populate(self):
        WWISE.activateRemapping('maps_training')
        super(MapsTrainingPage, self)._populate()

    def _dispose(self):
        WWISE.deactivateRemapping('maps_training')
        super(MapsTrainingPage, self)._dispose()
