# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/halloween_controller.py
from itertools import izip
import logging
import BigWorld
from gui.app_loader import g_appLoader
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from account_helpers.settings_core.ServerSettingsManager import UI_HELLOWEEN_KEYS
from Event import Event, EventManager
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.shared.money import Currency
from gui.shared.events import GUICommonEvent
from gui import SystemMessages
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.server_events.events_helpers import isHalloween
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError, makeI18nSuccess
from gui.shared.money import Money
from gui.shared.utils import decorators
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.locale.EVENT import EVENT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from helpers import dependency
from skeletons.gui.halloween_controller import IHalloweenController
from skeletons.gui.server_events import IEventsCache
from gui.shared.utils import isPopupsWindowsOpenDisabled
from helpers.i18n import makeString as _ms
from helpers.time_utils import getTimeString
from gui.shared.formatters import formatGoldPrice
from gui.SystemMessages import SM_TYPE
from helpers.CallbackDelayer import CallbackDelayer
from gui.shared.formatters.icons import makeImageTag
from gui.server_events.awards_formatters import AWARDS_SIZES, getHalloweenProgressAwardPacker, getHalloweenHangarGUIData
_logger = logging.getLogger(__name__)
HALLOWEEN_SOULS_TOKEN = 'halloween_souls'
HALLOWEEN_PROGRESS_GROUP_PREFIX = 'progress'
HALLOWEEN_PROGRESS_BONUS_GROUP_PREFIX = 'progress_bonus'
HALLOWEEN_PROGRESS_BONUS_ELITE_GROUP_PREFIX = 'progress_bonus_elite'
HALLOWEEN_BOUGHT_LAST_LEVEL = 'halloween_bought_last_level'
HALLOWEEN_FINAL_REWARD = 'halloween_final_reward'
_SNDID_ACHIEVEMENT = 'result_screen_achievements'
_BONUS_ORDER = (Currency.CREDITS,
 Currency.GOLD,
 Currency.CRYSTAL,
 'creditsFactor',
 'freeXP',
 'freeXPFactor',
 'tankmenXP',
 'tankmenXPFactor',
 'xp',
 'xpFactor',
 'dailyXPFactor',
 'creditsFactorHE',
 'xpFactorHE',
 'xpFactorEliteHE',
 'freeXPFactorHE')

class HalloweenController(IHalloweenController):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(HalloweenController, self).__init__()
        self._progress = None
        return

    def init(self):
        pass

    def fini(self):
        self.stop()

    def start(self):
        if self._progress is None:
            self._progress = HalloweenProgress()
            self._progress.init()
        return

    def stop(self):
        if self._progress:
            self._progress.fini()
            self._progress = None
        return

    def getProgress(self):
        return self._progress

    def getSoulsCount(self):
        return self.eventsCache.questsProgress.getTokenCount(HALLOWEEN_SOULS_TOKEN)

    def isEnabled(self):
        return self.eventsCache.isEventEnabled()


