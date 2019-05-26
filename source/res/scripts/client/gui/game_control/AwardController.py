# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/AwardController.py
import types
import weakref
import logging
from itertools import ifilter
from abc import ABCMeta, abstractmethod
from copy import deepcopy
import ArenaType
import gui.awards.event_dispatcher as shared_events
import personal_missions
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, AWARDS, SPEAKERS_DEVICE
from account_helpers.settings_core.settings_constants import SOUND
from account_shared import getFairPlayViolationName
from chat_shared import SYS_MESSAGE_TYPE
from constants import EVENT_TYPE, INVOICE_ASSET, PREMIUM_TYPE
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.layouts import PERSONAL_MISSIONS_GROUP
from gui import DialogsInterface
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.DialogsInterface import showDialog
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18PunishmentDialogMeta
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.ranked_battles import ranked_helpers
from gui.server_events import events_dispatcher as quests_events, recruit_helper
from gui.server_events.events_dispatcher import showLootboxesAward, showPiggyBankRewardWindow
from gui.server_events.finders import PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID, getBranchByOperationId, BRANCH_TO_OPERATION_IDS, CHAMPION_BADGES_BY_BRANCH
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.event_dispatcher import showProgressiveRewardAwardWindow
from gui.shared.events import PersonalMissionsEvent
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.functions import getViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.sounds.sound_constants import SPEAKERS_CONFIG
from helpers import dependency
from helpers import i18n
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr, vehicles as vehicles_core
from items.components.crew_books_constants import CREW_BOOK_DISPLAYED_AWARDS_COUNT
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import TelecomReceivedInvoiceFormatter
from messenger.proto.events import g_messengerEvents
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IAwardController, IRankedBattlesController, IBootcampController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.sounds import ISoundsController
from gui.awards.event_dispatcher import showCrewSkinAward
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardBonuses
_logger = logging.getLogger(__name__)

class QUEST_AWARD_POSTFIX(object):
    CREW_SKINS = 'awardcrewskin'
    CREW_BOOKS = 'awardcrewbook'


class AwardController(IAwardController, IGlobalListener):
    bootcampController = dependency.descriptor(IBootcampController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.__handlers = [BattleQuestsAutoWindowHandler(self),
         QuestBoosterAwardHandler(self),
         BoosterAfterBattleAwardHandler(self),
         PunishWindowHandler(self),
         TokenQuestsWindowHandler(self),
         MotiveQuestsWindowHandler(self),
         VehiclesResearchHandler(self),
         VictoryHandler(self),
         BattlesCountHandler(self),
         PveBattlesCountHandler(self),
         PersonalMissionBonusHandler(self),
         PersonalMissionWindowAfterBattleHandler(self),
         PersonalMissionAutoWindowHandler(self),
         PersonalMissionByAwardListHandler(self),
         PersonalMissionOperationAwardHandler(self),
         PersonalMissionOperationUnlockedHandler(self),
         GoldFishHandler(self),
         TelecomHandler(self),
         RankedQuestsHandler(self),
         MarkByInvoiceHandler(self),
         MarkByQuestHandler(self),
         CrewSkinsQuestHandler(self),
         CrewBooksQuestHandler(self),
         RecruitHandler(self),
         SoundDeviceHandler(self),
         EliteWindowHandler(self),
         LootBoxByInvoiceHandler(self),
         ProgressiveRewardHandler(self),
         PiggyBankOpenHandler(self)]
        super(AwardController, self).__init__()
        self.__delayedHandlers = []
        self.__isLobbyLoaded = False

    def init(self):
        for handler in self.__handlers:
            handler.init()

    def fini(self):
        for handler in self.__handlers:
            handler.fini()

    def postponeOrCall(self, handler, ctx):
        if self.canShow():
            handler(ctx)
        else:
            _logger.debug('Postponed award call: %s, %s', handler, ctx)
            self.__delayedHandlers.append((handler, ctx))

    def handlePostponed(self, *args):
        if self.canShow():
            for handler, ctx in self.__delayedHandlers:
                _logger.debug('Calling postponed award handler: %s, %s', handler, ctx)
                handler(ctx)

            self.__delayedHandlers = []

    def canShow(self):
        popupsWindowsDisabled = isPopupsWindowsOpenDisabled() or self.bootcampController.isInBootcamp()
        prbDispatcher = self.prbDispatcher
        return self.__isLobbyLoaded and not popupsWindowsDisabled if prbDispatcher is None else self.__isLobbyLoaded and not popupsWindowsDisabled and not prbDispatcher.getFunctionalState().hasLockedState

    def onAvatarBecomePlayer(self):
        self.__isLobbyLoaded = False
        self.stopGlobalListening()

    def onDisconnected(self):
        self.__isLobbyLoaded = False
        self.stopGlobalListening()
        for handler in self.__handlers:
            handler.stop()

    def onLobbyInited(self, *args):
        self.startGlobalListening()
        self.__isLobbyLoaded = True
        self.handlePostponed()
        for handler in self.__handlers:
            handler.start()

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        self.handlePostponed()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.handlePostponed()

    def onDequeued(self, queueType, *args):
        self.handlePostponed()


class AwardHandler(object):
    __metaclass__ = ABCMeta
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, awardCtrl):
        self._awardCtrl = weakref.proxy(awardCtrl)

    def init(self):
        pass

    def fini(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def handle(self, *args):
        if self._needToShowAward(args):
            self._awardCtrl.postponeOrCall(self._showAward, args)

    def isShowCongrats(self, quest):
        return quest.getData().get('showCongrats', False) if quest else False

    @abstractmethod
    def _needToShowAward(self, ctx):
        pass

    @abstractmethod
    def _showAward(self, ctx):
        pass


class ServiceChannelHandler(AwardHandler):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, channelType, awardCtrl):
        super(ServiceChannelHandler, self).__init__(awardCtrl)
        self.__type = channelType

    def init(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.handle

    def fini(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.handle

    def _needToShowAward(self, ctx):
        _, message = ctx
        return message is not None and message.type == self.__type and message.data is not None and message.data


class MultiTypeServiceChannelHandler(ServiceChannelHandler):

    def __init__(self, handledTypes, awardCtrl):
        super(MultiTypeServiceChannelHandler, self).__init__(None, awardCtrl)
        self.__types = handledTypes
        return

    def _needToShowAward(self, ctx):
        _, message = ctx
        return message is not None and message.type in self.__types and message.data is not None

    def _showAward(self, ctx):
        pass


class EliteWindowHandler(AwardHandler):
    __gui = dependency.descriptor(IGuiLoader)

    def init(self):
        g_playerEvents.onVehicleBecomeElite += self.handle

    def fini(self):
        g_playerEvents.onVehicleBecomeElite -= self.handle

    def _needToShowAward(self, ctx):
        return self.__gui.windowsManager.getViewByLayoutID(R.views.lobby.blueprints.blueprint_screen.blueprint_screen.BlueprintScreen()) is None

    def _showAward(self, ctx):
        vehTypeCompDescrs = ctx
        for vehTypeCompDescr in vehTypeCompDescrs:
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.ELITE_WINDOW, getViewName(VIEW_ALIAS.ELITE_WINDOW, vehTypeCompDescr), ctx={'vehTypeCompDescr': vehTypeCompDescr}), scope=EVENT_BUS_SCOPE.LOBBY)


class PunishWindowHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PunishWindowHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        arenaTypeID = message.data.get('arenaTypeID', 0)
        if arenaTypeID > 0 and arenaTypeID in ArenaType.g_cache:
            arenaType = ArenaType.g_cache[arenaTypeID]
        else:
            arenaType = None
        arenaCreateTime = message.data.get('arenaCreateTime', None)
        fairplayViolations = message.data.get('fairplayViolations', None)
        if arenaCreateTime and arenaType and fairplayViolations is not None and fairplayViolations[:2] != (0, 0):
            penaltyType = None
            violation = None
            if fairplayViolations[1] != 0:
                penaltyType = 'penalty'
                violation = fairplayViolations[1]
            elif fairplayViolations[0] != 0:
                penaltyType = 'warning'
                violation = fairplayViolations[0]
            showDialog(I18PunishmentDialogMeta('punishmentWindow', None, {'penaltyType': penaltyType,
             'arenaName': i18n.makeString(arenaType.name),
             'time': TimeFormatter.getActualMsgTimeStr(arenaCreateTime),
             'reason': i18n.makeString(DIALOGS.all('punishmentWindow/reason/%s' % getFairPlayViolationName(violation)))}), lambda *args: None)
        return


class PersonalMissionBonusHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PersonalMissionBonusHandler, self).__init__(SYS_MESSAGE_TYPE.potapovQuestBonus.index(), awardCtrl)

    def _showAward(self, ctx):
        _logger.debug('Show personal mission bonus award! %s', ctx)
        data = ctx[1].data
        achievements = []
        for recordIdx, value in data.get('popUpRecords', []):
            factory = getAchievementFactory(DB_ID_TO_RECORD[recordIdx])
            if factory is not None:
                a = factory.create(value=int(value))
                if a is not None:
                    achievements.append(a)

        if achievements:
            quests_events.showAchievementsAward(achievements)
        return


class PersonalMissionWindowAfterBattleHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PersonalMissionWindowAfterBattleHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        achievements = []
        popUpRecords = ctx[1].data.get('popUpRecords', [])
        for recordIdx, value in popUpRecords:
            recordName = DB_ID_TO_RECORD[recordIdx]
            if recordName in PERSONAL_MISSIONS_GROUP:
                factory = getAchievementFactory(recordName)
                if factory is not None:
                    a = factory.create(value=int(value))
                    if a is not None:
                        achievements.append(a)

        if achievements:
            quests_events.showAchievementsAward(achievements)
        return


class TokenQuestsWindowHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(TokenQuestsWindowHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        completedQuests = {}
        allQuests = self.eventsCache.getAllQuests(includePersonalMissions=True)
        for qID in data.get('completedQuestIDs', set()):
            if qID in allQuests:
                if self.isShowCongrats(allQuests[qID]):
                    vehiclesList = data.get('vehicles', [])
                    vehiclesDict = vehiclesList[0] if vehiclesList else {}
                    windowCtx = {'eventsCache': self.eventsCache,
                     'bonusVehicles': vehiclesDict}
                    currentQuest = allQuests[qID]
                    currentQuest = _getBlueprintActualBonus(data, currentQuest)
                    completedQuests[qID] = (currentQuest, windowCtx)

        for quest, context in completedQuests.itervalues():
            self._showWindow(quest, context)

    @staticmethod
    def _showWindow(quest, context):
        quests_events.showMissionAward(quest, context)


class LootBoxByInvoiceHandler(ServiceChannelHandler):
    itemsCache = dependency.descriptor(IItemsCache)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, awardCtrl):
        super(LootBoxByInvoiceHandler, self).__init__(SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl)

    def _showAward(self, ctx):
        invoiceData = ctx[1].data
        lootBoxes = {}
        if invoiceData.get('assetType', None) == INVOICE_ASSET.DATA and 'data' in invoiceData and 'tokens' in invoiceData['data']:
            tokensDict = invoiceData['data']['tokens']
            boxes = self.itemsCache.items.tokens.getLootBoxes()
            for tokenName, tokenData in tokensDict.iteritems():
                count = tokenData.get('count', 0)
                if count > 0 and tokenName in boxes:
                    lootbox = boxes[tokenName]
                    lootboxType = lootbox.getType()
                    if lootboxType not in lootBoxes:
                        lootBoxes[lootboxType] = {'count': count,
                         'userName': lootbox.getUserName(),
                         'isFree': lootbox.isFree()}
                    else:
                        lootBoxes[lootboxType]['count'] += count

        if lootBoxes:
            self._showWindow(lootBoxes)
        return

    @classmethod
    def _showWindow(cls, lootBoxes):
        for lootBoxType, lootBoxInfo in lootBoxes.iteritems():
            lootboxesCount = lootBoxInfo.get('count', 0)
            app = cls.appLoader.getApp()
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_HANGAR))
            if view is not None:
                showLootboxesAward(lootboxId=lootBoxType, lootboxCount=lootboxesCount, isFree=lootBoxInfo['isFree'])

        return


class PiggyBankOpenHandler(ServiceChannelHandler):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, awardCtrl):
        super(PiggyBankOpenHandler, self).__init__(SYS_MESSAGE_TYPE.piggyBankSmashed.index(), awardCtrl)

    def _showAward(self, ctx):
        if ctx[1].data:
            data = ctx[1].data
            credits_ = data.get('credits')
            if credits_ and credits_ > 0:
                self._showWindow(credits_, self.__isPremiumEnable())

    @staticmethod
    def _showWindow(credits_, isPremium):
        showPiggyBankRewardWindow(credits_, isPremium)

    def __isPremiumEnable(self):
        return self.itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)


class MarkByInvoiceHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(MarkByInvoiceHandler, self).__init__(SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl)

    def _showAward(self, ctx):
        invoiceData = ctx[1].data
        totalCount = 0
        if 'assetType' in invoiceData and invoiceData['assetType'] == INVOICE_ASSET.DATA:
            if 'data' in invoiceData:
                data = invoiceData['data']
                if 'tokens' in data:
                    tokensDict = data['tokens']
                    for tokenName, tokenData in tokensDict.iteritems():
                        if tokenName.startswith('img:'):
                            totalCount += tokenData.get('count', 0)

        if totalCount:
            self._showMessage(totalCount)

    @staticmethod
    def _showMessage(tokenCount):
        SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.TOKENS_NOTIFICATION_MARK_ACQUIRED, count=tokenCount, type=SystemMessages.SM_TYPE.tokenWithMarkAcquired)


class MarkByQuestHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(MarkByQuestHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index()), awardCtrl)
        self.__tokenCount = 0

    def _needToShowAward(self, ctx):
        if not super(MarkByQuestHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        self.__tokenCount = self.__extractCount(message)
        return bool(self.__tokenCount)

    def _showAward(self, ctx):
        self.__showMessage()

    def __showMessage(self):
        SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.TOKENS_NOTIFICATION_MARK_ACQUIRED, count=self.__tokenCount, type=SystemMessages.SM_TYPE.tokenWithMarkAcquired)

    @staticmethod
    def __extractCount(message):
        totalCounts = 0
        tokensDict = message.data.get('tokens', {})
        for tokenName, tokenData in tokensDict.iteritems():
            if tokenName.startswith('img:'):
                totalCounts += tokenData.get('count', 0)

        return totalCounts


class CrewSkinsQuestHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(CrewSkinsQuestHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index()), awardCtrl)

    def _needToShowAward(self, ctx):
        _, message = ctx
        res = super(CrewSkinsQuestHandler, self)._needToShowAward(ctx)
        questIDs = message.data.get('completedQuestIDs', set())
        res = res and 'crewSkins' in message.data
        res = res and next(ifilter(lambda x: x.endswith(QUEST_AWARD_POSTFIX.CREW_SKINS), questIDs), None) is not None
        return res

    def _showAward(self, ctx):
        showCrewSkinAward()


class CrewBooksQuestHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(CrewBooksQuestHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index()), awardCtrl)

    def _needToShowAward(self, ctx):

        def isCrewBook(intCD):
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(intCD)
            return itemTypeID == ITEM_TYPE_INDICES['crewBook']

        _, message = ctx
        res = super(CrewBooksQuestHandler, self)._needToShowAward(ctx)
        questIDs = message.data.get('completedQuestIDs', set())
        res = res and 'items' in message.data
        res = res and any((isCrewBook(intCD) for intCD in message.data['items'].iterkeys()))
        res = res and next(ifilter(lambda x: x.endswith(QUEST_AWARD_POSTFIX.CREW_BOOKS), questIDs), None) is not None
        return res

    def _showAward(self, ctx):
        _, message = ctx
        bonuses, _ = getProgressiveRewardBonuses(message.data, maxAwardCount=CREW_BOOK_DISPLAYED_AWARDS_COUNT)
        if bonuses:
            showProgressiveRewardAwardWindow(bonuses, LootCongratsTypes.INIT_CONGRAT_TYPE_CREW_BOOKS, 0)
        else:
            _logger.error("Can't show empty or invalid reward!")


class RecruitHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(RecruitHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)
        self.__questTypes = [SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index(), SYS_MESSAGE_TYPE.invoiceReceived.index()]

    def _needToShowAward(self, ctx):
        _, message = ctx
        return message is not None and message.type in self.__questTypes and message.data is not None

    def _showAward(self, ctx):
        messageData = ctx[1].data
        if 'data' in messageData:
            data = messageData['data']
        else:
            data = messageData
        tokensDict = data.get('tokens', {})
        for tokenName in tokensDict:
            recruitInfo = recruit_helper.getRecruitInfo(tokenName)
            if recruitInfo is not None:
                self._showWindow(recruitInfo.getLabel())
                return

        return

    @staticmethod
    def _showWindow(eventKey):
        event = i18n.makeString(eventKey)
        SystemMessages.pushMessage(i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_RECRUITGIFT_TEXT, event=event), SystemMessages.SM_TYPE.RecruitGift, messageData={'header': i18n.makeString(MESSENGER.SERVICECHANNELMESSAGES_RECRUITGIFT_HEADER)})


class MotiveQuestsWindowHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(MotiveQuestsWindowHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        motiveQuests = self.eventsCache.getMotiveQuests()
        for qID in data.get('completedQuestIDs', set()):
            if qID in motiveQuests and self.isShowCongrats(motiveQuests[qID]):
                quests_events.showMotiveAward(motiveQuests[qID])


class QuestBoosterAwardHandler(ServiceChannelHandler):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, awardCtrl):
        super(QuestBoosterAwardHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        goodies = data.get('goodies', {})
        for boosterID in goodies:
            booster = self.goodiesCache.getBooster(boosterID)
            if booster is not None and booster.enabled:
                shared_events.showBoosterAward(booster)

        return


class BoosterAfterBattleAwardHandler(ServiceChannelHandler):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, awardCtrl):
        super(BoosterAfterBattleAwardHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        goodies = ctx[1].data.get('goodies', {})
        for boosterID in goodies:
            booster = self.goodiesCache.getBooster(boosterID)
            if booster is not None and booster.enabled:
                shared_events.showBoosterAward(booster)

        return


class BattleQuestsAutoWindowHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(BattleQuestsAutoWindowHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.personalMissionRebalance.index()), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuests = {}
        allQuests = self.eventsCache.getAllQuests(includePersonalMissions=True, filterFunc=self._isAppropriate)
        completedQuestUniqueIDs = message.data.get('completedQuestIDs', set())
        for uniqueQuestID in completedQuestUniqueIDs:
            questID, ctx = self._getContext(uniqueQuestID, completedQuests, completedQuestUniqueIDs)
            if questID in allQuests:
                quest = allQuests[questID]
                if self.isShowCongrats(quest):
                    vehiclesList = message.data.get('vehicles', [])
                    vehiclesDict = vehiclesList[0] if vehiclesList else {}
                    ctx.update({'eventsCache': self.eventsCache,
                     'bonusVehicles': vehiclesDict})
                    quest = _getBlueprintActualBonus(message.data, quest)
                    completedQuests[questID] = (quest, ctx)

        values = sorted(completedQuests.values(), key=lambda v: v[0].getID())
        for quest, context in values:
            self._showWindow(quest, context)

    @staticmethod
    def _showWindow(quest, context):
        quests_events.showMissionAward(quest, context)

    @staticmethod
    def _isAppropriate(quest):
        return quest.getType() in (EVENT_TYPE.BATTLE_QUEST,
         EVENT_TYPE.TOKEN_QUEST,
         EVENT_TYPE.PERSONAL_QUEST,
         EVENT_TYPE.RANKED_QUEST)

    @staticmethod
    def _getContext(uniqueQuestID, completedQuests, completedQuestUniqueIDs):
        return (uniqueQuestID, {})


class PersonalMissionAutoWindowHandler(BattleQuestsAutoWindowHandler):

    @staticmethod
    def _showWindow(quest, context):
        quests_events.showPersonalMissionAward(quest, context)

    @staticmethod
    def _isAppropriate(quest):
        return quest.getType() == EVENT_TYPE.PERSONAL_MISSION

    @staticmethod
    def _getContext(uniqueQuestID, completedQuests, completedQuestUniqueIDs):
        if personal_missions.g_cache.isPersonalMission(uniqueQuestID):
            pqType = personal_missions.g_cache.questByUniqueQuestID(uniqueQuestID)
            if pqType.id not in completedQuests:
                ctx = {'isMainReward': pqType.mainQuestID in completedQuestUniqueIDs,
                 'isAddReward': pqType.addQuestID in completedQuestUniqueIDs,
                 'awardListReturned': uniqueQuestID.endswith('_add_award_list')}
                return (pqType.id, ctx)
            if uniqueQuestID.endswith('_add_award_list'):
                _, ctx = completedQuests[pqType.id]
                ctx.update(awardListReturned=True)
        return (None, {})


class PersonalMissionByAwardListHandler(PersonalMissionAutoWindowHandler):

    def _needToShowAward(self, ctx):
        _, msg = ctx
        if msg is not None and isinstance(msg.data, types.DictType):
            completedQuestUniqueIDs = msg.data.get('completedQuestIDs', set())
            for uniqueQuestID in completedQuestUniqueIDs:
                if personal_missions.g_cache.isPersonalMission(uniqueQuestID) and uniqueQuestID.endswith('_main_award_list'):
                    return True

        return False

    @staticmethod
    def _getContext(uniqueQuestID, completedQuests, completedQuestUniqueIDs):
        if personal_missions.g_cache.isPersonalMission(uniqueQuestID):
            pqType = personal_missions.g_cache.questByUniqueQuestID(uniqueQuestID)
            if pqType.id not in completedQuests:
                ctx = {'isMainReward': True,
                 'isAddReward': False,
                 'isAwardListUsed': True}
                return (pqType.id, ctx)
        return (None, {})


class PersonalMissionOperationAwardHandler(BattleQuestsAutoWindowHandler):
    __FINAL_BRANCHES_OPERATION_IDS = tuple([ ids[-1] for ids in BRANCH_TO_OPERATION_IDS.values() ])
    __CHAMPION_BADGES_IDS = CHAMPION_BADGES_BY_BRANCH.values()

    def __init__(self, awardCtrl):
        super(PersonalMissionOperationAwardHandler, self).__init__(awardCtrl)
        self.__postponedAwards = []
        self.__openedOperationsAwards = set()
        self.__delayedWindows = {}

    def init(self):
        super(PersonalMissionOperationAwardHandler, self).init()
        g_eventBus.addListener(PersonalMissionsEvent.ON_AWARD_SCEEN_CLOSE, self.__onAwardScreenClose, EVENT_BUS_SCOPE.LOBBY)

    def fini(self):
        super(PersonalMissionOperationAwardHandler, self).fini()
        g_eventBus.removeListener(PersonalMissionsEvent.ON_AWARD_SCEEN_CLOSE, self.__onAwardScreenClose, EVENT_BUS_SCOPE.LOBBY)
        self.__delayedWindows.clear()
        self.__postponedAwards = []
        self.__openedOperationsAwards.clear()

    def _needToShowAward(self, ctx):
        _, msg = ctx
        if msg is not None and isinstance(msg.data, types.DictType):
            completedQuestUniqueIDs = msg.data.get('completedQuestIDs', set())
            for uniqueQuestID in completedQuestUniqueIDs:
                if personal_missions.g_cache.isPersonalMission(uniqueQuestID):
                    pqType = personal_missions.g_cache.questByUniqueQuestID(uniqueQuestID)
                    if pqType.isFinal:
                        self.__openedOperationsAwards.add((pqType.id, pqType.tileID))
                for operationID, prefixes in PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID.iteritems():
                    if uniqueQuestID.startswith(prefixes):
                        if uniqueQuestID in self.__CHAMPION_BADGES_IDS:
                            return True
                        if operationID in self.__FINAL_BRANCHES_OPERATION_IDS:
                            pmCache = self.eventsCache.getPersonalMissions()
                            operation = pmCache.getAllOperations()[operationID]
                            operations = pmCache.getOperationsForBranch(operation.getBranch())
                            if all([ op.isFullCompleted() for op in operations.itervalues() ]):
                                self.__postponedAwards.append(uniqueQuestID)
                            else:
                                return True
                        else:
                            return True

        return False

    def _showAward(self, ctx):
        _, message = ctx
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        allQuests = self.eventsCache.getHiddenQuests()
        for operationId, prefixes in PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID.iteritems():
            quests = []
            for uniqueQuestID in completedQuestIDs:
                if uniqueQuestID.startswith(prefixes) and uniqueQuestID in allQuests:
                    quests.append(uniqueQuestID)

            if quests:
                ctx = {'operationID': operationId,
                 'branch': getBranchByOperationId(operationId),
                 'questIds': quests + self.__postponedAwards}
                self._showWindow(None, ctx)
                self.__postponedAwards = []

        return

    def _showWindow(self, quest, context):
        opId = context['operationID']
        operations = [ data[1] for data in self.__openedOperationsAwards ]
        if opId not in operations:
            quests_events.showPersonalMissionsOperationAwardsScreen(context)
        else:
            self.__delayedWindows[opId] = context

    def __onAwardScreenClose(self, event):
        opID = event.ctx['operationID']
        eventID = event.ctx['eventID']
        if (eventID, opID) in self.__openedOperationsAwards:
            self.__openedOperationsAwards.discard((eventID, opID))
        operations = [ data[1] for data in self.__openedOperationsAwards ]
        if opID not in operations and opID in self.__delayedWindows:
            quests_events.showPersonalMissionsOperationAwardsScreen(self.__delayedWindows.pop(opID))


class PersonalMissionOperationUnlockedHandler(BattleQuestsAutoWindowHandler):
    OPERATION_COMPLETION_IDS = {'pt_final_s1_t1': 1,
     'pt_final_s1_t2': 2,
     'pt_final_s1_t3': 3,
     'pt_final_s1_t4': 4,
     'pt_final_s2_t5': 5,
     'pt_final_s2_t6': 6,
     'pt_final_s2_t7': 7}

    def _needToShowAward(self, ctx):
        _, msg = ctx
        if msg is not None and isinstance(msg.data, types.DictType):
            completedQuestUniqueIDs = msg.data.get('completedQuestIDs', set())
            for uniqueQuestID in completedQuestUniqueIDs:
                if uniqueQuestID in self.OPERATION_COMPLETION_IDS:
                    return True

        return False

    def _showAward(self, ctx):
        _, message = ctx
        allQuests = self.eventsCache.getHiddenQuests()
        operations = self.eventsCache.getPersonalMissions().getAllOperations()
        context = {'eventsCache': self.eventsCache}
        completedQuestUniqueIDs = message.data.get('completedQuestIDs', set())
        for uniqueQuestID in (qID for qID in completedQuestUniqueIDs if qID in allQuests):
            for oCompletionID, oID in self.OPERATION_COMPLETION_IDS.iteritems():
                if uniqueQuestID == oCompletionID:
                    quest = allQuests[uniqueQuestID]
                    operation = operations[oID]
                    nextOperationIDs = operation.getNextOperationIDs()
                    for nextOperationID in nextOperationIDs:
                        ctx = {'nextOperationID': nextOperationID}
                        ctx.update(context)
                        self._showWindow(quest, ctx)

    @staticmethod
    def _showWindow(quest, context):
        quests_events.showOperationUnlockedAward(quest, context)


class SpecialAchievement(AwardHandler):
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self, key, awardCtrl, awardCountToMessage):
        super(SpecialAchievement, self).__init__(awardCtrl)
        self.__key = key
        self._awardCntToMsg = awardCountToMessage

    def isChanged(self, value):
        return value != AccountSettings.getFilter(AWARDS).get(self.__key)

    def getAchievementCount(self):
        raise NotImplementedError

    def showAwardWindow(self, achievementCount, messageNumber):
        raise NotImplementedError

    def _needToShowAward(self, ctx=None):
        return (not self._awardCtrl.canShow() or self._getAchievementToShow() is not None) and not self.bootcampController.isInBootcamp()

    def _getAchievementToShow(self):
        achievementCount = self.getAchievementCount()
        lastElement = max(self._awardCntToMsg.keys())
        if achievementCount != 0 and self.isChanged(achievementCount):
            if achievementCount in self._awardCntToMsg or achievementCount % lastElement == 0:
                return achievementCount
            sortedKeys = sorted(self._awardCntToMsg.keys(), reverse=True)
            for i in xrange(len(sortedKeys) - 1):
                if sortedKeys[i] > achievementCount and achievementCount > sortedKeys[i + 1] and self.isChanged(sortedKeys[i + 1]):
                    return sortedKeys[i + 1]

        return None

    def _showAward(self, ctx=None):
        achievementCount = self._getAchievementToShow()
        if achievementCount is not None:
            messageNumber = self._awardCntToMsg.get(achievementCount, self._awardCntToMsg[max(self._awardCntToMsg.keys())])
            self.__setNewValue(achievementCount)
            self.showAwardWindow(achievementCount, messageNumber)
        return

    def __setNewValue(self, value):
        achievement = AccountSettings.getFilter(AWARDS)
        achievement[self.__key] = value
        AccountSettings.setFilter(AWARDS, achievement)


