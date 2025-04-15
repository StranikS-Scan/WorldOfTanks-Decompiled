# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/daily_quest_view_constants.py
from constants import DailyQuestsLevels
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_view_model import DailyTabs
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_constants import DailyQuestsConstants
QUESTS_LEVELS_IN_TAB = {level:{DailyTabs.QUESTS} for level in DailyQuestsLevels.DAILY}
for level in DailyQuestsLevels.DAILY_PREMIUM:
    QUESTS_LEVELS_IN_TAB.setdefault(level, set()).add(DailyTabs.PREMIUM)

QUESTS_TABS_IN_LEVEL = {}
for level, tabs in QUESTS_LEVELS_IN_TAB.iteritems():
    for tab in tabs:
        QUESTS_TABS_IN_LEVEL.setdefault(tab, set()).add(level)

WIDGET_GROUP_TO_LEVELS = {DailyQuestsConstants.DAILY_GROUP_ID: DailyQuestsLevels.DAILY,
 DailyQuestsConstants.PREMIUM_GROUP_ID: DailyQuestsLevels.DAILY_PREMIUM,
 DailyQuestsConstants.EPIC_GROUP_ID: (DailyQuestsLevels.EPIC,)}
