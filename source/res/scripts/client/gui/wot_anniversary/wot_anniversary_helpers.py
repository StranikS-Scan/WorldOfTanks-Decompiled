# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/wot_anniversary_helpers.py
import typing
import WWISE
from account_helpers.AccountSettings import AccountSettings, WOT_ANNIVERSARY_SECTION
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IWotAnniversaryController
from wot_anniversary_common import WotAnniversaryUrls
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
    from gui.server_events.event_items import Quest
WOT_ANNIVERSARY_PREFIX = 'anniversary:'
WOT_ANNIVERSARY_DAILY_QUEST_PREFIX = WOT_ANNIVERSARY_PREFIX + 'daily:'
WOT_ANNIVERSARY_WEEKLY_QUEST_PREFIX = WOT_ANNIVERSARY_PREFIX + 'big:'
WOT_ANNIVERSARY_LAST_WEEKLY_QUEST = WOT_ANNIVERSARY_WEEKLY_QUEST_PREFIX + '2'
WOT_ANNIVERSARY_FINAL_REWARD_PREFIX = WOT_ANNIVERSARY_PREFIX + 'final_reward:'
WOT_ANNIVERSARY_FIRST_FINAL_REWARD_QUEST = WOT_ANNIVERSARY_FINAL_REWARD_PREFIX + '1'
WOT_ANNIVERSARY_SECOND_FINAL_REWARD_QUEST = WOT_ANNIVERSARY_FINAL_REWARD_PREFIX + '2'
WOT_ANNIVERSARY_QUEST_POINTS = WOT_ANNIVERSARY_PREFIX + 'points'
WOT_ANNIVERSARY_DAILY_TOKEN_PREFIX = WOT_ANNIVERSARY_PREFIX + 'quest:daily:'
WOT_ANNIVERSARY_REWARDS = 'anniversary_rewards'

class WotAnniversaryEventState(object):
    PAUSE = 1
    ENABLED = 2
    FINISHED = 3


def showWotAnniversaryAwardWindow(questID, rawAwards, useQueue=False):
    from gui.shared.event_dispatcher import findAndLoadWindow
    from gui.wot_anniversary.wot_anniversary_award_view import WotAnniversaryAwardWindow
    findAndLoadWindow(useQueue, WotAnniversaryAwardWindow, questID, rawAwards)


def showWotAnniversaryIntroWindow(closeCallback=None):
    from gui.wot_anniversary.wot_anniversary_intro_view import WotAnniversaryIntroWindow
    if not WotAnniversaryIntroWindow.getInstances():
        window = WotAnniversaryIntroWindow(closeCallback=closeCallback)
        window.load()


def showWotAnniversaryWelcomeWindow(useQueue=False):
    from gui.shared.event_dispatcher import findAndLoadWindow
    from gui.wot_anniversary.wot_anniversary_welcome_view import WotAnniversaryWelcomeWindow
    findAndLoadWindow(useQueue, WotAnniversaryWelcomeWindow)


def getWotAnniversarySectionSetting(settingName):
    settings = AccountSettings.getSettings(WOT_ANNIVERSARY_SECTION)
    return settings.get(settingName)


def setWotAnniversarySectionSetting(settingName, settingValue):
    settings = AccountSettings.getSettings(WOT_ANNIVERSARY_SECTION)
    settings.update({settingName: settingValue})
    AccountSettings.setSettings(WOT_ANNIVERSARY_SECTION, settings)


def findWeeklyQuest(quests):
    for qID, quest in quests.iteritems():
        if qID.startswith(WOT_ANNIVERSARY_WEEKLY_QUEST_PREFIX):
            return (qID, quest)

    return ('', None)


def showMainView():
    _showBrowserView(WotAnniversaryUrls.MAIN)


def showRewardProgressView():
    _showBrowserView(WotAnniversaryUrls.REWARDS)


@dependency.replace_none_kwargs(wotAnniversaryCtrl=IWotAnniversaryController)
def _showBrowserView(urlName, wotAnniversaryCtrl=None):
    from gui.shared.event_dispatcher import showBrowserOverlayView

    def _onExitPlaySound():
        WWISE.WW_eventGlobal(backport.sound(R.sounds.ev_bday_12_exit()))

    showBrowserOverlayView(wotAnniversaryCtrl.getUrl(urlName), VIEW_ALIAS.WOT_ANNIVERSARY_BROWSER_VIEW, callbackOnClose=_onExitPlaySound)


def isWotAnniversaryQuest(questID):
    return questID.startswith(WOT_ANNIVERSARY_PREFIX)


def isFinalTokenQuest(questID):
    return questID.startswith(WOT_ANNIVERSARY_FINAL_REWARD_PREFIX)


def getQuestNeededTokensCount(quest):
    if quest is not None:
        tokens = quest.accountReqs.getTokens()
        if tokens:
            return tokens[-1].getNeededCount()
    return 0
