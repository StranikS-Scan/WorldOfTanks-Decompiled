# Embedded file name: scripts/client/gui/game_control/AwardController.py
import types
import weakref
from abc import ABCMeta, abstractmethod
import ArenaType
from goodies.goodie_constants import GOODIE_TARGET_TYPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.goodies.GoodiesCache import g_goodiesCache
from gui.shared.economics import getPremiumCostActionPrc
from gui.shared.utils import findFirst
import potapov_quests
import gui.awards.event_dispatcher as shared_events
from constants import EVENT_TYPE
from helpers import i18n
from chat_shared import SYS_MESSAGE_TYPE
from account_helpers.AccountSettings import AccountSettings, AWARDS
from account_shared import getFairPlayViolationName
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING, LOG_ERROR, LOG_DEBUG
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr
from messenger.proto.events import g_messengerEvents
from messenger.formatters import NCContextItemFormatter, TimeFormatter
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.layouts import POTAPOV_QUESTS_GROUP
from gui.Scaleform.daapi.view.dialogs import I18PunishmentDialogMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.server_events import events_dispatcher as quests_events
from gui.server_events import g_eventsCache
from gui.game_control.controllers import Controller
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared import g_itemsCache, EVENT_BUS_SCOPE, REQ_CRITERIA, g_eventBus, events
from gui.shared.utils.transport import z_loads
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.prb_helpers import GlobalListener
from PlayerEvents import g_playerEvents
from FortifiedRegionBase import FORT_ATTACK_RESULT

class AwardController(Controller, GlobalListener):

    def __init__(self, proxy):
        super(AwardController, self).__init__(proxy)
        self.__handlers = [PunishWindowHandler(self),
         RefSystemQuestsWindowHandler(self),
         FortResultsWindowHandler(self),
         PotapovQuestsBonusHandler(self),
         PotapovWindowAfterBattleHandler(self),
         TokenQuestsWindowHandler(self),
         RefSysStatusWindowHandler(self),
         VehiclesResearchHandler(self),
         VictoryHandler(self),
         BattlesCountHandler(self),
         PotapovQuestsAutoWindowHandler(self),
         PersonalDiscountHandler(self),
         QuestBoosterAwardHandler(self),
         BoosterAfterBattleAwardHandler(self),
         GoldFishHandler(self)]
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
            self.__delayedHandlers.append((handler, ctx))

    def handlePostponed(self, *args):
        if self.canShow:
            for handler, ctx in self.__delayedHandlers:
                handler(ctx)

            self.__delayedHandlers = []

    def canShow(self):
        prbDispatcher = self.prbDispatcher
        if prbDispatcher is None:
            return self.__isLobbyLoaded
        else:
            return self.__isLobbyLoaded and not (prbDispatcher.getFunctionalState().hasLockedState or prbDispatcher.getPlayerInfo().isReady)

    def onAvatarBecomePlayer(self):
        self.__isLobbyLoaded = False

    def onLobbyInited(self, *args):
        self.startGlobalListening()
        self.__isLobbyLoaded = True
        self.handlePostponed()

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        self.handlePostponed()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.handlePostponed()

    def onDequeued(self):
        self.handlePostponed()


class AwardHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, awardCtrl):
        self._awardCtrl = weakref.proxy(awardCtrl)

    def init(self):
        pass

    def fini(self):
        pass

    def handle(self, *args):
        if self._needToShowAward(args):
            self._awardCtrl.postponeOrCall(self._showAward, args)

    @abstractmethod
    def _needToShowAward(self, ctx):
        pass

    @abstractmethod
    def _showAward(self, ctx):
        pass


class ServiceChannelHandler(AwardHandler):

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
        for dataForVehicle in message.data.values():
            arenaTypeID = dataForVehicle.get('arenaTypeID', 0)
            arenaType = ArenaType.g_cache[arenaTypeID] if arenaTypeID > 0 else None
            arenaCreateTime = dataForVehicle.get('arenaCreateTime', None)
            fairplayViolations = dataForVehicle.get('fairplayViolations', None)
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
            self._awardCtrl._proxy.refSystem.showTankmanAwardWindow(Tankman(tmanCompDescr), completedQuestIDs)

        for vehTypeCompDescr in message.data.get('vehicles') or {}:
            self._awardCtrl._proxy.refSystem.showVehicleAwardWindow(Vehicle(typeCompDescr=abs(vehTypeCompDescr)), completedQuestIDs)

        self._awardCtrl._proxy.refSystem.showCreditsAwardWindow(message.data.get('credits', 0), completedQuestIDs)


class FortResultsWindowHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(FortResultsWindowHandler, self).__init__(SYS_MESSAGE_TYPE.fortBattleEnd.index(), awardCtrl)

    def _showAward(self, ctx):
        battleResult = ctx[1].data
        if battleResult and battleResult['isWinner'] == 0:
            if battleResult['attackResult'] == FORT_ATTACK_RESULT.TECHNICAL_DRAW:
                battleResult['isWinner'] = -1
        g_eventBus.handleEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_BATTLE_RESULTS_WINDOW_ALIAS, ctx={'data': battleResult}), scope=EVENT_BUS_SCOPE.LOBBY)


class PersonalDiscountHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PersonalDiscountHandler, self).__init__(SYS_MESSAGE_TYPE.premiumPersonalDiscount.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        if data:
            newGoodies = data.get('newGoodies', [])
            if len(newGoodies) > 0:
                discountID = findFirst(None, newGoodies)
                shopDiscounts = g_itemsCache.items.shop.premiumPacketsDiscounts
                discount = shopDiscounts.get(discountID, None)
                if discount is not None and discount.targetID == GOODIE_TARGET_TYPE.ON_BUY_PREMIUM:
                    packet = discount.getTargetValue()
                    discountPrc = getPremiumCostActionPrc(shopDiscounts, packet, g_itemsCache.items)
                    shared_events.showPremiumDiscountAward(discount.condition[1], packet, discountPrc)
        return


class PotapovQuestsBonusHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PotapovQuestsBonusHandler, self).__init__(SYS_MESSAGE_TYPE.potapovQuestBonus.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        completedQuestIDs = set(data.get('completedQuestIDs', set()))
        achievements = []
        tokens = {}
        for recordIdx, value in data.get('popUpRecords') or {}:
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

    @staticmethod
    def __tryToShowTokenAward(tID, tCount, completedQuestIDs):
        for q in g_eventsCache.getQuestsByTokenBonus(tID):
            if q.getType() == EVENT_TYPE.POTAPOV_QUEST:
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
        for vehTypeCompDescr, battleResult in ctx[1].data.iteritems():
            for recordIdx, value in battleResult.get('popUpRecords') or {}:
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
        allQuests = g_eventsCache.getAllQuests(includePotapovQuests=True)
        needToShowVehAwardWindow = False
        for qID in data.get('completedQuestIDs', set()):
            if qID in allQuests:
                for tokenID, children in allQuests[qID].getChildren().iteritems():
                    for chID in children:
                        chQuest = allQuests[chID]
                        if chQuest.getType() == EVENT_TYPE.POTAPOV_QUEST:
                            needToShowVehAwardWindow = True
                            break

        if needToShowVehAwardWindow:
            for vehTypeCompDescr in data.get('vehicles') or {}:
                quests_events.showVehicleAward(Vehicle(typeCompDescr=abs(vehTypeCompDescr)))


class QuestBoosterAwardHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(QuestBoosterAwardHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        goodies = data.get('goodies', {})
        for boosterID in goodies:
            booster = g_goodiesCache.getBooster(boosterID)
            if booster is not None:
                shared_events.showBoosterAward(booster)

        return


class BoosterAfterBattleAwardHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(BoosterAfterBattleAwardHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        battleResult = ctx[1].data
        battleResult = next(battleResult.itervalues())
        goodies = battleResult.get('goodies', {})
        for boosterID in goodies:
            booster = g_goodiesCache.getBooster(boosterID)
            if booster is not None:
                shared_events.showBoosterAward(booster)

        return


class PotapovQuestsAutoWindowHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PotapovQuestsAutoWindowHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        pqCompletedQuests = {}
        for vehTypeCompDescr, battleResult in ctx[1].data.iteritems():
            completedQuestIDs = battleResult.get('completedQuestIDs', set())
            for qID in completedQuestIDs:
                if potapov_quests.g_cache.isPotapovQuest(qID):
                    pqType = potapov_quests.g_cache.questByUniqueQuestID(qID)
                    if pqType.id not in pqCompletedQuests and not pqType.isFinal:
                        pqCompletedQuests[pqType.id] = (pqType.mainQuestID in completedQuestIDs, pqType.addQuestID in completedQuestIDs)

        for potapovQuestID, (isMain, isAdd) in pqCompletedQuests.iteritems():
            quests_events.showRegularAward(g_eventsCache.potapov.getQuests()[potapovQuestID], isMain, isAdd)


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
            getattr(self._awardCtrl._proxy.refSystem, methodName)(**ctx)
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
            else:
                LOG_ERROR('Context item is invalid', item)
                result[key] = str(item)

        return result


class SpecialAchievement(AwardHandler):

    def __init__(self, key, awardCtrl, awardCountToMessage):
        super(SpecialAchievement, self).__init__(awardCtrl)
        self.__key = key
        self.__awardCntToMsg = awardCountToMessage

    def isChanged(self, value):
        return value != AccountSettings.getFilter(AWARDS).get(self.__key)

    def getAchievementCount(self):
        raise NotImplementedError

    def showAwardWindow(self, achievementCount, messageNumber):
        raise NotImplementedError

    def _needToShowAward(self, ctx = None):
        return self._awardCtrl.canShow() == False or self._getAchievementToShow() != None

    def _getAchievementToShow(self):
        achievementCount = self.getAchievementCount()
        lastElement = max(self.__awardCntToMsg.keys())
        if achievementCount != 0 and self.isChanged(achievementCount):
            if achievementCount in self.__awardCntToMsg or achievementCount % lastElement == 0:
                return achievementCount
            sortedKeys = sorted(self.__awardCntToMsg.keys(), reverse=True)
            for i in xrange(len(sortedKeys) - 1):
                if sortedKeys[i] > achievementCount and achievementCount > sortedKeys[i + 1] and self.isChanged(sortedKeys[i + 1]):
                    return sortedKeys[i + 1]

        return None

    def _showAward(self, ctx = None):
        achievementCount = self._getAchievementToShow()
        if achievementCount is not None:
            messageNumber = self.__awardCntToMsg.get(achievementCount, self.__awardCntToMsg[max(self.__awardCntToMsg.keys())])
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
        return len(g_itemsCache.items.getVehicles(criteria=REQ_CRITERIA.UNLOCKED | ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.VEHICLE.PREMIUM | ~REQ_CRITERIA.VEHICLE.LEVELS([1]) | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR))

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
        return g_itemsCache.items.getAccountDossier().getTotalStats().getWinsCount()

    def showAwardWindow(self, achievementCount, messageNumber):
        return shared_events.showVictoryAward(achievementCount, messageNumber)


class BattlesCountHandler(SpecialAchievement):
    BATTLE_AMOUNT = {10: 1,
     50: 2,
     100: 3,
     250: 4,
     500: 1,
     1000: 2,
     2000: 3,
     5000: 4,
     7500: 1,
     10000: 2}

    def __init__(self, awardCtrl):
        super(BattlesCountHandler, self).__init__('battlesCountAward', awardCtrl, BattlesCountHandler.BATTLE_AMOUNT)

    def init(self):
        g_playerEvents.onGuiCacheSyncCompleted += self.handle
        g_playerEvents.onDossiersResync += self.handle
        g_playerEvents.onBattleResultsReceived += self.handle

    def fini(self):
        g_playerEvents.onGuiCacheSyncCompleted -= self.handle
        g_playerEvents.onDossiersResync -= self.handle
        g_playerEvents.onBattleResultsReceived -= self.handle

    def getAchievementCount(self):
        return g_itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()

    def showAwardWindow(self, achievementCount, messageNumber):
        return shared_events.showBattleAward(achievementCount, messageNumber)


class GoldFishHandler(AwardHandler):

    def __init__(self, awardCtrl):
        super(GoldFishHandler, self).__init__(awardCtrl)

    def init(self):
        self.handle()

    def _needToShowAward(self, ctx):
        return True

    def _showAward(self, ctx):
        if isGoldFishActionActive() and isTimeToShowGoldFishPromo():
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.GOLD_FISH_WINDOW))
