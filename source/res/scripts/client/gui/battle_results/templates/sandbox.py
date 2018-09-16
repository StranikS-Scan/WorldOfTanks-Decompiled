# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/templates/sandbox.py
from gui.battle_results.components import base
from gui.battle_results.components import personal
from gui.battle_results.components import shared
from gui.battle_results.templates import regular
_SANDBOX_NO_INCOME_ALERT_VO_META = base.PropertyMeta((('icon', '', 'icon'), ('text', '', 'text')))
_SANDBOX_NO_INCOME_ALERT_VO_META.bind(personal.SandboxNoIncomeAlert)
SANDBOX_PERSONAL_STATS_BLOCK = regular.REGULAR_PERSONAL_STATS_BLOCK.clone()
SANDBOX_PERSONAL_STATS_BLOCK.addNextComponent(shared.TrueFlag('showNoIncomeAlert'))
SANDBOX_PERSONAL_STATS_BLOCK.addNextComponent(personal.SandboxNoIncomeAlert(field='noIncomeAlert'))
SANDBOX_TEAM_ITEM_STATS_ENABLE = shared.FalseFlag('closingTeamMemberStatsEnabled')
SANDBOX_PERSONAL_ACCOUNT_DB_ID = personal.PersonalAccountDBID('selectedTeamMemberId')
