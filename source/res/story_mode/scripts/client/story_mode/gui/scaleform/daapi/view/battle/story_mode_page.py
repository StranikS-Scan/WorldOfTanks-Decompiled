# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/story_mode_page.py
from gui.Scaleform.daapi.view.battle.pve_base.page import PveBaseBattlePage
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from shared_utils import CONST_CONTAINER
from story_mode.gui.scaleform.daapi.view.battle.page_base import STORY_MODE_EXTERNAL_COMPONENTS, StoryModeBattlePageBase

class DynamicAliases(CONST_CONTAINER):
    PREBATTLE_TIMER_SOUND_PLAYER = 'prebattleTimerSoundPlayer'


STORY_MODE_CONFIG = ComponentsConfig(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
   BATTLE_VIEW_ALIASES.HINT_PANEL,
   BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL)),
 (BATTLE_CTRL_ID.PERKS, (BATTLE_VIEW_ALIASES.SITUATION_INDICATORS,)),
 (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (BATTLE_VIEW_ALIASES.PLAYERS_PANEL,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
 (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT, BATTLE_VIEW_ALIASES.NEWBIE_HINT)),
 (BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_PANEL)),
 (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL))), viewsConfig=((DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),))

class StoryModeBattlePage(StoryModeBattlePageBase, PveBaseBattlePage):

    def __init__(self):
        super(StoryModeBattlePage, self).__init__(components=STORY_MODE_CONFIG, external=STORY_MODE_EXTERNAL_COMPONENTS, fullStatsAlias=None)
        return

    def _filterExistingViewAliases(self, income):
        existingAliases = set(self.components.keys())
        return income & existingAliases if income is not None else set()
