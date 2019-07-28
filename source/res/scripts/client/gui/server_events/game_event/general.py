# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/general.py
import logging
import BigWorld
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from account_helpers.settings_core.ServerSettingsManager import UI_GAME_EVENT_KEYS
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError, makeI18nSuccess
from gui.shared.money import Money
from gui.shared.formatters import formatPrice
from gui.SystemMessages import CURRENCY_TO_SM_TYPE
from gui.shared.utils import decorators
from gui import SystemMessages
from game_event_progress import GameEventProgress
from gui.server_events.conditions import getTokenNeededCountInCondition
from gui.server_events.awards_formatters import getEventAwardFormatter
from gui.server_events.bonuses import mergeBonuses, FloatBonus
from items import vehicles
from gui.impl import backport
from gui.impl.gen import R
DEFAULT_BONUSES = [ FloatBonus(name, 0) for name in ('xpFactor', 'creditsFactor', 'freeXPFactor') ]
GENERAL_PROGRESS_TOKEN = 'se1_general_{}_progress_{}'
_logger = logging.getLogger(__name__)

class GeneralProgress(GameEventProgress):

    def __init__(self, generalId):
        super(GeneralProgress, self).__init__('se1_2019_general_{}'.format(generalId), 'progress', 'final_reward', 'bonuses', 'se1_general_{}_bought_last_level'.format(generalId))
        self._id = generalId

    def getID(self):
        return self._id

    def getFrontID(self):
        return self._getGeneralData().get('frontID', None)

    def isLevelAwardShown(self, level):
        offset = 8 * (level - 1) + self.getID()
        return self._getGameEventServerSetting(UI_GAME_EVENT_KEYS.GENERAL_LEVEL_AWARD_SHOWN, 0) & 1 << offset

    def setLevelAwardIsShown(self, level):
        offset = 8 * (level - 1) + self.getID()
        oldValue = self._getGameEventServerSetting(UI_GAME_EVENT_KEYS.GENERAL_LEVEL_AWARD_SHOWN, 0)
        newValue = oldValue | 1 << offset
        self.settingsCore.serverSettings.saveInGameEventStorage({UI_GAME_EVENT_KEYS.GENERAL_LEVEL_AWARD_SHOWN: newValue})

    def getVehiclesByLevel(self, level):
        return self._getGeneralDataByLevel('vehicles', level, default=[])

    def getAbilitiesByLevel(self, level):
        return sorted(self._getRawAbilitiesByLevel(level), key=lambda abilityID: (-self._getAbilityWeightCoef(self.getAbilityBaseName(abilityID), level), abilityID))

    def getAbilityBaseName(self, abilityID):
        descr = vehicles.g_cache.equipments()[abilityID]
        return '_'.join(descr.name.split('_')[:-1])

    def getCurrentCostForLevel(self, level):
        buyInfo = self._getGeneralDataByLevel('buyInfo', level, default=None)
        return (None, None) if buyInfo is None else (buyInfo['currency'], buyInfo['amount'])

    def getOldCostForLevel(self, level):
        buyInfo = self._getGeneralDataByLevel('buyInfo', level, default=None)
        return (None, None) if buyInfo is None else (buyInfo['currency'], buyInfo['oldAmount'])

    @decorators.process('buyGeneral')
    def buy(self, generalLevel):
        currency, amount = self.getCurrentCostForLevel(generalLevel)
        if currency is None or amount is None:
            return
        else:
            result = yield GeneralItemBuyer(self.getID(), generalLevel, currency, amount).request()
            if result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            self.onItemsUpdated()
            return

    def canBuy(self, generalLevel):
        currency, amount = self.getCurrentCostForLevel(generalLevel)
        return currency is not None and amount is not None

    def isLocked(self):
        return self.getID() in BigWorld.player().generalsLock.values()

    def getProgressTokenName(self):
        return 'se1_general_{}_event_points'.format(self.getID())

    def _getGeneralDataByLevel(self, key, level, default=None):
        generalData = self._getGeneralData()
        if not generalData:
            return default
        levels = generalData.get('levels', {})
        if level in levels:
            levelInfo = levels[level]
            if key in levelInfo:
                return levelInfo[key]
        return default

    def _getGeneralData(self):
        return self.eventsCache.getGameEventData().get('generals', {}).get(self.getID(), None)

    def _getRawAbilitiesByLevel(self, level):
        abilities = []
        for key in ('abilities', 'dummyAbilities'):
            abilities.extend(self._getGeneralDataByLevel(key, level, default=[]))

        return abilities

    def _getAbilityWeightCoef(self, abilityName, level):
        exist = int(abilityName in (self.getAbilityBaseName(abilityID) for abilityID in self._getRawAbilitiesByLevel(level)))
        if level > 0:
            exist += self._getAbilityWeightCoef(abilityName, level - 1)
        return exist


class GeneralItemBuyer(Processor):

    def __init__(self, generalID, level, currency, money):
        super(GeneralItemBuyer, self).__init__(plugins=(plugins.MessageConfirmator('seApril2019ShopBuyBundle', isEnabled=True, ctx={'money': formatPrice(Money(**{currency: money}), reverse=True, useStyle=True, currency=currency, useIcon=True),
          'bundleName': backport.text(R.strings.event.general_buy_page.level.num(level).bundleName())}), plugins.MoneyValidator(Money(**{currency: money}))))
        self._generalID = generalID
        self._generalLevel = level
        self._currency = currency
        self._money = money

    def _request(self, callback):
        _logger.debug('Make server request to buy general_%d for: %d ', self._generalID, self._money)
        BigWorld.player().buyGeneralLevel(self._generalID, self._generalLevel, lambda code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('se_april_2019/%s' % errStr, defaultSysMsgKey='se_april_2019/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('se_april_2019/buy_general_level_success', money=formatPrice(Money(**{self._currency: self._money}), reverse=True, useStyle=True, currency=self._currency, useIcon=True), level=self._generalLevel + 1, type=CURRENCY_TO_SM_TYPE[self._currency])


class GeneralBonusQuest(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, questID, progressTokenName):
        self._questID = questID
        self._progressTokenName = progressTokenName

    def isActive(self):
        return False if self._quest is None else any((item.isAvailable() for item in self._quest.accountReqs.getConditions().items))

    def getBonuses(self):
        if self._quest is None:
            return list(DEFAULT_BONUSES)
        else:
            bonuses = self._quest.getBonuses()
            bonuses.extend(DEFAULT_BONUSES)
            return mergeBonuses(bonuses)

    def getBonusesFormatted(self):
        return getEventAwardFormatter().format(self.getBonuses())

    def getQuestID(self):
        return self._questID

    def getMedalsNeeded(self):
        return 0 if self._quest is None else getTokenNeededCountInCondition(self._quest, self._progressTokenName, default=0)

    @property
    def _quest(self):
        hiddenQuests = self.eventsCache.getHiddenQuests()
        return hiddenQuests[self.getQuestID()] if self.getQuestID() in hiddenQuests else None