class VehiclesResearchHandler(SpecialAchievement):
    VEHICLE_AMOUNT = {2: 1,
     5: 2,
     10: 3,
     20: 4,
     30: 1}

    def __init__(self, awardCtrl):
        super(VehiclesResearchHandler, self).__init__('vehicleResearchAward', awardCtrl, VehiclesResearchHandler.VEHICLE_AMOUNT)

    def init(self):
        g_clientUpdateManager.addCallbacks({'stats.unlocks': self.onUnlocksChanged})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def getAchievementCount(self):
        return len(self.itemsCache.items.getVehicles(criteria=REQ_CRITERIA.UNLOCKED | ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.VEHICLE.PREMIUM | ~REQ_CRITERIA.VEHICLE.LEVELS([1]) | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR))

    def onUnlocksChanged(self, unlocks):
        isChanged = False
        for unlock in list(unlocks):
            if getTypeOfCompactDescr(unlock) == ITEM_TYPE_INDICES['vehicle']:
                isChanged = True

        if isChanged:
            self.handle()

    def showAwardWindow(self, achievementCount, messageNumber):
        return shared_events.showResearchAward(achievementCount, messageNumber)


class VictoryHandler(SpecialAchievement):
    VICTORY_AMOUNT = {5: 1,
     10: 2,
     20: 3,
     50: 4,
     100: 1,
     250: 2,
     500: 3,
     1000: 4}

    def __init__(self, awardCtrl):
        super(VictoryHandler, self).__init__('victoryAward', awardCtrl, VictoryHandler.VICTORY_AMOUNT)

    def init(self):
        g_playerEvents.onGuiCacheSyncCompleted += self.handle
        g_playerEvents.onDossiersResync += self.handle
        g_playerEvents.onBattleResultsReceived += self.handle

    def fini(self):
        g_playerEvents.onGuiCacheSyncCompleted -= self.handle
        g_playerEvents.onDossiersResync -= self.handle
        g_playerEvents.onBattleResultsReceived -= self.handle

    def getAchievementCount(self):
        return self.itemsCache.items.getAccountDossier().getTotalStats().getWinsCount()

    def showAwardWindow(self, achievementCount, messageNumber):
        return shared_events.showVictoryAward(achievementCount, messageNumber)


