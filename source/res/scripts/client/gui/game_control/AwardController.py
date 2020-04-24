# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/AwardController.py
import logging
import types
import weakref
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from itertools import ifilter
import BigWorld
import ArenaType
import gui.awards.event_dispatcher as shared_events
import personal_missions
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, AWARDS, SPEAKERS_DEVICE, GUI_START_BEHAVIOR, TECHTREE_INTRO_BLUEPRINTS
from account_helpers.settings_core.settings_constants import SOUND, GuiSettingsBehavior
from account_shared import getFairPlayViolationName
from battle_pass_common import BattlePassRewardReason
from battle_pass_common import BattlePassState
from chat_shared import SYS_MESSAGE_TYPE
from collector_vehicle import CollectorVehicleConsts
from constants import EVENT_TYPE, INVOICE_ASSET, PREMIUM_TYPE
from constants import IS_DEVELOPMENT
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui.layouts import PERSONAL_MISSIONS_GROUP
from gui import DialogsInterface
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.DialogsInterface import showDialog
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18PunishmentDialogMeta
from gui.Scaleform.daapi.view.lobby.hangar.seniority_awards import getSeniorityAwardsBox
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.awards.event_dispatcher import showCrewSkinAward
from gui.gold_fish import isGoldFishActionActive, isTimeToShowGoldFishPromo
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardBonuses
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.ranked_battles import ranked_helpers
from gui.server_events import events_dispatcher as quests_events, recruit_helper, awards
from gui.server_events.events_dispatcher import showLootboxesAward, showPiggyBankRewardWindow
from gui.server_events.events_helpers import isDailyQuest
from gui.server_events.finders import PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID, getBranchByOperationId, CHAMPION_BADGES_BY_BRANCH, CHAMPION_BADGE_AT_OPERATION_ID
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from gui.shared.event_dispatcher import showProgressiveRewardAwardWindow, showBattlePassAwardsWindow, showBattlePassVehicleAwardWindow, showSeniorityRewardAwardWindow, showRankedYeardAwardWindow
from gui.shared.events import PersonalMissionsEvent, LobbySimpleEvent
from gui.shared.gui_items.dossier.factories import getAchievementFactory
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.functions import getViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.sounds.sound_constants import SPEAKERS_CONFIG
from helpers import dependency
from helpers import i18n
from helpers import time_utils
from items import ITEM_TYPE_INDICES, getTypeOfCompactDescr, vehicles as vehicles_core
from items.components.crew_books_constants import CREW_BOOK_DISPLAYED_AWARDS_COUNT
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import TelecomReceivedInvoiceFormatter
from messenger.proto.events import g_messengerEvents
from nations import NAMES
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IAwardController, IRankedBattlesController, IBootcampController, IBattlePassController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.sounds import ISoundsController
from ten_year_countdown_config import EVENT_BADGE_MISSION_ID
from ten_year_countdown_config import EVENT_STYLE_MISSION_ID
from ten_year_countdown_config import TEN_YEAR_COUNTDOWN_QUEST_TOKEN_PREFIX
from ten_year_countdown_config import TEN_YEAR_COUNTDOWN_QUEST_TOKEN_POSTFIX
from gui.shared.event_dispatcher import show10YCAwardWindow
from gui.impl.auxiliary.rewards_helper import getTokenAward
_logger = logging.getLogger(__name__)

class QUEST_AWARD_POSTFIX(object):
    CREW_SKINS = 'awardcrewskin'
    CREW_BOOKS = 'awardcrewbook'


SENIORITY_AWARDS_TOKEN_QUEST = 'SeniorityAwardsQuest'
_POPUP_RECORDS = 'popUpRecords'

