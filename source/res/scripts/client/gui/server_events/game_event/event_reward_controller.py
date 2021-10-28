# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/event_reward_controller.py
from collections import namedtuple
from weakref import proxy
import itertools
from adisp import async
import BigWorld
from gui.ClientUpdateManager import g_clientUpdateManager
from gui import SystemMessages
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus
from gui.shared.events import GUICommonEvent
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError, makeI18nSuccess
from gui.shared.utils import decorators
from constants import EVENT, NC_MESSAGE_PRIORITY
from gui.server_events.conditions import getBattleResultItemDataFromQuestCondition as getQuestCond
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from messenger import g_settings
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
QuestConditions = namedtuple('QuestConditions', ['difficultyLevel', 'environmentID', 'phaseNum'])
QuestConditions.__new__.__defaults__ = (0,) * len(QuestConditions._fields)
BoxPrice = namedtuple('BoxPrice', ['currency', 'amount'])
BoxPrice.__new__.__defaults__ = (None, 0)

class RewardBox(namedtuple('RewardBox', ['boxIndex',
 'decodePrice',
 'skipPrice',
 'bonusRewards',
 'bonusVehicles',
 'questConditions'])):

    def getCtx(self):
        return dict(self._asdict())


class EventRewardController(object):
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, gameEventController):
        super(EventRewardController, self).__init__()
        self._gameEventController = proxy(gameEventController)
        self.__rewardBoxesConfig = {}
        self.__rewardBoxesIdsInOrder = []

    def init(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__handleTokensUpdate})
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyLoaded)

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyLoaded)
        self.__rewardBoxesConfig = {}
        self.__rewardBoxesIdsInOrder = []

    def isEnabled(self):
        return self.__getConfig().get('enabled', False)

    def isRewardBoxOpened(self, rewardBoxID):
        openedTokenID = rewardBoxID + self.__getConfig().get('openedBoxSuffix', '')
        return self._gameEventController.eventsCache.questsProgress.getTokenCount(openedTokenID) > 0

    def isRewardBoxRecieved(self, rewardBoxID):
        return self._gameEventController.eventsCache.questsProgress.getTokenCount(rewardBoxID) > 0

    def getRewardBoxKeyQuantity(self):
        return self._gameEventController.getShop().getKeys()

    def getCurrentRewardProgress(self):
        return sum(list((int(self.isRewardBoxOpened(boxID)) for boxID in self.rewardBoxesIDsInOrder)))

    def getAvailbleRewardProgress(self):
        return sum(list((int(self.isRewardBoxRecieved(boxID)) for boxID in self.rewardBoxesIDsInOrder)))

    def getMaxRewardProgress(self):
        return len(self.rewardBoxesIDsInOrder) - 1

    def iterAvailbleRewardBoxIDsInOrder(self):
        return (boxID for boxID in self.rewardBoxesIDsInOrder if self.isRewardBoxRecieved(boxID))

    @async
    @decorators.process('updating')
    def openRewardBox(self, boxID, isSkipQuest, callback):
        if not self.isEnabled():
            error = makeI18nError(OpenRewardBoxProcessor.MSG_KEY.format('server_error'))
            SystemMessages.pushMessage(error.userMsg, type=error.sysMsgType)
            return
        result = yield OpenRewardBoxProcessor(self, boxID, isSkipQuest).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    @property
    def rewardBoxesConfig(self):
        if not self.isEnabled():
            self.__rewardBoxesConfig = {}
        elif not self.__rewardBoxesConfig:
            self.__rewardBoxesConfig = dict(((boxID, RewardBox(index, BoxPrice(*self.__getRewardBoxPrice(boxID)), BoxPrice(*self.__getRewardBoxQuestSkipPrice(boxID)), self.__getRewardBonuses(boxID), self.__getRewardBonuses(boxID, True), self.__getRewardBoxQuestConditions(boxID))) for index, boxID in enumerate(self.rewardBoxesIDsInOrder)))
        return self.__rewardBoxesConfig

    @property
    def rewardBoxesIDsInOrder(self):
        if not self.isEnabled():
            self.__rewardBoxesIdsInOrder = []
        elif not self.__rewardBoxesIdsInOrder:
            self.__rewardBoxesIdsInOrder = list((boxID for boxID in self.__getRewardBoxes().iterkeys()))
            self.__rewardBoxesIdsInOrder.sort()
        return self.__rewardBoxesIdsInOrder

    def __getRewardBoxQuestSkipPrice(self, rewardBoxID):
        return self.__getRewardBoxes().get(rewardBoxID, {}).get('questSkipCost', (None, 0))

    def __getRewardBoxPrice(self, rewardBoxID):
        return self.__getRewardBoxes().get(rewardBoxID, {}).get('cost', (None, 0))

    def __getRewardBoxQuestConditions(self, rewardBoxID):
        quest = self._gameEventController.eventsCache.getAllQuests().get(rewardBoxID)
        if quest is not None:
            questConditions = QuestConditions(*(val for val, _ in (getQuestCond(quest, key) for key in QuestConditions._fields)))
            diffCtrl = self._gameEventController.getDifficultyController()
            phaseNum = diffCtrl.getPhaseNumber(questConditions.environmentID, questConditions.difficultyLevel)
            return QuestConditions(questConditions.difficultyLevel, questConditions.environmentID, phaseNum)
        else:
            return QuestConditions()

    def __getRewardBonuses(self, rewardBoxID, isVehicle=False):
        rewards = []
        bonusesConfig = self.__getRewardBoxes().get(rewardBoxID, {}).get('bonus', {})
        if isVehicle:
            questsToRun = self.__getRewardBoxes().get(rewardBoxID, {}).get('questsToRun', [])
            quests = self._gameEventController.eventsCache.getHiddenQuests(lambda q: q.getID() in questsToRun)
            if quests:
                rewards.extend((bonus for bonus in itertools.chain.from_iterable((q.getBonuses() for q in quests.itervalues())) if bonus.getName() == 'vehicles'))
        bonusTypeFilter = (lambda type: type == 'vehicles') if isVehicle else (lambda type: type != 'vehicles')
        for bonusType, bonusValue in bonusesConfig.iteritems():
            if bonusTypeFilter(bonusType):
                rewards.extend(getNonQuestBonuses(bonusType, bonusValue))

        return rewards

    def __getConfig(self):
        return self._gameEventController.eventsCache.getGameEventData().get('rewardBox', {})

    def __getRewardBoxes(self):
        return self.__getConfig().get('boxes', {}) if self.isEnabled() else {}

    def __getRewardBox(self, boxID):
        return self.__getRewardBoxes().get(boxID, {})

    def __getRewardVehicle(self, token):
        bonusVehicles = first(self.rewardBoxesConfig[token].bonusVehicles)
        if bonusVehicles is None:
            return
        else:
            rewardData = first(bonusVehicles.getVehicles())
            return first(rewardData)

    def __handleTokensUpdate(self, diff):
        hasDailyTokens = False
        for token in diff.iterkeys():
            if token.startswith(EVENT.REWARD_BOX.TOKEN_PREFIX):
                self._gameEventController.onRewardBoxUpdated()
                self.__processSystemMessages(token)
            if token.startswith(EVENT.REWARD_BOX.KEY_TOKEN):
                self._gameEventController.onRewardBoxKeyUpdated()
            if token.startswith(EVENT.HW21_DAILY_TOKEN_PREFIX):
                hasDailyTokens = hasDailyTokens or bool(diff[token])

        if hasDailyTokens:
            self.__processDailyQuestsSystemMessage()

    def __handleLobbyLoaded(self, _):
        for token in self.itemsCache.items.tokens.getTokens().iterkeys():
            if token.startswith(EVENT.REWARD_BOX.TOKEN_PREFIX) and not self.isRewardBoxOpened(token) and not self.settingsCore.serverSettings.getHW21NotificationShown(token):
                self.__processSystemMessages(token)

    def __processDailyQuestsSystemMessage(self):
        SystemMessages.pushMessage(type=SM_TYPE.halloweenNewDailyQuests, text=backport.text(R.strings.event.serviceChannelMessages.newDailyQuests()))

    def __processSystemMessages(self, token):
        if token not in self.rewardBoxesIDsInOrder:
            return
        if token == self.rewardBoxesIDsInOrder[-1] and self.isRewardBoxOpened(token):
            rewardBoxAchievedMsg = R.strings.system_messages.event_progression_reward_box_achieved.final
            rewardVehicle = self.__getRewardVehicle(token)
            purchaseNameString = g_settings.htmlTemplates.format('halloweenProgressionReward', ctx={'text': rewardVehicle.userName})
            SystemMessages.pushMessage(type=SM_TYPE.halloweenProgressionUpdate, text=backport.text(rewardBoxAchievedMsg.body(), vehicle=purchaseNameString), messageData={'header': backport.text(rewardBoxAchievedMsg.title())})
        elif not self.isRewardBoxOpened(token):
            rewardBoxAchievedMsg = R.strings.system_messages.event_progression_reward_box_achieved
            SystemMessages.pushMessage(type=SM_TYPE.halloweenProgressionUpdate, text=backport.text(rewardBoxAchievedMsg.body()), messageData={'header': backport.text(rewardBoxAchievedMsg.title())})
            self.settingsCore.serverSettings.setHW21NotificationShown(token)
        else:
            rewardVehicle = self.__getRewardVehicle(token)
            if not (rewardVehicle and not rewardVehicle.isInInventory):
                return
            SystemMessages.pushI18nMessage(MESSENGER.SERVICECHANNELMESSAGES_HALLOWEENHANGAR_EVENTVEHICLEACQUIRED, vehicle=rewardVehicle.userName, type=SM_TYPE.Information, priority=NC_MESSAGE_PRIORITY.DEFAULT)


class OpenRewardBoxProcessor(Processor):
    MSG_KEY = 'hw19_open_interrogation/{}'
    MSG_TYPE = SM_TYPE.EventOpenedRewardBox

    def __init__(self, controller, rewardBoxID, isSkipQuest):
        super(OpenRewardBoxProcessor, self).__init__(plugins=(plugins.CheckRewardBox(controller, rewardBoxID, isSkipQuest),))
        self._controller = controller
        self._rewardBoxID = rewardBoxID
        self._isSkipQuest = isSkipQuest

    def _request(self, callback):
        BigWorld.player().openRewardBox(self._rewardBoxID, self._isSkipQuest, lambda requestID, code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(self.MSG_KEY.format(errStr), defaultSysMsgKey=self.MSG_KEY.format('server_error'))

    def _successHandler(self, code, ctx=None):
        rewardBox = self._controller.rewardBoxesConfig[self._rewardBoxID]
        money = rewardBox.decodePrice.amount if not self._isSkipQuest else rewardBox.skipPrice.amount
        return makeI18nSuccess(self.MSG_KEY.format('success'), money=money, type=self.MSG_TYPE)
