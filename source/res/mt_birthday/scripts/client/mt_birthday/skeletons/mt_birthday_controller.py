# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/skeletons/mt_birthday_controller.py
import typing
from skeletons.gui.game_control import IGameController
from gui.server_events.event_items import Quest
from th_async import th_async
if typing.TYPE_CHECKING:
    from typing import Sequence, List, Dict, Optional, Tuple
    from mt_birthday.skeletons.sub_controllers import IGiftSystemSubController, ITanksBirthdayProgressionSubController
    from gui.shared.view_helpers.UsersInfoHelper import BatchUsersInfoHelper
    from gui.Scaleform.daapi.view.lobby.hangar.entry_points.gf_header_widget import GFWidgetAliases
    from mt_birthday.gui.feature_types import BattlePlayerData
    from Event import Event

class ITanksBirthdayController(IGameController):
    onEventSettingsUpdated = None
    onNewGiftsReceived = None
    onLootboxSeen = None
    onQuestsUpdated = None

    @property
    def progression(self):
        raise NotImplementedError

    @property
    def giftSystem(self):
        raise NotImplementedError

    @property
    def userInfoHelper(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isPaused(self):
        raise NotImplementedError

    def isDisabled(self):
        raise NotImplementedError

    def isEnding(self):
        raise NotImplementedError

    def isAlreadyReceivedGift(self, spaID):
        raise NotImplementedError

    def isBlogger(self):
        raise NotImplementedError

    def isPlayerBlocked(self, spaID):
        raise NotImplementedError

    def isPlayerInBlackList(self, spaID):
        raise NotImplementedError

    def getHangarWidgetAlias(self):
        raise NotImplementedError

    def getExpiryTime(self):
        raise NotImplementedError

    def getBadgeQuestRequiredReplyTokens(self):
        raise NotImplementedError

    def getStartTime(self):
        raise NotImplementedError

    def getEventState(self):
        raise NotImplementedError

    def getLastFightsPlayers(self):
        raise NotImplementedError

    def addLastFightsPlayerID(self, playerId):
        raise NotImplementedError

    def addLastFightsPlayersIDs(self, playersIDs):
        raise NotImplementedError

    def getBannedPlayersIDs(self):
        raise NotImplementedError

    def addBannedPlayersID(self, playerID):
        raise NotImplementedError

    def getStampCount(self):
        raise NotImplementedError

    def getPhrasesIds(self):
        raise NotImplementedError

    def setPhrasesIds(self, phrasesIds):
        raise NotImplementedError

    def getGoldenTicketsCount(self):
        raise NotImplementedError

    def getMaxSelectedPlayers(self):
        raise NotImplementedError

    def getSpecialStampCount(self):
        raise NotImplementedError

    def getCooldownGiftTime(self):
        raise NotImplementedError

    def getLocalEndDate(self):
        raise NotImplementedError

    def getEconomicBonusTypes(self):
        raise NotImplementedError

    def getEconomyBonusValue(self):
        raise NotImplementedError

    def getBattleQuests(self):
        raise NotImplementedError

    def getQuestGiverBattleQuests(self):
        raise NotImplementedError

    def hasActiveQuestGiverQuest(self):
        raise NotImplementedError

    def getMaxProgressionLevel(self):
        raise NotImplementedError

    def getUnseenGiftsCount(self):
        raise NotImplementedError

    def getUnseenGiftId(self):
        raise NotImplementedError

    def pushNewGiftReceived(self, giftId, count):
        raise NotImplementedError

    def seenGiftNotification(self, count):
        raise NotImplementedError

    def getNewGiftForNotification(self):
        raise NotImplementedError

    def getGoldWagonURL(self):
        raise NotImplementedError

    def isGoldWagonEnabled(self):
        raise NotImplementedError

    def getTicketExchangeURL(self):
        raise NotImplementedError

    def isTicketExchangeEnabled(self):
        raise NotImplementedError

    @staticmethod
    def getRandomBloggerPhraseID(currPhraseID=None):
        raise NotImplementedError

    def shufflePhrases(self):
        raise NotImplementedError

    def shuffleLastPhrases(self):
        raise NotImplementedError

    def getNextPhraseID(self):
        raise NotImplementedError

    def getAccountSettingsTipPathByTabId(self, tabId=None):
        raise NotImplementedError

    def isGeneralTipCompleted(self):
        raise NotImplementedError

    def isTabTipsCompleted(self, tabId=None):
        raise NotImplementedError

    @th_async
    def sendGifts(self, stampType, receiversIDs, messageIdx, arenaUniqueID=None):
        raise NotImplementedError


class ILastBattlesPlayersController(IGameController):

    def getLastFightsPlayers(self):
        raise NotImplementedError

    def addLastFightsPlayerID(self, playerId):
        raise NotImplementedError

    def addLastFightsPlayersIDs(self, playersIDs):
        raise NotImplementedError
