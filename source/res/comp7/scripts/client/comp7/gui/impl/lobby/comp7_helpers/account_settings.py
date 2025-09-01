# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/comp7_helpers/account_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_WEEKLY_WIDGET_SHOWN_QUEST, COMP7_UI_SECTION, COMP7_UMG_ENTRY_POINT_SEEN

def getLastSeenQuestData(questID):
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    settings.setdefault(COMP7_WEEKLY_WIDGET_SHOWN_QUEST, {}).setdefault(questID, (0, True))
    return settings[COMP7_WEEKLY_WIDGET_SHOWN_QUEST][questID]


def setLastSeenQuestData(questID, questData):
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    settings.setdefault(COMP7_WEEKLY_WIDGET_SHOWN_QUEST, {})
    settings[COMP7_WEEKLY_WIDGET_SHOWN_QUEST][questID] = questData
    AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)


def markUmgEntryPointSeen():
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    settings[COMP7_UMG_ENTRY_POINT_SEEN] = True
    AccountSettings.setUIFlag(COMP7_UI_SECTION, settings)


def getUmgEntryPointSeen():
    settings = AccountSettings.getUIFlag(COMP7_UI_SECTION)
    return settings.get(COMP7_UMG_ENTRY_POINT_SEEN, False)
