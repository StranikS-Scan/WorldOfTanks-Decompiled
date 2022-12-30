# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/AwardController.py
import logging
import types
import weakref
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from functools import partial
from itertools import chain, ifilter
import typing
import BigWorld
from shared_utils import first
import ArenaType
import wg_async
import gui.awards.event_dispatcher as award_events
import personal_missions
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AWARDS, AccountSettings, RANKED_CURRENT_AWARDS_BUBBLE_YEAR_REACHED, RANKED_YEAR_POSITION, SPEAKERS_DEVICE
from account_helpers.settings_core.settings_constants import SOUND
from adisp import adisp_process
from battle_pass_common import BattlePassRewardReason, get3DStyleProgressToken
from chat_shared import SYS_MESSAGE_TYPE
from collector_vehicle import CollectorVehicleConsts
from comp7_common import Comp7QuestType
from constants import DOSSIER_TYPE, EVENT_TYPE, INVOICE_ASSET, PREMIUM_TYPE
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.achievements import BADGES_BLOCK
from dossiers2.ui.layouts import PERSONAL_MISSIONS_GROUP
from gui import DialogsInterface, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.DialogsInterface import showPunishmentDialog
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.managers.view_lifecycle_watcher import IViewLifecycleHandler, ViewLifecycleWatcher
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.awards.event_dispatcher import showDynamicAward
from gui.battle_pass.battle_pass_constants import MIN_LEVEL
from gui.battle_pass.battle_pass_helpers import getStyleInfoForChapter
from gui.battle_pass.state_machine.state_machine_helpers import packStartEvent, packToken
from gui.customization.shared import checkIsFirstProgressionDecalOnVehicle
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardBonuses
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.awards.items_collection_provider import MultipleAwardRewardsMainPacker
from gui.impl.lobby.mapbox.map_box_awards_view import MapBoxAwardsViewWindow
from gui.impl.lobby.comp7.comp7_quest_helpers import isComp7Quest, getComp7QuestType, parseComp7RanksQuestID, parseComp7WinsQuestID
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX
from gui.server_events import awards, events_dispatcher as quests_events, recruit_helper
from gui.server_events.bonuses import getServiceBonuses, getMergedBonusesFromDicts
from gui.server_events.events_dispatcher import showCurrencyReserveAwardWindow, showLootboxesAward, showMissionsBattlePass, showPiggyBankRewardWindow, showSubscriptionAwardWindow
from gui.server_events.events_helpers import isACEmailConfirmationQuest, isDailyQuest
from gui.server_events.finders import CHAMPION_BADGES_BY_BRANCH, CHAMPION_BADGE_AT_OPERATION_ID, PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID, getBranchByOperationId
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showBadgeInvoiceAwardWindow, showBattlePassAwardsWindow, showBattlePassVehicleAwardWindow, showDedicationRewardWindow, showEliteWindow, showMultiAwardWindow, showProgressionRequiredStyleUnlockedWindow, showProgressiveItemsRewardWindow, showProgressiveRewardAwardWindow, showRankedSeasonCompleteView, showRankedSelectableReward, showRankedYearAwardWindow, showRankedYearLBAwardWindow, showSeniorityRewardAwardWindow, showResourceWellAwardWindow
from gui.shared.events import PersonalMissionsEvent
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.system_factory import registerAwardControllerHandlers, collectAwardControllerHandlers
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.sounds.sound_constants import SPEAKERS_CONFIG
from helpers import dependency, i18n
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr, vehicles as vehicles_core
from items.components.crew_books_constants import CREW_BOOK_DISPLAYED_AWARDS_COUNT
from messenger.formatters.service_channel import TelecomReceivedInvoiceFormatter
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from messenger.proto.events import g_messengerEvents
from nations import NAMES
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IAwardController, IBattlePassController, IBootcampController, IMapboxController, IRankedBattlesController, ISeniorityAwardsController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.sounds import ISoundsController
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from comp7_ranks_common import Comp7Division
    from gui.platform.catalog_service.controller import _PurchaseDescriptor
    from gui.server_events.event_items import TokenQuest
_logger = logging.getLogger(__name__)

class QUEST_AWARD_POSTFIX(object):
    CREW_BOOKS = 'awardcrewbook'


_POPUP_RECORDS = 'popUpRecords'

class _NonOverlappingViewsLifecycleHandler(IViewLifecycleHandler):
    __NON_OVERLAPPING_VIEWS = (VIEW_ALIAS.LOBBY_CUSTOMIZATION,)

    def __init__(self, postponeAwardsCallback, handlePostponedCallback):
        super(_NonOverlappingViewsLifecycleHandler, self).__init__([ ViewKey(alias) for alias in self.__NON_OVERLAPPING_VIEWS ])
        self.__openedViews = set()
        self.__postponeAwardsCallback = postponeAwardsCallback
        self.__handlePostponedCallback = handlePostponedCallback

    def onViewCreated(self, view):
        self.__postponeAwardsCallback(True)
        self.__openedViews.add(view.key)

    def onViewDestroyed(self, view):
        self.__openedViews.discard(view.key)
        if not self.__openedViews:
            self.__postponeAwardsCallback(False)
            self.__handlePostponedCallback()


def _showDailyQuestEpicRewardScreen(quest, context):
    bonusesFromMissionAward = awards.EpicAward(quest, context, None).getAwards()
    if bonusesFromMissionAward:
        showProgressiveRewardAwardWindow(bonusesFromMissionAward, LootCongratsTypes.INIT_CONGRAT_TYPE_EPIC_REWARDS, 0)
    return


