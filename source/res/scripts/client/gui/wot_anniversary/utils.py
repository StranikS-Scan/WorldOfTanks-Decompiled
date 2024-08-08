# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/utils.py
import logging
from typing import Optional, TYPE_CHECKING
from gui.wot_anniversary.wot_anniversary_constants import WOT_ANNIVERSARY_LOGIN_QUESTS_PREFIX, Phase, WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN, WOT_ANNIVERSARY_MASCOT_TOKEN, WOT_ANNIVERSARY_DAILY_QUEST_PREFIX, WOT_ANNIVERSARY_PREFIX, WOT_ANNIVERSARY_ALL_MASCOT_BATTLE_QUESTS_PREFIX, WOT_ANNIVERSARY_ALL_MASCOT_REWARD_QUEST
from helpers import dependency
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
if TYPE_CHECKING:
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)

def showWotAnniversaryAwardWindow(quest, useQueue=False):
    from gui.shared.event_dispatcher import findAndLoadWindow
    from gui.wot_anniversary.award_view import WotAnniversaryAwardWindow
    findAndLoadWindow(useQueue, WotAnniversaryAwardWindow, quest)


def showWotAnniversaryIntroWindow(closeCallback=None):
    from gui.wot_anniversary.intro_view import WotAnniversaryIntroWindow
    if not WotAnniversaryIntroWindow.getInstances():
        window = WotAnniversaryIntroWindow(closeCallback=closeCallback)
        window.load()


def showWotAnniversaryWelcomeWindow(useQueue=False):
    from gui.shared.event_dispatcher import findAndLoadWindow
    from gui.wot_anniversary.welcome_view import WotAnniversaryWelcomeWindow
    findAndLoadWindow(useQueue, WotAnniversaryWelcomeWindow)


@dependency.replace_none_kwargs(settings=ISettingsCore)
def setAnniversaryServerSetting(settingsSection, settings=None):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    settings.serverSettings.setSections([SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE], settingsSection)


@dependency.replace_none_kwargs(settings=ISettingsCore)
def isAnniversaryNotificationShowed(notification, settings=None):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    return settings.serverSettings.getSection(SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE).get(notification)


@dependency.replace_none_kwargs(settings=ISettingsCore)
def isAnniversaryIntroShowed(settings=None):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from account_helpers.settings_core.settings_constants import WotAnniversaryStorageKeys
    return settings.serverSettings.getSectionSettings(SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE, WotAnniversaryStorageKeys.WOT_ANNIVERSARY_INTRO_SHOWED, False)


@dependency.replace_none_kwargs(settings=ISettingsCore)
def isAnniversaryWelcomeShowed(settings=None):
    from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
    from account_helpers.settings_core.settings_constants import WotAnniversaryStorageKeys
    return settings.serverSettings.getSectionSettings(SETTINGS_SECTIONS.WOT_ANNIVERSARY_STORAGE, WotAnniversaryStorageKeys.WOT_ANNIVERSARY_WELCOME_SHOWED, False)


def isWotAnniversaryLoginQuest(questID):
    return questID.startswith(WOT_ANNIVERSARY_LOGIN_QUESTS_PREFIX) and questID != WOT_ANNIVERSARY_LOGIN_UNLOCK_TOKEN


def isWotAnniversaryDailyQuest(questID):
    return questID.startswith(WOT_ANNIVERSARY_DAILY_QUEST_PREFIX)


def isWotAnniversaryQuest(questID):
    return questID.startswith(WOT_ANNIVERSARY_PREFIX)


def isMascotRewardQuest(questID):
    return questID.startswith(WOT_ANNIVERSARY_ALL_MASCOT_REWARD_QUEST)


def getPhaseFromQuestID(questID):
    phase = None
    if questID.startswith(WOT_ANNIVERSARY_ALL_MASCOT_BATTLE_QUESTS_PREFIX) or questID.startswith(WOT_ANNIVERSARY_ALL_MASCOT_REWARD_QUEST):
        parts = questID.split(':')
        if len(parts) > 4:
            phase = parts[4]
    return Phase.CAT if phase not in Phase.ALL() else phase


def isTokenQuestUnlocked(quest, token):
    tokenCondition = findFirst(lambda t: t.getID() == token, quest.accountReqs.getConditions().findAll('token'))
    return tokenCondition.isAvailable() if tokenCondition else False


def isMascotQuestRewardAvailable(quest):
    phase = getPhaseFromQuestID(quest.getID())
    token = WOT_ANNIVERSARY_MASCOT_TOKEN.format(phase)
    isQuestUnlocked = isTokenQuestUnlocked(quest, token)
    return isQuestUnlocked and not quest.isCompleted()


def getQuestNumber(questID):
    dayNumber = None
    if questID.startswith(WOT_ANNIVERSARY_LOGIN_QUESTS_PREFIX):
        parts = questID.split(':')
        if len(parts) > 4:
            dayNumber = parts[4]
    elif questID.startswith(WOT_ANNIVERSARY_DAILY_QUEST_PREFIX):
        parts = questID.split(':')
        if len(parts) > 3:
            dayNumber = parts[3]
    elif questID.startswith(WOT_ANNIVERSARY_ALL_MASCOT_BATTLE_QUESTS_PREFIX):
        parts = questID.split(':')
        if len(parts) > 5:
            dayNumber = parts[5]
    return int(dayNumber) if dayNumber is not None and dayNumber.isdigit() else None
