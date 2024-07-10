# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/__init__.py
from gui.battle_results.components import base
from gui.battle_results.templates.cybersport import CYBER_SPORT_BLOCK
from gui.battle_results.templates.fortification import STRONGHOLD_BATTLE_COMMON_STATS_BLOCK
from gui.battle_results.templates.fortification import STRONGHOLD_PERSONAL_STATS_BLOCK
from gui.battle_results.templates.fortification import STRONGHOLD_TEAMS_STATS_BLOCK
from gui.battle_results.templates.regular import MULTI_TEAM_TABS_BLOCK
from gui.battle_results.templates.regular import PROGRESSIVE_REWARD_VO
from gui.battle_results.templates.regular import PRESTIGE_PROGRESS_VO
from gui.battle_results.templates.regular import REGULAR_TABS_BLOCK
from gui.battle_results.templates.regular import VEHICLE_PROGRESS_STATS_BLOCK
from gui.battle_results.templates.regular import BATTLE_PASS_PROGRESS_STATS_BLOCK
from gui.battle_results.templates.regular import QUESTS_PROGRESS_STATS_BLOCK
from gui.battle_results.templates.regular import DOG_TAGS_PROGRESS_STATS_BLOCK
from gui.battle_results.templates.regular import REGULAR_COMMON_STATS_BLOCK
from gui.battle_results.templates.regular import REGULAR_PERSONAL_STATS_BLOCK
from gui.battle_results.templates.regular import REGULAR_TEAMS_STATS_BLOCK
from gui.battle_results.templates.regular import REGULAR_TEXT_STATS_BLOCK
from gui.battle_results.templates.regular import CLAN_TEXT_STATS_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_COMMON_STATS_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_TEAMS_STATS_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_RESULTS_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_PERSONAL_STATS_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_RESULTS_STATUS_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_RESULTS_TEAMS_STATS_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_ENABLE_ANIMATION_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_SHOW_WIDGET_BLOCK
from gui.battle_results.templates.ranked_battles import RANKED_RESULTS_STATE_BLOCK
from gui.battle_results.templates.epic import EPIC_TABS_BLOCK
from gui.battle_results.templates.epic import EPIC_COMMON_STATS_BLOCK
from gui.battle_results.templates.epic import EPIC_PERSONAL_STATS_BLOCK
from gui.battle_results.templates.epic import EPIC_TEAMS_STATS_BLOCK
from gui.battle_results.templates.maps_training import MAPS_TRAINING_RESULTS_BLOCK
from gui.battle_results.templates.comp7 import COMP7_PERSONAL_STATS_BLOCK
from gui.battle_results.templates.comp7 import TOURNAMENT_COMP7_PERSONAL_STATS_BLOCK
from gui.battle_results.templates.comp7 import COMP7_COMMON_STATS_BLOCK
from gui.battle_results.templates.comp7 import TOURNAMENT_COMP7_COMMON_STATS_BLOCK
from gui.battle_results.templates.comp7 import COMP7_TEAMS_STATS_BLOCK
from gui.battle_results.templates.comp7 import COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK
from gui.battle_results.templates.comp7 import EFFICIENCY_TITLE_WITH_SKILLS_VO
from gui.battle_results.templates.comp7 import TRAINING_COMP7_COMMON_STATS_BLOCK
from gui.battle_results.templates.comp7 import TRAINING_COMP7_PERSONAL_STATS_BLOCK
from gui.impl import backport
from gui.impl.gen import R
__all__ = ('TOTAL_VO_META', 'MULTI_TEAM_TABS_BLOCK', 'REGULAR_TABS_BLOCK', 'VEHICLE_PROGRESS_STATS_BLOCK', 'BATTLE_PASS_PROGRESS_STATS_BLOCK', 'QUESTS_PROGRESS_STATS_BLOCK', 'DOG_TAGS_PROGRESS_STATS_BLOCK', 'REGULAR_COMMON_STATS_BLOCK', 'REGULAR_PERSONAL_STATS_BLOCK', 'REGULAR_TEAMS_STATS_BLOCK', 'REGULAR_TEXT_STATS_BLOCK', 'CLAN_TEXT_STATS_BLOCK', 'STRONGHOLD_BATTLE_COMMON_STATS_BLOCK', 'STRONGHOLD_PERSONAL_STATS_BLOCK', 'STRONGHOLD_TEAMS_STATS_BLOCK', 'CYBER_SPORT_BLOCK', 'RANKED_COMMON_STATS_BLOCK', 'RANKED_TEAMS_STATS_BLOCK', 'RANKED_RESULTS_BLOCK', 'RANKED_PERSONAL_STATS_BLOCK', 'RANKED_RESULTS_STATUS_BLOCK', 'RANKED_ENABLE_ANIMATION_BLOCK', 'EPIC_COMMON_STATS_BLOCK', 'EPIC_TABS_BLOCK', 'EPIC_PERSONAL_STATS_BLOCK', 'EPIC_TEAMS_STATS_BLOCK', 'RANKED_SHOW_WIDGET_BLOCK', 'PROGRESSIVE_REWARD_VO', 'RANKED_RESULTS_STATE_BLOCK', 'MAPS_TRAINING_RESULTS_BLOCK', 'COMP7_PERSONAL_STATS_BLOCK', 'TOURNAMENT_COMP7_PERSONAL_STATS_BLOCK', 'COMP7_COMMON_STATS_BLOCK', 'TOURNAMENT_COMP7_COMMON_STATS_BLOCK', 'COMP7_TEAMS_STATS_BLOCK', 'COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK', 'EFFICIENCY_TITLE_WITH_SKILLS_VO', 'PRESTIGE_PROGRESS_VO', 'TRAINING_COMP7_COMMON_STATS_BLOCK', 'TRAINING_COMP7_PERSONAL_STATS_BLOCK')
TOTAL_VO_META = base.DictMeta({'personal': {},
 'common': {},
 'team1': [],
 'team2': [],
 'textData': {},
 'battlePass': None,
 'quests': None,
 'unlocks': [],
 'tabInfo': [],
 'cyberSport': None,
 'isFreeForAll': False,
 'closingTeamMemberStatsEnabled': True,
 'selectedTeamMemberId': -1,
 'progressiveReward': None,
 'dog_tags': {},
 'prestige': None,
 'efficiencyTitle': backport.text(R.strings.battle_results.common.battleEfficiencyWithoutOreders.title())})