def _showACEmailConfirmedRewardScreen(quest, context):
    missionAwards = awards.MissionAward(quest, context, None).getAwards()
    if missionAwards:
        showProgressiveRewardAwardWindow(missionAwards, LootCongratsTypes.INIT_CONGRAT_TYPE_AC_EMAIL_CONFIRMATION, 0)
    else:
        _logger.warning('Empty mission [%s] awards.', quest.getID())
    return


def _getBlueprintActualBonus(data, quest):
    questData = data.get('detailedRewards', {}).get(quest.getID(), {})
    if 'blueprints' in questData:
        blueprintActualBonus = questData.get('blueprints', {})
        actualQuest = deepcopy(quest)
        actualQuest.getData()['bonus'].update({'blueprints': blueprintActualBonus})
        return actualQuest
    return quest


class AwardController(IAwardController, IGlobalListener):
    appLoader = dependency.descriptor(IAppLoader)
    bootcampController = dependency.descriptor(IBootcampController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(AwardController, self).__init__()
        self.__handlers = []
        self.__delayedHandlers = []
        self.__isLobbyLoaded = False
        self.__postpone = False
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()

    def init(self):
        handlers = collectAwardControllerHandlers()
        self.__handlers = [ handler(self) for handler in handlers ]
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
            removeIndexes = []
            self.__delayedHandlers.sort(key=lambda handle: isinstance(handle, BattlePassRewardHandler), reverse=True)
            for index, (handler, ctx) in enumerate(self.__delayedHandlers):
                _logger.debug('Calling postponed award handler: %s, %s', handler, ctx)
                handler(ctx)
                removeIndexes.append(index)

            removeIndexes.reverse()
            for index in removeIndexes:
                self.__delayedHandlers.pop(index)

    def canShow(self):
        if self.__postpone:
            return False
        else:
            popupsWindowsDisabled = isPopupsWindowsOpenDisabled() or self.bootcampController.isInBootcamp()
            prbDispatcher = self.prbDispatcher
            return self.__isLobbyLoaded and not popupsWindowsDisabled if prbDispatcher is None else self.__isLobbyLoaded and not popupsWindowsDisabled and not prbDispatcher.getFunctionalState().hasLockedState

    def onAvatarBecomePlayer(self):
        self.__isLobbyLoaded = False
        for handler in self.__handlers:
            handler.onAvatarBecomePlayer()

        self.stopGlobalListening()

    def onDisconnected(self):
        self.__isLobbyLoaded = False
        self.stopGlobalListening()
        for handler in self.__handlers:
            handler.stop()

        self.__viewLifecycleWatcher.stop()

    def onLobbyInited(self, *args):
        self.startGlobalListening()
        self.__isLobbyLoaded = True
        self.handlePostponed()
        for handler in self.__handlers:
            handler.start()

        app = self.appLoader.getApp()
        handler = _NonOverlappingViewsLifecycleHandler(postponeAwardsCallback=self.__postponeAwards, handlePostponedCallback=self.handlePostponed)
        self.__viewLifecycleWatcher.start(app.containerManager, [handler])

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        self.handlePostponed()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.handlePostponed()

    def onDequeued(self, queueType, *args):
        self.handlePostponed()

    def __postponeAwards(self, value):
        self.__postpone = value


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

    def onAvatarBecomePlayer(self):
        pass

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
        if BigWorld.checkUnattended():
            return
        vehTypeCompDescrs = ctx
        for vehTypeCompDescr in vehTypeCompDescrs:
            showEliteWindow(vehTypeCompDescr)


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
            banDuration = message.data['restriction'][1] if 'restriction' in message.data else None
            showPunishmentDialog(arenaType, arenaCreateTime, fairplayViolations, banDuration)
        return


class PersonalMissionBonusHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(PersonalMissionBonusHandler, self).__init__(SYS_MESSAGE_TYPE.potapovQuestBonus.index(), awardCtrl)

    def _showAward(self, ctx):
        _logger.debug('Show personal mission bonus award! %s', ctx)
        data = ctx[1].data
        achievements = []
        for recordIdx, value in data.get(_POPUP_RECORDS, []):
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
        popUpRecords = ctx[1].data.get(_POPUP_RECORDS, [])
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
    seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

    def __init__(self, awardCtrl):
        super(TokenQuestsWindowHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        completedQuests = {}
        allQuests = self.eventsCache.getAllQuests(includePersonalMissions=True)
        seniorityQuestPrefix = self.seniorityAwardCtrl.seniorityQuestPrefix
        for qID in data.get('completedQuestIDs', set()):
            if qID in allQuests:
                if self.isShowCongrats(allQuests[qID]):
                    vehiclesList = data.get('detailedRewards', {}).get(qID, {}).get('vehicles', [])
                    vehiclesDict = vehiclesList[0] if vehiclesList else {}
                    windowCtx = {'eventsCache': self.eventsCache,
                     'bonusVehicles': vehiclesDict}
                    currentQuest = allQuests[qID]
                    blueprintDict = data.get('detailedRewards', {}).get(qID, {}).get('blueprints', {})
                    currentQuest = _getBlueprintActualBonus(blueprintDict, currentQuest)
                    if not seniorityQuestPrefix or seniorityQuestPrefix not in qID:
                        completedQuests[qID] = (currentQuest, windowCtx)

        for quest, context in completedQuests.itervalues():
            if isDailyQuest(str(quest.getID())):
                _showDailyQuestEpicRewardScreen(quest, context)
            if isACEmailConfirmationQuest(quest.getID()):
                _showACEmailConfirmedRewardScreen(quest, context)
            self._showWindow(quest, context)

    @staticmethod
    def _showWindow(quest, context):
        quests_events.showMissionAward(quest, context)


class SeniorityAwardsWindowHandler(ServiceChannelHandler):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)
    seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

    def __init__(self, awardCtrl):
        super(SeniorityAwardsWindowHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)
        self.__completedQuests = None
        self.__mergedRewards = None
        self.__questsData = None
        self.__callback = None
        return

    def fini(self):
        self.__completedQuests = None
        self.eventsCache.onSyncCompleted -= self.__onEventCacheSyncCompleted
        self.seniorityAwardCtrl.onUpdated -= self.__onSAConfigReady
        super(SeniorityAwardsWindowHandler, self).fini()
        return

    def _needToShowAward(self, ctx):
        if ctx == (None,):
            return self.__update()
        _, message = ctx
        if not super(SeniorityAwardsWindowHandler, self)._needToShowAward(ctx):
            return False
        data = message.data
        seniorityQuestPrefix = self.seniorityAwardCtrl.seniorityQuestPrefix
        if not seniorityQuestPrefix:
            self.seniorityAwardCtrl.onUpdated += self.__onSAConfigReady
            return False
        completedQuests = tuple((qID for qID in data.get('completedQuestIDs', set()) if qID.startswith(seniorityQuestPrefix)))
        if completedQuests:
            self.__completedQuests = completedQuests
            self.__questsData = data
            return self.__update()
        else:
            return False

    def _showAward(self, ctx=None):
        if self.__mergedRewards:
            self.seniorityAwardCtrl.markRewardReceived()
            showSeniorityRewardAwardWindow(self.__completedQuests, self.__mergedRewards)
            self.__mergedRewards = None
            self.__questsData = None
            self.__completedQuests = None
        return

    def __update(self):
        if self.__questsData:
            allQuests = self.eventsCache.getAllQuests()
            detailedRewards = self.__questsData.get('detailedRewards', {})
            rewards = list((detailedRewards.get(qID, {}) for qID in self.__completedQuests if self.isShowCongrats(allQuests.get(qID))))
            if rewards:
                self.__mergedRewards = getMergedBonusesFromDicts(rewards)
                return True
            self.eventsCache.onSyncCompleted += self.__onEventCacheSyncCompleted
        return False

    def __onSAConfigReady(self):
        self.seniorityAwardCtrl.onUpdated -= self.__onSAConfigReady
        if self.seniorityAwardCtrl.seniorityQuestPrefix:
            self.handle(None)
        return

    def __onEventCacheSyncCompleted(self, *_):
        self.eventsCache.onSyncCompleted -= self.__onEventCacheSyncCompleted
        allQuests = self.eventsCache.getAllQuests()
        if self.__completedQuests and all((qID in allQuests for qID in self.__completedQuests)):
            self.handle(None)
        return


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
            creditsEarned = data.get('credits', 0)
            goldEarned = data.get('gold', 0)
            if creditsEarned or goldEarned:
                self._showWindow(creditsEarned, goldEarned, self.__isPremiumEnable())

    @staticmethod
    def _showWindow(creditsEarned, goldEarned, isPremium):
        showNewWindow = PiggyBankOpenHandler._canShowWotPlusWindow(goldEarned)
        if not showNewWindow and goldEarned:
            _logger.info('There is hidden gold in piggy bank award screen.')
        if showNewWindow:
            showCurrencyReserveAwardWindow(creditsEarned, goldEarned)
        else:
            showPiggyBankRewardWindow(creditsEarned, isPremium)

    @staticmethod
    def _canShowWotPlusWindow(goldEarned):
        lobbyContext = dependency.instance(ILobbyContext)
        isWotPlusEnabled = lobbyContext.getServerSettings().isRenewableSubEnabled()
        isWotPlusNSEnabled = lobbyContext.getServerSettings().isWotPlusNewSubscriptionEnabled()
        hasWotPlusActive = BigWorld.player().renewableSubscription.isEnabled()
        return isWotPlusEnabled and (hasWotPlusActive or isWotPlusNSEnabled or goldEarned)

    def __isPremiumEnable(self):
        return self.itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)


class RenewableSubscriptionHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(RenewableSubscriptionHandler, self).__init__(SYS_MESSAGE_TYPE.wotPlusUnlocked.index(), awardCtrl)

    def _showAward(self, ctx):
        showSubscriptionAwardWindow()


class MarkByInvoiceHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(MarkByInvoiceHandler, self).__init__(SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl)

    def _showAward(self, ctx):
        invoiceData = ctx[1].data
        totalCount = 0
        if invoiceData.get('assetType') == INVOICE_ASSET.DATA:
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

    def _showAward(self, ctx):
        _, message = ctx
        tokenCount = self.__extractCount(message)
        if tokenCount > 0:
            self.__showMessage(tokenCount)

    def __showMessage(self, tokenCount):
        SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.TOKENS_NOTIFICATION_MARK_ACQUIRED, count=tokenCount, type=SystemMessages.SM_TYPE.tokenWithMarkAcquired)

    @staticmethod
    def __extractCount(message):
        totalCounts = 0
        tokensDict = message.data.get('tokens', {})
        for tokenName, tokenData in tokensDict.iteritems():
            if tokenName.startswith('img:'):
                totalCounts += tokenData.get('count', 0)

        return totalCounts


class CrewBooksQuestHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(CrewBooksQuestHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index()), awardCtrl)
        self._qId = None
        return

    def _needToShowAward(self, ctx):

        def isCrewBook(intCD):
            itemTypeID, _, _ = vehicles_core.parseIntCompactDescr(intCD)
            return itemTypeID == ITEM_TYPE_INDICES['crewBook']

        _, message = ctx
        res = super(CrewBooksQuestHandler, self)._needToShowAward(ctx)
        if res:
            questIDs = message.data.get('completedQuestIDs', set())
            res = res and 'items' in message.data
            res = res and any((isCrewBook(intCD) for intCD in message.data['items'].iterkeys()))
            self._qId = next(ifilter(lambda x: x.endswith(QUEST_AWARD_POSTFIX.CREW_BOOKS), questIDs), None)
            res = res and self._qId is not None
        return res

    def _showAward(self, ctx):
        _, message = ctx
        questData = message.data.get('detailedRewards', {}).get(self._qId, {})
        bonuses, _ = getProgressiveRewardBonuses(questData, maxAwardCount=CREW_BOOK_DISPLAYED_AWARDS_COUNT)
        if bonuses:
            showProgressiveRewardAwardWindow(bonuses, LootCongratsTypes.INIT_CONGRAT_TYPE_CREW_BOOKS, 0)
        else:
            _logger.error("Can't show empty or invalid reward!")


class RecruitHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(RecruitHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)
        self.__questTypes = [SYS_MESSAGE_TYPE.battleResults.index(),
         SYS_MESSAGE_TYPE.tokenQuests.index(),
         SYS_MESSAGE_TYPE.invoiceReceived.index(),
         SYS_MESSAGE_TYPE.converter.index()]

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
                self._showWindow(recruitInfo.getEventName())
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
        pass


class BoosterAfterBattleAwardHandler(ServiceChannelHandler):
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self, awardCtrl):
        super(BoosterAfterBattleAwardHandler, self).__init__(SYS_MESSAGE_TYPE.battleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        pass


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
                    vehiclesList = message.data.get('detailedRewards', {}).get(questID, {}).get('vehicles', [])
                    vehiclesDict = vehiclesList[0] if vehiclesList else {}
                    ctx.update({'eventsCache': self.eventsCache,
                     'bonusVehicles': vehiclesDict})
                    blueprintDict = message.data.get('detailedRewards', {}).get(questID, {}).get('blueprints', {})
                    quest = _getBlueprintActualBonus(blueprintDict, quest)
                    completedQuests[questID] = (quest, ctx)

        values = sorted(completedQuests.values(), key=lambda v: v[0].getID())
        for quest, context in values:
            if isDailyQuest(str(quest.getID())):
                _showDailyQuestEpicRewardScreen(quest, context)
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
                for operationID, prefix in PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID.iteritems():
                    if uniqueQuestID in self.__CHAMPION_BADGES_IDS:
                        return True
                    if uniqueQuestID.startswith(prefix):
                        if operationID in CHAMPION_BADGE_AT_OPERATION_ID:
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
        for operationId, prefix in PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID.iteritems():
            quests = []
            for uniqueQuestID in completedQuestIDs:
                if (uniqueQuestID.startswith(prefix) or self.__isChampionBadgeQuest(uniqueQuestID, operationId)) and uniqueQuestID in allQuests:
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

    @staticmethod
    def __isChampionBadgeQuest(qID, operationID):
        return False if operationID not in CHAMPION_BADGE_AT_OPERATION_ID else qID == CHAMPION_BADGE_AT_OPERATION_ID[operationID]

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
        self.__unlocks = set()
        self.__achievementCounts = 0

    def init(self):
        g_clientUpdateManager.addCallbacks({'stats.unlocks': self.onUnlocksChanged})

    def fini(self):
        self.__unlocks.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def getAchievementCount(self):
        self.__achievementCounts = len(self.itemsCache.items.getVehicles(criteria=REQ_CRITERIA.UNLOCKED | ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.VEHICLE.PREMIUM | ~REQ_CRITERIA.VEHICLE.LEVELS([1]) | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR | ~REQ_CRITERIA.COLLECTIBLE))
        return self.__achievementCounts

    def onUnlocksChanged(self, unlocks):
        isChanged = False
        self.__unlocks.clear()
        self.__achievementCounts = 0
        for unlock in list(unlocks):
            if getTypeOfCompactDescr(unlock) == ITEM_TYPE_INDICES['vehicle']:
                self.__unlocks.add(unlock)
                isChanged = True

        if isChanged:
            self.handle()

    def showAwardWindow(self, achievementCount, messageNumber):
        return award_events.showResearchAward(achievementCount, messageNumber)

    def _needToShowAward(self, ctx=None):
        isNeededToShow = super(VehiclesResearchHandler, self)._needToShowAward()
        if isNeededToShow:
            bcVehicles = self.bootcampController.getAwardVehicles()
            isAwardVehicles = set(bcVehicles).issubset(self.__unlocks) if bcVehicles else False
            return not isAwardVehicles and self.__achievementCounts in self._awardCntToMsg
        return False


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
        return award_events.showVictoryAward(achievementCount, messageNumber)


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
        return award_events.showBattleAward(achievementCount, messageNumber)

    def _getAwardCountToMessage(self):
        return BattlesCountHandler.BATTLE_AMOUNT


class PveBattlesCountHandler(BattlesCountHandler):

    def __init__(self, awardCtrl):
        super(PveBattlesCountHandler, self).__init__(awardCtrl, 'pveBattlesCountAward')

    def getAchievementCount(self):
        return self.itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()

    def showAwardWindow(self, achievementCount, messageNumber):
        return award_events.showPveBattleAward(achievementCount, messageNumber)

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
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.GOLD_FISH_WINDOW)), scope=EVENT_BUS_SCOPE.LOBBY)


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
            award_events.showTelecomAward(vehicleDesrs, data['bundleID'], hasCrew, hasBrotherhood)
        else:
            _logger.error("Can't show telecom award window!")


