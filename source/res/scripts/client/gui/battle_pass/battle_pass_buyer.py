# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_buyer.py
import logging
from adisp import adisp_async, adisp_process
from gui import SystemMessages
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.shared.event_dispatcher import showExchangeXPWindow
from gui.shared.gui_items.processors.battle_pass import BuyBattlePass, BuyBattlePassLevels, BuyBattlePassWithLevels
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shop import showBuyGoldForBattlePass, showBuyGoldForBattlePassLevels
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController, ISoundEventChecker
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BattlePassBuyer(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    __soundEventChecker = dependency.descriptor(ISoundEventChecker)

    @classmethod
    @decorators.adisp_process('buyBattlePass')
    def buyBP(cls, seasonID, chapterID, priceID, onBuyCallback=None):
        if chapterID not in cls.__battlePass.getChapterIDs():
            _logger.error('Invalid chapterID: %s!', chapterID)
            return
        currency, amount = first(cls.__battlePass.getBattlePassCost(chapterID)[priceID].iteritems())
        result = False
        if currency == Currency.GOLD and cls.__itemsCache.items.stats.actualGold < amount:
            showBuyGoldForBattlePass(amount)
        elif currency == Currency.FREE_XP and cls.__itemsCache.items.stats.actualFreeXP < amount:
            showExchangeXPWindow(amount)
        else:
            result = yield cls.__buyBattlePass(seasonID, chapterID, priceID)
        if onBuyCallback:
            onBuyCallback(result)

    @classmethod
    @decorators.adisp_process('buyBattlePass')
    def buyBPWithLevels(cls, seasonID, chapterID, priceID, onBuyCallback=None):
        if chapterID not in cls.__battlePass.getChapterIDs():
            _logger.error('Invalid chapterID: %s!', chapterID)
            return
        spendMoney = cls.__battlePass.getBattlePassCost(chapterID)[priceID].get(Currency.GOLD)
        levelCount = cls.__battlePass.getMaxLevelInChapter(chapterID) - cls.__battlePass.getLevelInChapter(chapterID)
        if levelCount > 0:
            spendMoney += cls.__itemsCache.items.shop.getBattlePassLevelCost().get(Currency.GOLD, 0) * levelCount
        result = False
        if cls.__itemsCache.items.stats.actualGold < spendMoney:
            showBuyGoldForBattlePass(spendMoney)
        else:
            result = yield cls.__buyBattlePassWithLevels(seasonID, chapterID, priceID)
        if onBuyCallback:
            onBuyCallback(result)

    @classmethod
    @decorators.adisp_process('buyBattlePassLevels')
    def buyLevels(cls, seasonID, chapterID, levels=0, onBuyCallback=None):
        if chapterID not in cls.__battlePass.getChapterIDs():
            _logger.error('Invalid chapterID: %s!', chapterID)
            return
        if cls.__battlePass.getChapterState(chapterID) != ChapterState.ACTIVE:
            _logger.error('Chapter %s should be active to buy levels at it!', chapterID)
            return
        spendMoneyGold = 0
        if levels > 0:
            spendMoneyGold += cls.__itemsCache.items.shop.getBattlePassLevelCost().get(Currency.GOLD, 0) * levels
        result = False
        if cls.__itemsCache.items.stats.actualGold < spendMoneyGold:
            showBuyGoldForBattlePassLevels(spendMoneyGold)
        else:
            cls.__soundEventChecker.lockPlayingSounds()
            result = yield cls.__buyBattlePassLevels(seasonID, chapterID, levels)
            cls.__soundEventChecker.unlockPlayingSounds()
        if onBuyCallback:
            onBuyCallback(result)

    @classmethod
    @adisp_async
    @adisp_process
    def __buyBattlePass(cls, seasonID, chapterID, priceID, callback):
        result = yield BuyBattlePass(seasonID, chapterID, priceID).request()
        startLevel, _ = cls.__battlePass.getChapterLevelInterval(chapterID)
        if cls.__battlePass.getLevelInChapter(chapterID) != startLevel - 1:
            callback(result.success)
            return
        else:
            if result.userMsg is not None:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, messageData=result.auxData)
            callback(result.success)
            return

    @staticmethod
    @adisp_async
    @adisp_process
    def __buyBattlePassLevels(seasonID, chapterID, levels, callback):
        result = yield BuyBattlePassLevels(seasonID, chapterID, levels).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    @classmethod
    @adisp_async
    @adisp_process
    def __buyBattlePassWithLevels(cls, seasonID, chapterID, priceID, callback):
        result = yield BuyBattlePassWithLevels(seasonID, chapterID, priceID).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)