def _showDailyQuestEpicRewardScreen(quest, context):
    bonusesFromMissionAward = awards.EpicAward(quest, context, None).getAwards()
    if bonusesFromMissionAward:
        showProgressiveRewardAwardWindow(bonusesFromMissionAward, LootCongratsTypes.INIT_CONGRAT_TYPE_EPIC_REWARDS, 0)
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
         MarkByInvoiceHandler(self),
         MarkByQuestHandler(self),
         CrewSkinsQuestHandler(self),
         CrewBooksQuestHandler(self),
         RecruitHandler(self),
         SoundDeviceHandler(self),
         EliteWindowHandler(self),
         LootBoxByInvoiceHandler(self),
         ProgressiveRewardHandler(self),
         PiggyBankOpenHandler(self),
         SeniorityAwardsWindowHandler(self),
         RankedQuestsHandler(self),
         BattlePassRewardHandler(self),
         BattlePassBuyEmptyHandler(self),
         BattlePassCapHandler(self),
         TechTreeIntroHandler(self),
         VehicleCollectorAchievementHandler(self),
         TenYearsCountdownHandler(self)]
        super(AwardController, self).__init__()
        self.__delayedHandlers = []
        self.__isLobbyLoaded = False
        self.__overlayLocks = []

    def init(self):
        g_eventBus.addListener(LobbySimpleEvent.LOCK_OVERLAY_SCREEN, self.__onLockOverlayScreen, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LobbySimpleEvent.UNLOCK_OVERLAY_SCREEN, self.__onUnlockOverlayScreen, EVENT_BUS_SCOPE.LOBBY)
        for handler in self.__handlers:
            handler.init()

    def fini(self):
        g_eventBus.removeListener(LobbySimpleEvent.LOCK_OVERLAY_SCREEN, self.__onLockOverlayScreen, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LobbySimpleEvent.UNLOCK_OVERLAY_SCREEN, self.__onUnlockOverlayScreen, EVENT_BUS_SCOPE.LOBBY)
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
            for index, (handler, ctx) in enumerate(self.__delayedHandlers):
                if self.__isLocked():
                    break
                _logger.debug('Calling postponed award handler: %s, %s', handler, ctx)
                handler(ctx)
                removeIndexes.append(index)

            removeIndexes.reverse()
            for index in removeIndexes:
                self.__delayedHandlers.pop(index)

    def canShow(self):
        if self.__isLocked():
            return False
        else:
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

    def __onLockOverlayScreen(self, event):
        source = event.ctx.get('source')
        if source and source not in self.__overlayLocks:
            self.__overlayLocks.append(source)

    def __onUnlockOverlayScreen(self, event):
        source = event.ctx.get('source')
        if source and source in self.__overlayLocks:
            self.__overlayLocks.remove(source)
        if not self.__overlayLocks:
            self.handlePostponed()

    def __isLocked(self):
        return len(self.__overlayLocks) > 0


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

    def __init__(self, awardCtrl):
        super(TokenQuestsWindowHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        completedQuests = {}
        allQuests = self.eventsCache.getAllQuests(includePersonalMissions=True)
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
                    if SENIORITY_AWARDS_TOKEN_QUEST not in qID:
                        completedQuests[qID] = (currentQuest, windowCtx)

        for quest, context in completedQuests.itervalues():
            if isDailyQuest(str(quest.getID())):
                _showDailyQuestEpicRewardScreen(quest, context)
            self._showWindow(quest, context)

    @staticmethod
    def _showWindow(quest, context):
        quests_events.showMissionAward(quest, context)


class SeniorityAwardsWindowHandler(ServiceChannelHandler):
    itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, awardCtrl):
        super(SeniorityAwardsWindowHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)
        self._qID = None
        self.__mergedRewards = {}
        self.__questData = None
        self.__autoOpenData = None
        self.__callback = None
        return

    def fini(self):
        self.__resetCallback()
        self._qID = None
        self.itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
        self.eventsCache.onSyncCompleted -= self.__onEventCacheSyncCompleted
        super(SeniorityAwardsWindowHandler, self).fini()
        return

    def _needToShowAward(self, ctx):
        _, message = ctx
        isLootBoxesAutoOpenType = SYS_MESSAGE_TYPE.lootBoxesAutoOpenReward.index() == message.type
        if not isLootBoxesAutoOpenType and not super(SeniorityAwardsWindowHandler, self)._needToShowAward(ctx):
            return False
        data = message.data
        if isLootBoxesAutoOpenType:
            self.__autoOpenData = data
            self.__callback = BigWorld.callback(time_utils.ONE_MINUTE, self.__onShowAutoOpenRewards)
            self.__update()
        else:
            for qID in data.get('completedQuestIDs', set()):
                if SENIORITY_AWARDS_TOKEN_QUEST in qID:
                    self._qID = qID
                    self.__questData = data
                    self.__update()

        return False

    def _showAward(self, ctx=None):
        self.__resetCallback()
        if self.__mergedRewards:
            showSeniorityRewardAwardWindow(self._qID, self.__mergedRewards)
            self.__mergedRewards = {}
            self.__autoOpenData = None
            self.__questData = None
        return

    def __update(self, isCallback=False):
        if self.__questData and self.__autoOpenData:
            if self.__isValidAutoOpenBoxData():
                self.__mergedRewards.update(self.__autoOpenData.get('rewards', {}))
            else:
                self.itemsCache.onSyncCompleted += self.__onItemCacheSyncCompleted
                return
            if isCallback:
                self._showAward()
                return
            allQuests = self.eventsCache.getAllQuests()
            if self._qID in allQuests and self.isShowCongrats(allQuests[self._qID]):
                self.__mergedRewards.update(self.__questData.get('detailedRewards', {}).get(self._qID, {}))
            else:
                self.eventsCache.onSyncCompleted += self.__onEventCacheSyncCompleted
                return
            self.itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
            self.eventsCache.onSyncCompleted -= self.__onEventCacheSyncCompleted
            self._showAward()

    def __resetCallback(self):
        if self.__callback:
            BigWorld.cancelCallback(self.__callback)
            self.__callback = None
        return

    def __onShowAutoOpenRewards(self):
        self.__callback = None
        self.__update(True)
        return

    def __onItemCacheSyncCompleted(self, *_):
        self.itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
        self.__update()

    def __onEventCacheSyncCompleted(self, *_):
        self.eventsCache.onSyncCompleted -= self.__onEventCacheSyncCompleted
        allQuests = self.eventsCache.getAllQuests()
        if self._qID in allQuests:
            self.__update()

    def __isValidAutoOpenBoxData(self):
        boxIDs = self.__autoOpenData.get('boxIDs', {})
        box = getSeniorityAwardsBox()
        return True if boxIDs and box and box.getID() in boxIDs else False


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


class CrewSkinsQuestHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(CrewSkinsQuestHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index()), awardCtrl)

    def _needToShowAward(self, ctx):
        _, message = ctx
        res = super(CrewSkinsQuestHandler, self)._needToShowAward(ctx)
        if res:
            questIDs = message.data.get('completedQuestIDs', set())
            res = res and 'crewSkins' in message.data
            res = res and next(ifilter(lambda x: x.endswith(QUEST_AWARD_POSTFIX.CREW_SKINS), questIDs), None) is not None
        return res

    def _showAward(self, ctx):
        showCrewSkinAward()


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

    def init(self):
        g_clientUpdateManager.addCallbacks({'stats.unlocks': self.onUnlocksChanged})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def getAchievementCount(self):
        return len(self.itemsCache.items.getVehicles(criteria=REQ_CRITERIA.UNLOCKED | ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.VEHICLE.PREMIUM | ~REQ_CRITERIA.VEHICLE.LEVELS([1]) | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR | ~REQ_CRITERIA.COLLECTIBLE))

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


class RankedQuestsHandler(ServiceChannelHandler):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, awardCtrl):
        super(RankedQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)
        self.__pending = []
        self.__locked = False

    def _showAward(self, ctx):
        _, message = ctx
        data = message.data.copy()
        seasonQuestIDs = []
        finalRewardsQuestIDs = []
        for questID in (h for h in data.get('completedQuestIDs', set()) if ranked_helpers.isRankedQuestID(h)):
            if ranked_helpers.isSeasonTokenQuest(questID):
                seasonQuestIDs.append(questID)
            if ranked_helpers.isFinalTokenQuest(questID):
                finalRewardsQuestIDs.append(questID)

        if seasonQuestIDs:
            self.__processQuests(seasonQuestIDs, data, self.__showSeasonAward)
        if finalRewardsQuestIDs:
            self.__processQuests(finalRewardsQuestIDs, data, self.__showFinalAward)

    def __processQuests(self, questIDs, data, handler):
        questID = questIDs[0]
        quest = self.eventsCache.getHiddenQuests().get(questID)
        if quest:
            questData = data.get('detailedRewards', {}).get(questID, {})
            self.__processOrHold(handler, (quest, questData))
        if len(questIDs) > 1:
            _logger.error('%s has collision with other quest. There can not be 2 or more same quests at the same time', questID)

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
        seasonID, _, _ = ranked_helpers.getDataFromSeasonTokenQuestID(quest.getID())
        season = self.__rankedController.getSeason(seasonID)
        if season is not None:
            g_eventBus.handleEvent(events.LoadViewEvent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, ctx={'quest': quest,
             'awards': data,
             'closeClb': self.__unlock}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.__unlock()
        return

    def __showFinalAward(self, quest, data):
        points = ranked_helpers.getDataFromFinalTokenQuestID(quest.getID())
        awardType = self.__rankedController.getAwardTypeByPoints(points)
        if awardType is not None:
            showRankedYeardAwardWindow(data, points, closeCallback=self.__unlock)
        else:
            self.__unlock()
        return


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


class TechTreeIntroHandler(ServiceChannelHandler):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, awardCtrl):
        super(TechTreeIntroHandler, self).__init__(SYS_MESSAGE_TYPE.converter.index(), awardCtrl)

    def _needToShowAward(self, ctx):
        if not super(TechTreeIntroHandler, self)._needToShowAward(ctx):
            return False
        settings = self.__getSettings()
        if not settings[GuiSettingsBehavior.TECHTREE_INTRO_BLUEPRINTS_RECEIVED]:
            _, message = ctx
            data = message.data or {}
            blueprints = data.get('blueprints', {})
            if blueprints:
                AccountSettings.setSettings(TECHTREE_INTRO_BLUEPRINTS, blueprints)
                settings[GuiSettingsBehavior.TECHTREE_INTRO_BLUEPRINTS_RECEIVED] = True
                self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)
        return False

    def _showAward(self, ctx):
        pass

    def __getSettings(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)


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
                shared_events.showVehicleCollectorAward(nationID)

            return

    def __showVehicleCollectorOfEverythingAward(self):
        if self.__isCollectionAssembled:
            shared_events.showVehicleCollectorOfEverythingAward()

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

    def __init__(self, awardCtrl):
        super(BattlePassRewardHandler, self).__init__(SYS_MESSAGE_TYPE.battlePassReward.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        rewards = message.data.get('reward', {})
        data = message.data.get('ctx', {})
        if 'reason' not in data:
            _logger.error('Invalid Battle Pass Reward data received! "reward" key missing!')
            return
        reason = data['reason']
        if reason in (BattlePassRewardReason.VOTE,):
            if IS_DEVELOPMENT:
                _logger.info('Battle Pass award message ignored because of its reason.')
            return
        for key in ('newLevel', 'newState', 'prevState', 'prevLevel'):
            if key not in data:
                _logger.error('Invalid Battle Pass Reward data received! "%s" key missing!', key)
                return

        isPremiumPurchase = reason in (BattlePassRewardReason.PURCHASE_BATTLE_PASS, BattlePassRewardReason.PURCHASE_BATTLE_PASS_LEVELS)
        prevState = data['prevState']
        level = data['newLevel']
        state = data['newState']
        if state == BattlePassState.POST and prevState == BattlePassState.BASE and reason != BattlePassRewardReason.PURCHASE_BATTLE_PASS:
            g_eventBus.handleEvent(events.BattlePassEvent(events.BattlePassEvent.BUYING_THINGS), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__battlePassController.getFinalFlowSM().startFlow([rewards], data)
        elif isPremiumPurchase or self.__battlePassController.isRareLevel(level, isBase=BattlePassState.BASE == state):
            if rewards:
                showBattlePassAwardsWindow([rewards], data)
            else:
                _logger.error("Can't show empty or invalid reward!")


class BattlePassBuyEmptyHandler(ServiceChannelHandler):
    __battlePassController = dependency.descriptor(IBattlePassController)

    def __init__(self, awardCtrl):
        super(BattlePassBuyEmptyHandler, self).__init__(SYS_MESSAGE_TYPE.battlePassBought.index(), awardCtrl)

    def _needToShowAward(self, ctx):
        needToShow = super(BattlePassBuyEmptyHandler, self)._needToShowAward(ctx)
        if needToShow:
            currentLevel = self.__battlePassController.getCurrentLevel()
            return currentLevel == 0 and self.__battlePassController.getState() == BattlePassState.BASE
        return False

    def _showAward(self, ctx):
        showBattlePassAwardsWindow([], {'reason': BattlePassRewardReason.PURCHASE_BATTLE_PASS})


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


class TenYearsCountdownHandler(MultiTypeServiceChannelHandler):

    def __init__(self, awardCtrl):
        super(TenYearsCountdownHandler, self).__init__((SYS_MESSAGE_TYPE.battleResults.index(), SYS_MESSAGE_TYPE.tokenQuests.index()), awardCtrl)
        self.__pending = []
        self.__locked = False

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

    def __show10YCAward(self, questID, data):
        if data is not None:
            bonuses, _ = getProgressiveRewardBonuses(data['detailedRewards'][questID])
            if questID.startswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_PREFIX) and questID.endswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_POSTFIX):
                bonuses.append(getTokenAward())
            show10YCAwardWindow(bonuses, questID, closeCallback=self.__unlock)
        else:
            self.__unlock()
        return

    def __sortAwardIDs(self, nameQuests):
        quests = []
        for questID in nameQuests:
            if questID.startswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_PREFIX) and questID.endswith(TEN_YEAR_COUNTDOWN_QUEST_TOKEN_POSTFIX):
                quests.append(questID)

        if EVENT_STYLE_MISSION_ID in nameQuests:
            quests.append(EVENT_STYLE_MISSION_ID)
        if EVENT_BADGE_MISSION_ID in nameQuests:
            quests.append(EVENT_BADGE_MISSION_ID)
        return quests

    def _showAward(self, ctx):
        _, message = ctx
        data = message.data.copy()
        nameQuests = data.get('completedQuestIDs', set())
        quests10YC = self.__sortAwardIDs(nameQuests)
        for questID in quests10YC:
            self.__processOrHold(self.__show10YCAward, (questID, data))