class RankedQuestsHandler(ServiceChannelHandler):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, awardCtrl):
        super(RankedQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        data = message.data.copy()
        seasonQuestIDs = []
        finalRewardsQuestIDs = []
        finalLeaderQuestIDs = []
        for questID in (h for h in data.get('completedQuestIDs', set()) if ranked_helpers.isRankedQuestID(h)):
            if ranked_helpers.isSeasonTokenQuest(questID):
                seasonQuestIDs.append(questID)
            if ranked_helpers.isFinalTokenQuest(questID):
                finalRewardsQuestIDs.append(questID)
            if ranked_helpers.isLeaderTokenQuest(questID):
                finalLeaderQuestIDs.append(questID)

        if seasonQuestIDs:
            self.__processQuests(seasonQuestIDs, data, self.__showSeasonAward)
        if finalRewardsQuestIDs:
            self.__showFinalAward(finalRewardsQuestIDs, data)
        if finalLeaderQuestIDs:
            self.__processQuests(finalLeaderQuestIDs, data, self.__showFinalLeaderAward)

    def __showSeasonAward(self, quest, data):
        seasonID, league, _ = ranked_helpers.getDataFromSeasonTokenQuestID(quest.getID())
        season = self.__rankedController.getSeason(seasonID)
        if season is not None:
            showRankedSeasonCompleteView({'quest': quest,
             'awards': data}, True)
        else:
            _logger.error('Try to show RankedBattlesSeasonCompleteView, but season is None. Params: %s %s', seasonID, league)
        return

    def __showFinalAward(self, questIDs, data):
        points = ranked_helpers.getDataFromFinalTokenQuestID(first(questIDs))
        awardType = self.__rankedController.getAwardTypeByPoints(points)
        if awardType is not None:
            if any((token.startswith(YEAR_AWARD_SELECTABLE_OPT_DEVICE_PREFIX) for token in data.get('tokens', {}).keys())):
                AccountSettings.setSettings(RANKED_CURRENT_AWARDS_BUBBLE_YEAR_REACHED, False)
                showRankedSelectableReward(data)
            else:
                showRankedYearAwardWindow(data, self.__rankedController.getYearRewardPoints(), True)
        return

    def __showFinalLeaderAward(self, _, data):
        yearPosition = AccountSettings.getSettings(RANKED_YEAR_POSITION)
        if yearPosition is not None and data:
            showRankedYearLBAwardWindow(yearPosition, data, True)
        return

    def __processQuests(self, questIDs, data, handler):
        questID = questIDs[0]
        quest = self.eventsCache.getHiddenQuests().get(questID)
        if quest:
            questData = data.get('detailedRewards', {}).get(questID, {})
            handler(quest, questData)
        if len(questIDs) > 1:
            _logger.error('There can not be 2 or more quests with the same meaning at the same time')


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

    def __init__(self, awardCtrl):
        super(ProgressiveRewardHandler, self).__init__(SYS_MESSAGE_TYPE.progressiveReward.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        bonuses, specialRewardType = getProgressiveRewardBonuses(message.data['rewards'])
        if bonuses:
            showProgressiveRewardAwardWindow(bonuses, specialRewardType, message.data['level'])
        else:
            _logger.error("Can't show empty or invalid reward!")


class ProgressiveItemsRewardHandler(ServiceChannelHandler):
    _gui = dependency.descriptor(IGuiLoader)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, awardCtrl):
        super(ProgressiveItemsRewardHandler, self).__init__(SYS_MESSAGE_TYPE.customizationProgress.index(), awardCtrl)
        self.__message = None
        return

    def fini(self):
        self._hangarSpace.onSpaceCreate -= self.__show
        super(ProgressiveItemsRewardHandler, self).fini()

    def _showAward(self, ctx):
        if BigWorld.checkUnattended():
            return
        _, self.__message = ctx
        if self._hangarSpace.spaceInited:
            self.__show()
        else:
            self._hangarSpace.onSpaceCreate += self.__show

    def __show(self):
        self._hangarSpace.onSpaceCreate -= self.__show
        for vehicleCD, items in self.__message.data.iteritems():
            newItemsCDs = items.keys()
            isFirst = checkIsFirstProgressionDecalOnVehicle(vehicleCD, newItemsCDs)
            for itemCD, level in items.iteritems():
                showProgressiveItemsRewardWindow(itemCD, vehicleCD, level, itemCD == newItemsCDs[-1] and not isFirst)

            if isFirst:
                showProgressionRequiredStyleUnlockedWindow(vehicleCD)


class VehicleCollectorAchievementHandler(ServiceChannelHandler):
    _PATTERN = CollectorVehicleConsts.COLLECTOR_MEDAL_PREFIX

    def __init__(self, awardCtrl):
        super(VehicleCollectorAchievementHandler, self).__init__(SYS_MESSAGE_TYPE.achievementReceived.index(), awardCtrl)
        self.__nationAwards = []
        self.__isCollectionAssembled = False

    def fini(self):
        self.__clear()
        super(VehicleCollectorAchievementHandler, self).fini()

    def _needToShowAward(self, ctx):
        isNeedToShow = super(VehicleCollectorAchievementHandler, self)._needToShowAward(ctx)
        if isNeedToShow:
            self.__setAwards(ctx)
            return self.__isAwardsReceived()
        return False

    def __setAwards(self, ctx):
        _, message = ctx
        medals = message.data.get(_POPUP_RECORDS, {})
        if not medals:
            return
        for _, medalName in medals:
            if not medalName.startswith(self._PATTERN):
                continue
            if len(medalName) == len(self._PATTERN):
                self.__isCollectionAssembled = True
            nation = int(medalName[len(self._PATTERN):])
            if self.__isNationCorrect(nation):
                self.__nationAwards.append(nation)

    def __isAwardsReceived(self):
        return len(self.__nationAwards) > 0 or self.__isCollectionAssembled

    def _showAward(self, ctx):
        self.__showNationalCollectorAward()
        self.__showVehicleCollectorOfEverythingAward()
        self.__clear()

    def __showNationalCollectorAward(self):
        if self.__nationAwards is None:
            return
        else:
            for nationID in self.__nationAwards:
                award_events.showVehicleCollectorAward(nationID)

            return

    def __showVehicleCollectorOfEverythingAward(self):
        if self.__isCollectionAssembled:
            award_events.showVehicleCollectorOfEverythingAward()

    def __clear(self):
        self.__nationAwards = []
        self.__isCollectionAssembled = False

    def __isNationCorrect(self, nationID):
        if nationID is None or nationID >= len(NAMES) or nationID < 0:
            _logger.error('Incorrect nationID=%s for the award window of the vehicle collector', nationID)
            return False
        else:
            return True


class BattlePassRewardHandler(ServiceChannelHandler):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __notificationMgr = dependency.descriptor(INotificationWindowController)

    def __init__(self, awardCtrl):
        super(BattlePassRewardHandler, self).__init__(SYS_MESSAGE_TYPE.battlePassReward.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        rewards = message.data.get('reward', {})
        data = message.data.get('ctx', {})
        if 'reason' not in data:
            _logger.error('Invalid Battle Pass Reward data received! "reward" key missing!')
            return
        elif data.get('reason') == BattlePassRewardReason.PURCHASE_BATTLE_PASS_MULTIPLE:
            return
        else:
            for key in ('newLevel', 'prevLevel', 'chapter'):
                if key not in data:
                    _logger.error('Invalid Battle Pass Reward data received! "%s" key missing!', key)
                    return

            event = packStartEvent(rewards, data, battlePass=self.__battlePassController)
            if event is not None:
                self.__notificationMgr.append(event)
            return


class BattlePassStyleRecievedHandler(ServiceChannelHandler):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, awardCtrl):
        super(BattlePassStyleRecievedHandler, self).__init__(SYS_MESSAGE_TYPE.battlePassStyleRecieved.index(), awardCtrl)
        self.__chapter = None
        return

    def fini(self):
        self.__itemsCache.onSyncCompleted -= self.__showAward
        super(BattlePassStyleRecievedHandler, self).fini()

    def _showAward(self, ctx):
        _, message = ctx
        self.__chapter = message.data.get('chapter', 0)
        _, level = getStyleInfoForChapter(self.__chapter)
        if level < 1:
            self.__itemsCache.onSyncCompleted += self.__showAward
        else:
            self.__showAward()

    def __showAward(self, *_):
        self.__itemsCache.onSyncCompleted -= self.__showAward
        _, level = getStyleInfoForChapter(self.__chapter)
        if level > 1:
            return
        data = {'chapter': self.__chapter,
         'reason': BattlePassRewardReason.STYLE_UPGRADE}
        styleToken = get3DStyleProgressToken(self.__battlePassController.getSeasonID(), self.__chapter, level)
        rewards = packToken(styleToken)
        showBattlePassAwardsWindow([rewards], data, useQueue=True)


class BattlePassBuyEmptyHandler(ServiceChannelHandler):
    __battlePassController = dependency.descriptor(IBattlePassController)
    __MULTIPLE_CHAPTER = 0

    def __init__(self, awardCtrl):
        super(BattlePassBuyEmptyHandler, self).__init__(SYS_MESSAGE_TYPE.battlePassBought.index(), awardCtrl)

    def _needToShowAward(self, ctx):
        needToShow = super(BattlePassBuyEmptyHandler, self)._needToShowAward(ctx)
        if needToShow:
            _, message = ctx
            chapterID = message.data.get('chapter')
            if chapterID is None:
                return False
            if chapterID:
                minLevel, _ = self.__battlePassController.getChapterLevelInterval(chapterID)
            else:
                minLevel = MIN_LEVEL
            return self.__battlePassController.getLevelInChapter(chapterID) < minLevel
        else:
            return False

    def _showAward(self, ctx):
        _, message = ctx
        chapterID = message.data.get('chapter')
        if chapterID is None:
            _logger.error('chapter can not be None!')
            return
        else:
            if chapterID:
                reason = BattlePassRewardReason.PURCHASE_BATTLE_PASS
            else:
                reason = BattlePassRewardReason.PURCHASE_BATTLE_PASS_MULTIPLE
            prevLevel, _ = self.__battlePassController.getChapterLevelInterval(chapterID)
            callback = partial(self.__onAwardShown, chapterID)
            data = {'prevLevel': prevLevel,
             'chapter': chapterID,
             'reason': reason,
             'callback': callback}
            showBattlePassAwardsWindow([], data, useQueue=True)
            return

    def __onAwardShown(self, chapterID):
        if self.__battlePassController.isDisabled() or chapterID is None:
            return
        else:
            showMissionsBattlePass(R.views.lobby.battle_pass.BattlePassProgressionsView() if chapterID else None, chapterID)
            return


class BattlePassCapHandler(ServiceChannelHandler):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, awardCtrl):
        super(BattlePassCapHandler, self).__init__(SYS_MESSAGE_TYPE.battlePassReachedCap.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        for key in ('vehTypeCompDescr', 'vehiclePoints', 'bonusPoints'):
            if key not in message.data:
                _logger.error('Invalid Reached Cap data!')
                return

        showBattlePassVehicleAwardWindow(message.data)


class DynamicBonusHandler(ServiceChannelHandler):
    AVAILABLE_TAGS = ['wgcq.clan_reward', 'wgcq.player_reward']

    def __init__(self, awardCtrl):
        super(DynamicBonusHandler, self).__init__(SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl)

    def _showAward(self, ctx):
        invoiceData = ctx[1].data
        if invoiceData.get('assetType') in (INVOICE_ASSET.DATA, INVOICE_ASSET.PURCHASE) and 'tags' in invoiceData:
            if 'data' not in invoiceData:
                _logger.error('Invalid Reached Cap data!')
            for tag in invoiceData['tags']:
                if tag in self.AVAILABLE_TAGS:
                    showDynamicAward(tag.replace('.', '_'), invoiceData['data'])


class DedicationReward(ServiceChannelHandler):
    itemsCache = dependency.descriptor(IItemsCache)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, awardCtrl):
        super(DedicationReward, self).__init__(SYS_MESSAGE_TYPE.dedicationReward.index(), awardCtrl)
        self.__pending = []
        self.__locked = False

    def fini(self):
        self._hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        super(DedicationReward, self).fini()

    def _showAward(self, ctx):
        _, message = ctx
        rewards = message.data.get('rewards', {})
        data = message.data.get('ctx', {})
        self.__processOrHold(([rewards], data))

    def __onSpaceCreated(self):
        self.__unlock()

    def _showDedicationReward(self, rewards, data):
        showDedicationRewardWindow(rewards, data, closeCallback=self.__unlock)

    def __processOrHold(self, args):
        if self.__locked or not self._hangarSpace.spaceInited:
            self._hangarSpace.onSpaceCreate += self.__onSpaceCreated
            self.__pending.append(args)
        else:
            self.__locked = True
            self._showDedicationReward(*args)

    def __unlock(self):
        self.__locked = False
        if self.__pending:
            self.__processOrHold(self.__pending.pop(0))


class BadgesInvoiceHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(BadgesInvoiceHandler, self).__init__(channelType=SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl=awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        invoiceData = message.data.get('data', {})
        changes = invoiceData.get('dossier', {}).get(DOSSIER_TYPE.ACCOUNT, {})
        it = changes.iteritems() if isinstance(changes, dict) else changes
        for (blockName, recordName), paramsDict in it:
            if blockName == BADGES_BLOCK:
                if paramsDict['value'] > 0:
                    badgeId = int(recordName)
                    badge = self.itemsCache.items.getBadgeByID(badgeId)
                    if badge is None:
                        _logger.error('Unknown Badge. id=%s', badgeId)
                    elif badge.showCongratsView:
                        self._showWindow(badge)

        return

    @staticmethod
    def _showWindow(badge):
        showBadgeInvoiceAwardWindow(badge)


class MapboxProgressionRewardHandler(AwardHandler):
    __notificationMgr = dependency.descriptor(INotificationWindowController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def init(self):
        g_messengerEvents.serviceChannel.onClientMessageReceived += self.handle

    def fini(self):
        g_messengerEvents.serviceChannel.onClientMessageReceived -= self.handle

    def _needToShowAward(self, args):
        _, __, settings = args
        return settings.messageSubtype == SCH_CLIENT_MSG_TYPE.MAPBOX_PROGRESSION_REWARD

    @wg_async.wg_async
    def _showAward(self, ctx):
        _, message, __ = ctx
        bonuses = chain.from_iterable([ getServiceBonuses(name, value) for name, value in message['savedData'].get('rewards', {}).iteritems() ])
        window = MapBoxAwardsViewWindow(message['savedData']['battles'], bonuses)
        self.__notificationMgr.append(WindowNotificationCommand(window))
        self.__eventsCache.onEventsVisited()
        yield wg_async.wg_await(self.__mapboxCtrl.forceUpdateProgressData())


class PurchaseHandler(ServiceChannelHandler):
    __purchaseCache = dependency.descriptor(IPurchaseCache)

    def __init__(self, awardCtrl):
        super(PurchaseHandler, self).__init__(SYS_MESSAGE_TYPE.invoiceReceived.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        invoiceData = message.data
        if invoiceData.get('assetType', 0) == INVOICE_ASSET.PURCHASE:
            if self.__purchaseCache.canBeRequestedFromProduct(invoiceData):
                if 'data' not in invoiceData:
                    _logger.error('Invalid purchase invoice data!')
                    return
                self.__tryToShowAwards(invoiceData)
            else:
                _logger.debug('Data can not be requested from the product! Award window will not be shown!')

    @adisp_process
    def __tryToShowAwards(self, invoiceData):
        yield lambda callback: callback(True)
        metaData = invoiceData.get('meta', {})
        if metaData.get('type') == 'normal':
            productCode = self.__purchaseCache.getProductCode(metaData)
            if productCode:
                pD = yield self.__purchaseCache.requestPurchaseByID(productCode)
                if pD.getDisplayWays().showAwardScreen:
                    rewards, tTips = yield MultipleAwardRewardsMainPacker().getWholeBonusesData(invoiceData, productCode)
                    if rewards:
                        showMultiAwardWindow(rewards, tTips, productCode)
                    else:
                        _logger.info('Reward list is empty, multiple awards window will not be shown for purchase %s', productCode)
            else:
                _logger.debug('Product code is empty! Awards Window will not be shown!')


class BattleMattersQuestsHandler(MultiTypeServiceChannelHandler):
    __battleMattersCtrl = dependency.descriptor(IBattleMattersController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, awardCtrl):
        super(BattleMattersQuestsHandler, self).__init__((SYS_MESSAGE_TYPE.hangarQuests.index(), SYS_MESSAGE_TYPE.tokenQuests.index(), SYS_MESSAGE_TYPE.battleResults.index()), awardCtrl)

    def _showAward(self, ctx, clientCtx=None):
        _, message = ctx
        if message.type == SYS_MESSAGE_TYPE.battleResults.index():
            self.__systemMessages.proto.serviceChannel.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.BATTLE_MATTERS_BATTLE_AWARD)
        self.__battleMattersCtrl.showAwardView(message.data)

    def _needToShowAward(self, ctx):
        _, message = ctx
        if not super(BattleMattersQuestsHandler, self)._needToShowAward(ctx):
            return False
        data = message.data
        return [ qID for qID in data.get('completedQuestIDs', set()) if self.__battleMattersCtrl.isRegularBattleMattersQuestID(qID) or self.__battleMattersCtrl.isIntermediateBattleMattersQuestID(qID) ]


class ResourceWellRewardHandler(ServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(ResourceWellRewardHandler, self).__init__(SYS_MESSAGE_TYPE.resourceWellReward.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        showResourceWellAwardWindow(serialNumber=message.data.get('serialNumber', ''))


class Comp7RewardHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(Comp7RewardHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index()), awardCtrl)
        self.__completedQuestIDs = set()

    def fini(self):
        self.__completedQuestIDs.clear()
        self.eventsCache.onSyncCompleted -= self.__showAward
        super(Comp7RewardHandler, self).fini()

    def _showAward(self, ctx):
        _, message = ctx
        data = message.data
        self.__completedQuestIDs.update((qID for qID in data.get('completedQuestIDs', set()) if isComp7Quest(qID)))
        if not self.__completedQuestIDs:
            return
        if self.eventsCache.waitForSync:
            self.eventsCache.onSyncCompleted += self.__onEventCacheSyncCompleted
        else:
            self.__showAward()

    def __showAward(self):
        ranksQuests, winsQuests, periodicQuests = self.__getComp7CompletedQuests()
        self.__completedQuestIDs.clear()
        for quest in ranksQuests:
            event_dispatcher.showComp7RanksRewardsScreen(quest=quest, periodicQuests=periodicQuests)

        for quest in winsQuests:
            event_dispatcher.showComp7WinsRewardsScreen(quest=quest)

    def __getComp7CompletedQuests(self):
        ranksQuests = []
        winsQuests = []
        periodicQuests = []
        if not self.__completedQuestIDs:
            return (ranksQuests, winsQuests, periodicQuests)
        else:
            allQuests = self.eventsCache.getAllQuests(lambda q: isComp7Quest(q.getID()))
            for qID in self.__completedQuestIDs:
                quest = allQuests.get(qID)
                if quest is None:
                    _logger.error('Missing Comp7 Quest qID=%s', qID)
                    continue
                qType = getComp7QuestType(qID)
                if qType == Comp7QuestType.RANKS:
                    ranksQuests.append(quest)
                if qType == Comp7QuestType.WINS:
                    winsQuests.append(quest)
                if qType == Comp7QuestType.PERIODIC:
                    periodicQuests.append(quest)

            ranksQuests.sort(key=self.__getRanksQuestSortKey)
            winsQuests.sort(key=self.__getWinsQuestSortKey)
            return (ranksQuests, winsQuests, periodicQuests)

    def __onEventCacheSyncCompleted(self, *_):
        self.eventsCache.onSyncCompleted -= self.__onEventCacheSyncCompleted
        self.__showAward()

    @staticmethod
    def __getRanksQuestSortKey(quest):
        division = parseComp7RanksQuestID(quest.getID())
        return (division.rank, division.index)

    @staticmethod
    def __getWinsQuestSortKey(quest):
        winsCount = parseComp7WinsQuestID(quest.getID())
        return winsCount


registerAwardControllerHandlers((BattleQuestsAutoWindowHandler,
 QuestBoosterAwardHandler,
 BoosterAfterBattleAwardHandler,
 PunishWindowHandler,
 TokenQuestsWindowHandler,
 MotiveQuestsWindowHandler,
 VehiclesResearchHandler,
 VictoryHandler,
 BattlesCountHandler,
 PveBattlesCountHandler,
 PersonalMissionBonusHandler,
 PersonalMissionWindowAfterBattleHandler,
 PersonalMissionAutoWindowHandler,
 PersonalMissionByAwardListHandler,
 PersonalMissionOperationAwardHandler,
 PersonalMissionOperationUnlockedHandler,
 GoldFishHandler,
 TelecomHandler,
 MarkByInvoiceHandler,
 MarkByQuestHandler,
 CrewBooksQuestHandler,
 RecruitHandler,
 SoundDeviceHandler,
 EliteWindowHandler,
 LootBoxByInvoiceHandler,
 ProgressiveRewardHandler,
 PiggyBankOpenHandler,
 SeniorityAwardsWindowHandler,
 RankedQuestsHandler,
 BattlePassRewardHandler,
 BattlePassStyleRecievedHandler,
 BattlePassBuyEmptyHandler,
 BattlePassCapHandler,
 VehicleCollectorAchievementHandler,
 DynamicBonusHandler,
 ProgressiveItemsRewardHandler,
 DedicationReward,
 BadgesInvoiceHandler,
 MapboxProgressionRewardHandler,
 PurchaseHandler,
 RenewableSubscriptionHandler,
 BattleMattersQuestsHandler,
 ResourceWellRewardHandler,
 Comp7RewardHandler))
