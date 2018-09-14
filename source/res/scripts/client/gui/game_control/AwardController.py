# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/AwardController.py
import types
import weakref
from abc import ABCMeta, abstractmethod
import ArenaType
import gui.awards.event_dispatcher as shared_events
import potapov_quests
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, AWARDS
from account_shared import getFairPlayViolationName
from chat_shared import SYS_MESSAGE_TYPE
from constants import EVENT_TYPE, QUEUE_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING, LOG_ERROR, LOG_DEBUG
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.layouts import POTAPOV_QUESTS_GROUP
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18PunishmentDialogMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.prb_control.storages import prequeue_storage_getter
from gui.ranked_battles import ranked_helpers
from gui.server_events import events_dispatcher as quests_events
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.transport import z_loads
from helpers import dependency
from helpers import i18n
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr, vehicles as vehicles_core
from messenger.formatters import NCContextItemFormatter, TimeFormatter
from messenger.formatters.service_channel import TelecomReceivedInvoiceFormatter
from messenger.proto.events import g_messengerEvents
from potapov_quests import PQ_BRANCH
from shared_utils import findFirst
from skeletons.gui.game_control import IRefSystemController, IAwardController, IRankedBattlesController, IBootcampController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class AwardController(IAwardController, IGlobalListener):
    refSystem = dependency.descriptor(IRefSystemController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.__handlers = [BattleQuestsAutoWindowHandler(self),
         QuestBoosterAwardHandler(self),
         BoosterAfterBattleAwardHandler(self),
         PunishWindowHandler(self),
         RefSystemQuestsWindowHandler(self),
         PotapovQuestsBonusHandler(self),
         PotapovWindowAfterBattleHandler(self),
         TokenQuestsWindowHandler(self),
         MotiveQuestsWindowHandler(self),
         RefSysStatusWindowHandler(self),
         VehiclesResearchHandler(self),
         VictoryHandler(self),
         BattlesCountHandler(self),
         PveBattlesCountHandler(self),
         PotapovQuestsAutoWindowHandler(self),
         GoldFishHandler(self),
         FalloutVehiclesBuyHandler(self),
         TelecomHandler(self),
         RankedQuestsHandler(self)]
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
            LOG_DEBUG('Postponed award call:', handler, ctx)
            self.__delayedHandlers.append((handler, ctx))

    def handlePostponed(self, *args):
        if self.canShow():
            for handler, ctx in self.__delayedHandlers:
                LOG_DEBUG('Calling postponed award handler:', handler, ctx)
                handler(ctx)

            self.__delayedHandlers = []

    def canShow(self):
        popupsWindowsDisabled = isPopupsWindowsOpenDisabled()
        prbDispatcher = self.prbDispatcher
        return self.__isLobbyLoaded and not popupsWindowsDisabled if prbDispatcher is None else self.__isLobbyLoaded and not popupsWindowsDisabled and not (prbDispatcher.getFunctionalState().hasLockedState or prbDispatcher.getPlayerInfo().isReady)

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

    def __init__(self, type, awardCtrl):
        super(ServiceChannelHandler, self).__init__(awardCtrl)
        self.__type = type

    def init(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.handle

    def fini(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.handle

    def _needToShowAward(self, ctx):
        _, message = ctx
        return message is not None and message.type == self.__type and message.data is not None


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
            from gui.DialogsInterface import showDialog
            showDialog(I18PunishmentDialogMeta('punishmentWindow', None, {'penaltyType': penaltyType,
             'arenaName': i18n.makeString(arenaType.name),
             'time': TimeFormatter.getActualMsgTimeStr(arenaCreateTime),
             'reason': i18n.makeString(DIALOGS.all('punishmentWindow/reason/%s' % getFairPlayViolationName(violation)))}), lambda *args: None)
        return


class RefSystemQuestsWindowHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(RefSystemQuestsWindowHandler, self).__init__(SYS_MESSAGE_TYPE.refSystemQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        for tmanCompDescr in message.data.get('tankmen') or []:
            self._awardCtrl.refSystem.showTankmanAwardWindow(Tankman(tmanCompDescr), completedQuestIDs)

        for vehiclesData in message.data.get('vehicles', []):
            for vehTypeCompDescr in vehiclesData:
                self._awardCtrl.refSystem.showVehicleAwardWindow(Vehicle(typeCompDescr=abs(vehTypeCompDescr)), completedQuestIDs)

        self._awardCtrl.refSystem.showCreditsAwardWindow(message.data.get('credits', 0), completedQuestIDs)


class PotapovQuestsBonusHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PotapovQuestsBonusHandler, self).__init__(SYS_MESSAGE_TYPE.potapovQuestBonus.index(), awardCtrl)

    def _showAward(self, ctx):
        LOG_DEBUG('Show potapov quest bonus award!', ctx)
        data = ctx[1].data
        completedQuestIDs = set(data.get('completedQuestIDs', set()))
        achievements = []
        tokens = {}
        for recordIdx, value in data.get('popUpRecords', []):
            factory = getAchievementFactory(DB_ID_TO_RECORD[recordIdx])
            if factory is not None:
                a = factory.create(value=int(value))
                if a is not None:
                    achievements.append(a)

        for tokenID, tokenData in (data.get('tokens') or {}).iteritems():
            tokens[tokenID] = tokenData.get('count', 1)

        if len(achievements):
            quests_events.showAchievementsAward(achievements)
        for tID, tCount in tokens.iteritems():
            self.__tryToShowTokenAward(tID, tCount, completedQuestIDs)

        return

    def __tryToShowTokenAward(self, tID, tCount, completedQuestIDs):
        for q in self.eventsCache.getQuestsByTokenBonus(tID):
            if q.getType() == EVENT_TYPE.POTAPOV_QUEST and q.getQuestBranch() == PQ_BRANCH.REGULAR:
                pqType = q.getPQType()
                if pqType.mainQuestID in completedQuestIDs or pqType.addQuestID in completedQuestIDs:
                    quests_events.showTokenAward(q, tID, tCount)
                    return True

        return False


class PotapovWindowAfterBattleHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PotapovWindowAfterBattleHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        achievements = []
        popUpRecords = ctx[1].data.get('popUpRecords', [])
        for recordIdx, value in popUpRecords:
            recordName = DB_ID_TO_RECORD[recordIdx]
            if recordName in POTAPOV_QUESTS_GROUP:
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
        allQuests = self.eventsCache.getAllQuests(includePotapovQuests=True)
        needToShowVehAwardWindow = False
        for qID in data.get('completedQuestIDs', set()):
            if qID in allQuests:
                if self.isShowCongrats(allQuests[qID]):
                    completedQuests[qID] = (allQuests[qID], {'eventsCache': self.eventsCache})
                for tokenID, children in allQuests[qID].getChildren().iteritems():
                    for chID in children:
                        chQuest = allQuests[chID]
                        if chQuest.getType() == EVENT_TYPE.POTAPOV_QUEST:
                            needToShowVehAwardWindow = True
                            break

        if needToShowVehAwardWindow:
            for vehiclesData in data.get('vehicles', []):
                for vehTypeCompDescr in vehiclesData:
                    quests_events.showVehicleAward(Vehicle(typeCompDescr=abs(vehTypeCompDescr)))

        for quest, context in completedQuests.itervalues():
            self._showWindow(quest, context)

    @staticmethod
    def _showWindow(quest, context):
        """Fire an actual show event to display an award window.
        
        :param quest: instance of event_items.Quest (or derived)
        :param context: dict with required data
        """
        quests_events.showMissionAward(quest, context)


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


class BattleQuestsAutoWindowHandler(ServiceChannelHandler):
    """ Handler responsible for battle quests awards.
    """

    def __init__(self, awardCtrl):
        super(BattleQuestsAutoWindowHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuests = {}
        allQuests = self.eventsCache.getAllQuests(includePotapovQuests=True, filterFunc=lambda quest: self._isAppropriate(quest))
        completedQuestUniqueIDs = message.data.get('completedQuestIDs', set())
        for uniqueQuestID in completedQuestUniqueIDs:
            questID, ctx = self._getContext(uniqueQuestID, completedQuests, completedQuestUniqueIDs)
            if questID in allQuests:
                quest = allQuests[questID]
                if self.isShowCongrats(quest):
                    ctx.update(eventsCache=self.eventsCache)
                    completedQuests[questID] = (quest, ctx)

        for quest, context in completedQuests.itervalues():
            self._showWindow(quest, context)

    @staticmethod
    def _showWindow(quest, context):
        """Fire an actual show event to display an award window.
        
        :param quest: instance of event_items.Quest (or derived)
        :param context: dict with required data
        """
        quests_events.showMissionAward(quest, context)

    @staticmethod
    def _isAppropriate(quest):
        """ Check if quest is appropriate for the current handler's scope.
        
        :param quest: instance of event_items.Quest (or derived)
        """
        return quest.getType() in (EVENT_TYPE.BATTLE_QUEST,
         EVENT_TYPE.TOKEN_QUEST,
         EVENT_TYPE.PERSONAL_QUEST,
         EVENT_TYPE.RANKED_QUEST)

    @staticmethod
    def _getContext(uniqueQuestID, completedQuests, completedQuestUniqueIDs):
        """ Gather the data needed by award window and get real quest id.
        
        :param uniqueQuestID: unique id of the quest (considering its sub quests)
        :param completedQuests: dict {questID: (quest, context)}
        :param completedQuestUniqueIDs: list with ids of completed quests
        
        :return: tuple (quest id, context)
        """
        return (uniqueQuestID, {})


class PotapovQuestsAutoWindowHandler(BattleQuestsAutoWindowHandler):
    """ Handler responsible for personal quests awards.
    """

    @staticmethod
    def _showWindow(quest, context):
        quests_events.showPersonalMissionAward(quest, context)

    @staticmethod
    def _isAppropriate(quest):
        return quest.getType() == EVENT_TYPE.POTAPOV_QUEST

    @staticmethod
    def _getContext(uniqueQuestID, completedQuests, completedQuestUniqueIDs):
        if potapov_quests.g_cache.isPotapovQuest(uniqueQuestID):
            pqType = potapov_quests.g_cache.questByUniqueQuestID(uniqueQuestID)
            if pqType.id not in completedQuests:
                ctx = {'isMainReward': pqType.mainQuestID in completedQuestUniqueIDs,
                 'isAddReward': pqType.addQuestID in completedQuestUniqueIDs}
                return (pqType.id, ctx)
        return (None, {})


class RefSysStatusWindowHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(RefSysStatusWindowHandler, self).__init__(SYS_MESSAGE_TYPE.notificationsCenter.index(), awardCtrl)

    def _showAward(self, ctx):
        data = z_loads(ctx[1].data)
        if 'window' not in data:
            return
        context = {}
        if 'context' in data:
            context = self.__formatContext(data['context'])
        if data['window'] == 1:
            self.__showRefSystemNotification('showReferrerIntroWindow', invitesCount=context.get('invites_count', 0))
        elif data['window'] == 2:
            self.__showRefSystemNotification('showReferralIntroWindow', nickname=context['nickname'], isNewbie=True)
        elif data['window'] == 3:
            self.__showRefSystemNotification('showReferralIntroWindow', nickname=context['nickname'], isNewbie=False)
        else:
            LOG_WARNING('Unknown referral system user status window', data)

    def __showRefSystemNotification(self, methodName, **ctx):
        try:
            getattr(self._awardCtrl.refSystem, methodName)(**ctx)
        except:
            LOG_ERROR('There is exception while processing notification center window', methodName, ctx)
            LOG_CURRENT_EXCEPTION()

    def __formatContext(self, ctx):
        result = {}
        if type(ctx) is not types.DictType:
            LOG_ERROR('Context is invalid', ctx)
            return result
        getItemFormat = NCContextItemFormatter.getItemFormat
        for key, item in ctx.iteritems():
            if len(item) > 1:
                itemType, itemValue = item[0:2]
                result[key] = getItemFormat(itemType, itemValue)
            LOG_ERROR('Context item is invalid', item)
            result[key] = str(item)

        return result


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


class FalloutVehiclesBuyHandler(AwardHandler):
    eventsCache = dependency.descriptor(IEventsCache)

    def start(self):
        hasVehicleLvl8 = False
        hasVehicleLvl10 = False
        if not self.falloutStorage.hasVehicleLvl8():
            if self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT | REQ_CRITERIA.VEHICLE.LEVELS(range(8, 10))):
                hasVehicleLvl8 = True
        if not self.falloutStorage.hasVehicleLvl10():
            if self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT | REQ_CRITERIA.VEHICLE.LEVEL(10)):
                hasVehicleLvl10 = True
        if hasVehicleLvl8 or hasVehicleLvl10:
            self.falloutStorage.setHasVehicleLvls(hasVehicleLvl8, hasVehicleLvl10)
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onVehsChanged})

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    @prequeue_storage_getter(QUEUE_TYPE.FALLOUT)
    def falloutStorage(self):
        return None

    def _needToShowAward(self, ctx=None):
        return self._awardCtrl.canShow() is False or self._shouldBeShown()

    def _shouldBeShown(self):
        return self.eventsCache.isFalloutEnabled() and (not self.falloutStorage.hasVehicleLvl8() or not self.falloutStorage.hasVehicleLvl10())

    def _showAward(self, ctx=None):
        if self._shouldBeShown():
            if not self.falloutStorage.hasVehicleLvl8():
                for vehicle in self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT | REQ_CRITERIA.VEHICLE.LEVELS(range(8, 10))).itervalues():
                    self.falloutStorage.setHasVehicleLvl8()
                    shared_events.showFalloutAward((vehicle.level,))
                    break

            if not self.falloutStorage.hasVehicleLvl10() and self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT | REQ_CRITERIA.VEHICLE.LEVEL(10)):
                self.falloutStorage.setHasVehicleLvl10()
                shared_events.showFalloutAward((10,), True)

    def __onVehsChanged(self, *args):
        self.handle()


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
            LOG_ERROR("Can't show telecom award window!")


class MultiTypeServiceChannelHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl, handledTypes):
        super(MultiTypeServiceChannelHandler, self).__init__(None, awardCtrl)
        self.__types = handledTypes
        return

    def _needToShowAward(self, ctx):
        _, message = ctx
        return message is not None and message.type in self.__types and message.data is not None

    def _showAward(self, ctx):
        pass


class RankedQuestsHandler(MultiTypeServiceChannelHandler):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, awardCtrl):
        super(RankedQuestsHandler, self).__init__(awardCtrl, (SYS_MESSAGE_TYPE.rankedQuests.index(), SYS_MESSAGE_TYPE.tokenQuests.index()))
        self.__pending = []
        self.__locked = False

    def _showAward(self, ctx):
        _, message = ctx
        data = message.data.copy()
        for questID in filter(ranked_helpers.isRankedQuestID, data.pop('completedQuestIDs', [])):
            if message.type == SYS_MESSAGE_TYPE.rankedQuests.index():
                quest = self.eventsCache.getRankedQuests().get(questID)
                if quest:
                    if quest.isProcessedAtCycleEnd():
                        self.__processOrHold(self.__showCycleAward, (quest, data))
                    elif quest.isBooby():
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

    def __showCycleAward(self, quest, data):
        season = self.rankedController.getSeason(quest.getSeasonID())
        if season is not None:
            g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_STAGE_COMPLETE, ctx={'quest': quest,
             'awards': data,
             'closeClb': self.__unlock,
             'season': season}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.__unlock()
        return

    def __showSeasonAward(self, quest, data):
        seasonID, _, _ = ranked_helpers.getRankedDataFromTokenQuestID(quest.getID())
        season = self.rankedController.getSeason(seasonID)
        if season is not None:
            g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, ctx={'quest': quest,
             'awards': data,
             'closeClb': self.__unlock,
             'season': season}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.__unlock()
        return

    def __showBoobyAwardWindow(self, quest):
        quests_events.showRankedBoobyAward(quest)
        self.__unlock()