class HalloweenProgress(CallbackDelayer):
    _CALLBACK_OFFSET = 2
    _CALLBACK_SHOW_AWARD_WAIT_TIME = 2.0
    eventsCache = dependency.descriptor(IEventsCache)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        CallbackDelayer.__init__(self)
        self._items = None
        self.__em = EventManager()
        self.onItemsUpdated = Event(self.__em)
        return

    def __del__(self):
        CallbackDelayer.destroy(self)

    def init(self):
        self._items = [HalloweenProgressItemEmpty()]
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        self._onSyncCompleted()

    def fini(self):
        self._items = None
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        self.__em.clear()
        self.clearCallbacks()
        return

    @property
    def items(self):
        return self._items

    @decorators.process('buyItem')
    def buyItem(self, item):
        cost = self.getCurrentCostForLevel()
        result = yield HalloweenItemBuyer(cost).request()
        if result.success:
            self.showAward()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def isCompleted(self):
        return self.isMaxLevelBought() or all((item.isCompleted() for item in self.items))

    def isMaxLevelBought(self):
        return bool(self.eventsCache.questsProgress.getTokenCount(HALLOWEEN_BOUGHT_LAST_LEVEL))

    def getCurrentProgressItem(self):
        return next((item for item in reversed(self.items) if item.isCompleted() or self.isMaxLevelBought()), None)

    def getSoulsLeftToNextLevel(self):
        item = self.getCurrentProgressItem()
        if item.getLevel() == self.getMaxLevel():
            return 0
        nextLevel = self.items[item.getLevel() + 1]
        return nextLevel.getMaxProgress() - nextLevel.getCurrentProgress() if nextLevel.isAvailable() else 0

    def getCurrentProgressLevel(self):
        currentLevel = self.getCurrentProgressItem()
        return currentLevel.getLevel() if currentLevel else 0

    def getCurrentCostForLevel(self):
        return self.eventsCache.getHalloweenMaxLevelPrice()

    def isMaxLevelBuyEnabled(self):
        return self.eventsCache.isHalloweenMaxLevelBuyEnabled()

    def getBonusesForSoul(self):
        return self.eventsCache.getHalloweenBonusesForSoul()

    def getMaxProgressItem(self):
        return self.items[-1] if self.items else None

    def getCurrentMaxProgressLevel(self):
        return next((item.getLevel() for item in reversed(self.items) if item.isUnlocked()), 0)

    def getMaxLevel(self):
        return len(self.items) - 1

    def getStartTime(self):
        return self.items[1].getStartTime() if len(self.items) > 1 else 0

    def getLastQuestStartTime(self):
        return self.items[-1].getStartTime() if self.items else 0

    def getFinishTime(self):
        return self.items[-1].getFinishTime() if self.items else 0

    def getFinishTimeLeft(self):
        return self.items[-1].getFinishTimeLeft() if self.items else 0

    def getFirstLockItem(self):
        return next((item for item in self.items if not item.isUnlocked()), None)

    def _onSyncCompleted(self):
        quests = sorted([ q for q in self.eventsCache.getHiddenQuests().itervalues() if self._isHalloweenProgressQuest(q) ], key=HalloweenProgressItem.getLevelFromQuest)
        if len(self.items) > len(quests) + 1:
            self._items = self.items[:len(quests) + 1]
        self.items[0].setQuest(None)
        for index, quest in enumerate(quests, start=1):
            if index >= len(self.items):
                self.items.append(HalloweenProgressItem(quest))
            self.items[index].setQuest(quest)

        self.onItemsUpdated()
        self.stopCallback(self._onSyncCompletedCallback)
        lockItem = self.getFirstLockItem()
        if lockItem:
            self.delayCallback(lockItem.getStartTimeLeft() + self._CALLBACK_OFFSET, self._onSyncCompletedCallback)
        return

    def _onSyncCompletedCallback(self):
        self._onSyncCompleted()

    def _isHalloweenProgressQuest(self, quest):
        return isHalloween(quest.getGroupID()) and quest.getGroupID().endswith(HALLOWEEN_PROGRESS_GROUP_PREFIX)

    def showAward(self):
        serverSettings = self.settingsCore.serverSettings
        if isPopupsWindowsOpenDisabled():
            return
        isQuestsAvailable = len(self._items) > 1
        isShowed = serverSettings.getHalloweenStorage().get(UI_HELLOWEEN_KEYS.AWARD_SHOWN) == 1
        if isShowed or not self.isCompleted() or not isQuestsAvailable:
            return

        def viewCallback():
            serverSettings.saveInHalloweenStorage({UI_HELLOWEEN_KEYS.AWARD_SHOWN: 1})

        bonuses = list(self.getMaxProgressItem().getBonuses())
        hiddenQuests = self.eventsCache.getHiddenQuests()
        if HALLOWEEN_FINAL_REWARD in hiddenQuests:
            bonuses.extend(hiddenQuests[HALLOWEEN_FINAL_REWARD].getBonuses())
        messages = [{'icon': 'event',
          'title': _ms(EVENT.FINAL_REWARD_TITLE),
          'description': _ms(EVENT.FINAL_REWARD_DESCRIPTION),
          'buttonLabel': _ms(EVENT.FINAL_REWARD_CONTINUE),
          'back': 'blue',
          'bonuses': bonuses,
          'soundID': _SNDID_ACHIEVEMENT,
          'callback': viewCallback}]
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.HALLOWEEN_HINTS, ctx={'messages': messages}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onLobbyInited(self, _):
        self.delayCallback(self._CALLBACK_SHOW_AWARD_WAIT_TIME, self.__showAwardDelayed)

    def __showAwardDelayed(self):
        app = g_appLoader.getApp()
        container = app.containerManager.getContainer(ViewTypes.WINDOW)
        if container is not None:
            view = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.EVENT_BATTLE_RESULTS})
            if view is None:
                self.showAward()
        return