class BattlesCountHandler(SpecialAchievement):
    BATTLE_AMOUNT = {50: 2,
     100: 3,
     250: 4,
     500: 1,
     1000: 2,
     2000: 3,
     5000: 4,
     7500: 1,
     10000: 2}

    def __init__(self, awardCtrl, key='battlesCountAward'):
        super(BattlesCountHandler, self).__init__(key, awardCtrl, self._getAwardCountToMessage())

    def init(self):
        g_playerEvents.onGuiCacheSyncCompleted += self.handle
        g_playerEvents.onDossiersResync += self.handle
        g_playerEvents.onBattleResultsReceived += self.handle

    def fini(self):
        g_playerEvents.onGuiCacheSyncCompleted -= self.handle
        g_playerEvents.onDossiersResync -= self.handle
        g_playerEvents.onBattleResultsReceived -= self.handle

    def getAchievementCount(self):
        return self.itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()

    def showAwardWindow(self, achievementCount, messageNumber):
        return shared_events.showBattleAward(achievementCount, messageNumber)

    def _getAwardCountToMessage(self):
        return BattlesCountHandler.BATTLE_AMOUNT


class PveBattlesCountHandler(BattlesCountHandler):

    def __init__(self, awardCtrl):
        super(PveBattlesCountHandler, self).__init__(awardCtrl, 'pveBattlesCountAward')

    def getAchievementCount(self):
        return self.itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()

    def showAwardWindow(self, achievementCount, messageNumber):
        return shared_events.showPveBattleAward(achievementCount, messageNumber)

    def _getAwardCountToMessage(self):
        return {BATTLES_TO_SELECT_RANDOM_MIN_LIMIT: 1}

    def _getAchievementToShow(self):
        achievementCount = self.getAchievementCount()
        if achievementCount != 0 and self.isChanged(achievementCount):
            if achievementCount in self._awardCntToMsg:
                return achievementCount
        return None


