# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/common.py
import typing
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.game_control.wallet import WalletController
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared.utils.requesters import IStatsRequester
if typing.TYPE_CHECKING:
    from typing import Dict
_BATTLE_PASS_CHAPTER_STATE_NAME = {ChapterState.NOT_STARTED: 'not_started',
 ChapterState.PAUSED: 'paused',
 ChapterState.ACTIVE: 'active',
 ChapterState.COMPLETED: 'completed'}

def formatBalance(stats):
    actualMoney = stats.actualMoney.toDict()
    balanceData = {Currency.currencyExternalName(currency):actualMoney.get(currency, 0) for currency in Currency.ALL}
    balanceData.update(stats.dynamicCurrencies)
    return balanceData


def formatWalletCurrencyStatuses(stats):
    statuses = {Currency.currencyExternalName(currencyCode):WalletController.STATUS.getKeyByValue(statusCode).lower() for currencyCode, statusCode in stats.currencyStatuses.iteritems() if currencyCode in Currency.ALL}
    statuses.update({currencyCode:WalletController.STATUS.getKeyByValue(statusCode).lower() for currencyCode, statusCode in stats.dynamicCurrencyStatuses.iteritems()})
    return statuses


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def formatBattlePassInfo(battlePass=None):
    return {'isActive': not battlePass.isPaused() and battlePass.isVisible(),
     'season': {'num': battlePass.getSeasonNum(),
                'leftTime': battlePass.getFinalOfferTime()},
     'chapters': {chapterID:{'isBought': battlePass.isBought(chapterID=chapterID),
                  'state': _BATTLE_PASS_CHAPTER_STATE_NAME[battlePass.getChapterState(chapterID)]} for chapterID in battlePass.getChapterIDs() if not battlePass.isExtraChapter(chapterID)}}