class HalloweenProgressItem(object):
    halloweenController = dependency.descriptor(IHalloweenController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, quest):
        super(HalloweenProgressItem, self).__init__()
        self._quest = quest
        self._bonuses = None
        self._bonusesGUI = None
        return

    def setQuest(self, quest):
        self._quest = quest
        if self._bonuses is not None:
            newBonuses = self._getBonuses()
            if len(newBonuses) != len(self._bonuses) or not all((l.getValue() == r.getValue() for l, r in izip(newBonuses, self._bonuses))):
                self._bonuses = newBonuses
                self._bonusesGUI = None
        return

    def getLevel(self):
        return self.getLevelFromQuest(self._quest)

    @staticmethod
    def getLevelFromQuest(quest):
        return int(quest.getID().split('_')[-1])

    def isAvailable(self):
        return False if not self._quest.isAvailable().isValid else self.halloweenController.getProgress().getCurrentProgressLevel() == self.getLevel() - 1

    def isCompleted(self):
        return self._quest.isCompleted()

    def isUnlocked(self):
        return self.getStartTimeLeft() <= 0

    def getCurrentProgress(self):
        maxProgress = self.getMaxProgress()
        if self.isCompleted():
            return maxProgress
        return min(self.halloweenController.getSoulsCount(), maxProgress) if self.isAvailable() else 0

    def getMaxProgress(self):
        for item in self._quest.accountReqs.getConditions().items:
            if item.getName() == 'token' and item.getID() == HALLOWEEN_SOULS_TOKEN:
                return item.getNeededCount()

    def getBonuses(self):
        if self._bonuses is None:
            self._bonuses = self._getBonuses()
        return self._bonuses

    def _getBonuses(self):
        bonuses = {}
        bonusQuest = self._getCorrespondBonusQuest()
        if bonusQuest:
            bonuses.update({bonus.getName():bonus for bonus in bonusQuest.getBonuses()})
        eliteBonusQuest = self._getCorrespondEliteBonusQuest()
        if eliteBonusQuest:
            for eliteBonus in eliteBonusQuest.getBonuses():
                if eliteBonus.getName() not in bonuses:
                    bonuses[eliteBonus.getName()] = eliteBonus
                if '{}EliteHE'.format(eliteBonus.getName()) in _BONUS_ORDER and (eliteBonus.getName() == 'xpFactor' or eliteBonus.getValue() != bonuses[eliteBonus.getName()].getValue()):
                    eliteBonus.setName('{}Elite'.format(eliteBonus.getName()))
                    bonuses[eliteBonus.getName()] = eliteBonus

        for bonus in bonuses.itervalues():
            newName = '{}HE'.format(bonus.getName())
            if newName in _BONUS_ORDER:
                bonus.setName(newName)

        return sorted(bonuses.values(), key=lambda bonus: _BONUS_ORDER.index(bonus.getName()))

    def getGUIBonusData(self):
        if self._bonusesGUI is None:
            self._bonusesGUI = getHalloweenHangarGUIData(self)
        return self._bonusesGUI

    def getStatusDescription(self):
        level = self.getLevel()
        currentLevel = self.halloweenController.getProgress().getCurrentProgressLevel()
        if level == currentLevel:
            levelStatus = _ms(TOOLTIPS.HALLOWEEN_CURRENTLEVEL)
        elif level < currentLevel:
            levelStatus = _ms(TOOLTIPS.HALLOWEEN_LEVELACHIEVED)
        elif self.isUnlocked():
            levelStatus = _ms(TOOLTIPS.HALLOWEEN_LEVELAVAILABLE)
        else:
            levelStatus = getTimeString(self.getStartTime(), TOOLTIPS.HALLOWEEN_LEVELAVAILABILITY)
        return levelStatus

    def getStartTime(self):
        return self._quest.getStartTime()

    def getStartTimeLeft(self):
        return self._quest.getStartTimeLeft()

    def getFinishTimeLeft(self):
        return self._quest.getFinishTimeLeft()

    def getFinishTime(self):
        return self._quest.getFinishTime()

    def _getCorrespondBonusQuest(self):
        return next((q for q in self.eventsCache.getHiddenQuests().itervalues() if self._isHalloweenBonusQuest(q) and self._getLevelFromBonusQuest(q) == self.getLevel()), None)

    def _getCorrespondEliteBonusQuest(self):
        return next((q for q in self.eventsCache.getHiddenQuests().itervalues() if self._isHalloweenEliteBonusQuest(q) and self._getLevelFromBonusQuest(q) == self.getLevel()), None)

    def _getLevelFromBonusQuest(self, quest):
        return int(quest.getID().split('_')[-1])

    def _isHalloweenBonusQuest(self, quest):
        return isHalloween(quest.getGroupID()) and quest.getGroupID().endswith(HALLOWEEN_PROGRESS_BONUS_GROUP_PREFIX)

    def _isHalloweenEliteBonusQuest(self, quest):
        return isHalloween(quest.getGroupID()) and quest.getGroupID().endswith(HALLOWEEN_PROGRESS_BONUS_ELITE_GROUP_PREFIX)