class GoldFishHandler(AwardHandler):

    def start(self):
        self.handle()

    def _needToShowAward(self, ctx):
        return True

    def _showAward(self, ctx):
        if isGoldFishActionActive() and isTimeToShowGoldFishPromo():
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.GOLD_FISH_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)


class TelecomHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(TelecomHandler, self).__init__(SYS_MESSAGE_TYPE.telecomOrderCreated.index(), awardCtrl)

    @staticmethod
    def __getVehileDesrs(data):
        return [ vehicles_core.getVehicleType(vehDesr).compactDescr for vehDesr in data['data']['vehicles'] ]

    def _showAward(self, ctx):
        data = ctx[1].data
        hasCrew = TelecomReceivedInvoiceFormatter.invoiceHasCrew(data)
        hasBrotherhood = TelecomReceivedInvoiceFormatter.invoiceHasBrotherhood(data)
        vehicleDesrs = self.__getVehileDesrs(data)
        if vehicleDesrs:
            shared_events.showTelecomAward(vehicleDesrs, hasCrew, hasBrotherhood)
        else:
            _logger.error("Can't show telecom award window!")


class RankedQuestsHandler(MultiTypeServiceChannelHandler):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, awardCtrl):
        super(RankedQuestsHandler, self).__init__((SYS_MESSAGE_TYPE.rankedQuests.index(), SYS_MESSAGE_TYPE.tokenQuests.index()), awardCtrl)
        self.__pending = []
        self.__locked = False

    def _showAward(self, ctx):
        _, message = ctx
        data = message.data.copy()
        for questID in filter(ranked_helpers.isRankedQuestID, data.pop('completedQuestIDs', [])):
            if message.type == SYS_MESSAGE_TYPE.rankedQuests.index():
                quest = self.eventsCache.getRankedQuests().get(questID)
                if quest:
                    if quest.isBooby():
                        self.__processOrHold(self.__showBoobyAwardWindow, (quest,))
            if message.type == SYS_MESSAGE_TYPE.tokenQuests.index():
                quest = self.eventsCache.getHiddenQuests().get(questID)
                if quest:
                    self.__processOrHold(self.__showSeasonAward, (quest, data))

    def __processOrHold(self, method, args):
        if self.__locked:
            self.__pending.append((method, args))
        else:
            self.__locked = True
            method(*args)

    def __unlock(self):
        self.__locked = False
        if self.__pending:
            self.__processOrHold(*self.__pending.pop(0))

    def __showSeasonAward(self, quest, data):
        seasonID, _ = ranked_helpers.getRankedDataFromTokenQuestID(quest.getID())
        season = self.rankedController.getSeason(seasonID)
        if season is not None:
            g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, ctx={'quest': quest,
             'awards': data,
             'closeClb': self.__unlock}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.__unlock()
        return

    def __showBoobyAwardWindow(self, quest):
        quests_events.showRankedBoobyAward(quest)
        self.__unlock()


class SoundDeviceHandler(AwardHandler):
    soundsCtrl = dependency.descriptor(ISoundsController)
    settingsCore = dependency.descriptor(ISettingsCore)

    def start(self):
        self.handle()

    def _needToShowAward(self, ctx):
        deviceSetting = self.settingsCore.options.getSetting(SOUND.SOUND_DEVICE)
        isValid, currentDeviceID = deviceSetting.getSystemState()
        if isValid:
            return False
        lastDeviceID = AccountSettings.getFilter(SPEAKERS_DEVICE)
        return False if currentDeviceID == lastDeviceID else True

    def _showAward(self, ctx):
        DialogsInterface.showI18nConfirmDialog('soundSpeakersPresetReset', callback=self.__callback)

    def __callback(self, result):
        deviceSetting = self.settingsCore.options.getSetting(SOUND.SOUND_DEVICE)
        if result:
            deviceSetting.apply(deviceSetting.SYSTEMS.SPEAKERS)
            self.soundsCtrl.system.setUserSpeakersPresetID(SPEAKERS_CONFIG.AUTO_DETECTION)
        else:
            _, currentDeviceID = deviceSetting.getSystemState()
            AccountSettings.setFilter(SPEAKERS_DEVICE, currentDeviceID)


class ProgressiveRewardHandler(ServiceChannelHandler):
    _gui = dependency.descriptor(IGuiLoader)

    def __init__(self, awardCtrl):
        super(ProgressiveRewardHandler, self).__init__(SYS_MESSAGE_TYPE.progressiveReward.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        bonuses, specialRewardType = getProgressiveRewardBonuses(message.data['rewards'])
        if bonuses:
            showProgressiveRewardAwardWindow(bonuses, specialRewardType, message.data['level'])
        else:
            _logger.error("Can't show empty or invalid reward!")


def _getBlueprintActualBonus(data, quest):
    if 'blueprints' in data:
        blueprintActualBonus = data.get('blueprints', {})
        actualQuest = deepcopy(quest)
        actualQuest.getData()['bonus'].update({'blueprints': blueprintActualBonus})
        return actualQuest
    return quest
