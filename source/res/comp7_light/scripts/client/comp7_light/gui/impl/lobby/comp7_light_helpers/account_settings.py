# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/comp7_light_helpers/account_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_LIGHT_UI_SECTION, COMP7_LIGHT_UMG_SEEN_QUESTS, COMP7_LIGHT_UMG_PROGRESSION_POINTS_SEEN, COMP7_LIGHT_UMG_ENTRY_POINT_SEEN

def getLastSeenQuestData(questID):
    settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
    settings.setdefault(COMP7_LIGHT_UMG_SEEN_QUESTS, {}).setdefault(questID, (0, True))
    return settings[COMP7_LIGHT_UMG_SEEN_QUESTS][questID]


def setLastSeenQuestData(questID, questData):
    settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
    settings.setdefault(COMP7_LIGHT_UMG_SEEN_QUESTS, {})
    settings[COMP7_LIGHT_UMG_SEEN_QUESTS][questID] = questData
    AccountSettings.setUIFlag(COMP7_LIGHT_UI_SECTION, settings)


def setUmgProgressionPointsSeen(curPoints):
    settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
    settings[COMP7_LIGHT_UMG_PROGRESSION_POINTS_SEEN] = curPoints
    AccountSettings.setUIFlag(COMP7_LIGHT_UI_SECTION, settings)


def getPrevUmgProgressionPointsSeen():
    settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
    return settings.get(COMP7_LIGHT_UMG_PROGRESSION_POINTS_SEEN, 0)


def markUmgEntryPointSeen():
    settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
    settings[COMP7_LIGHT_UMG_ENTRY_POINT_SEEN] = True
    AccountSettings.setUIFlag(COMP7_LIGHT_UI_SECTION, settings)


def getUmgEntryPointSeen():
    settings = AccountSettings.getUIFlag(COMP7_LIGHT_UI_SECTION)
    return settings.get(COMP7_LIGHT_UMG_ENTRY_POINT_SEEN, False)