class HalloweenProgressItemEmpty(HalloweenProgressItem):

    def __init__(self):
        super(HalloweenProgressItemEmpty, self).__init__(None)
        return

    def getLevel(self):
        pass

    def isAvailable(self):
        return True

    def isCompleted(self):
        return True

    def getMaxProgress(self):
        pass

    def isUnlocked(self):
        return True

    def getStartTimeLeft(self):
        pass

    def getFinishTimeLeft(self):
        pass

    def getFinishTime(self):
        pass

    def getStartTime(self):
        pass


class HalloweenItemBuyer(Processor):
    halloweenController = dependency.descriptor(IHalloweenController)

    def __init__(self, money):
        super(HalloweenItemBuyer, self).__init__(plugins=(plugins.MessageConfirmator('halloweenShopBuyItem', isEnabled=True), plugins.MoneyValidator(Money(gold=money))))
        self.money = money

    def _request(self, callback):
        _logger.debug('Make server request to buy halloween item for: %s', self.money)
        BigWorld.player().buyHalloweenItem(self.money, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('halloween/%s' % errStr, defaultSysMsgKey='halloween/server_error')

    def _successHandler(self, code, ctx=None):
        maxPorgressItem = self.halloweenController.getProgress().getMaxProgressItem()
        achieves = ' '.join((bonus.label + makeImageTag(bonus.getImage(AWARDS_SIZES.SMALL)) for bonus in getHalloweenProgressAwardPacker().format(maxPorgressItem.getBonuses())))
        return makeI18nSuccess('he_shop/buy_max_level_success', gold=formatGoldPrice(self.money), type=SM_TYPE.PurchaseForGold, achieves=achieves)
