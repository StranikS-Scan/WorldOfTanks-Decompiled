# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/common.py
import typing
from constants import RP_PGB_POINT, RP_POINT
from gui.battle_pass.battle_pass_constants import ChapterState
from gui.game_control.wallet import WalletController
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared.utils.requesters import IStatsRequester
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from helpers.time_utils import getServerUTCTime
from battle_pass_common import BattlePassChapterType
if typing.TYPE_CHECKING:
    from typing import Dict
_BATTLE_PASS_CHAPTER_STATE_NAME = {ChapterState.NOT_STARTED: 'not_started',
 ChapterState.PAUSED: 'paused',
 ChapterState.ACTIVE: 'active',
 ChapterState.COMPLETED: 'completed',
 ChapterState.DISABLED: 'disabled'}
_BATTLEPASS_CHAPTER_TYPE_NAME = {BattlePassChapterType.DEFAULT: 'default',
 BattlePassChapterType.MARATHON: 'marathon',
 BattlePassChapterType.RESOURCE: 'resource'}

def formatBalance(stats):
    actualMoney = stats.actualMoney.toDict()
    balanceData = {Currency.currencyExternalName(currency):actualMoney.get(currency, 0) for currency in Currency.ALL}
    balanceData.update(stats.dynamicCurrencies)
    balanceData['free_xp'] = stats.freeXP
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
                  'state': _BATTLE_PASS_CHAPTER_STATE_NAME[battlePass.getChapterState(chapterID)],
                  'chapterType': _BATTLEPASS_CHAPTER_TYPE_NAME[BattlePassChapterType(battlePass.getChapterType(chapterID))]} for chapterID in battlePass.getChapterIDs() if not battlePass.isMarathonChapter(chapterID)}}


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def formatReferralProgramInfo(lobbyContext=None, itemsCache=None):
    refProgram = itemsCache.items.refProgram
    entitlements = itemsCache.items.stats.entitlements
    rpPgbPoints = entitlements.get(RP_PGB_POINT, 0)
    rpPoints = entitlements.get(RP_POINT, 0)
    pgbLimitPoints = refProgram.getRPPgbPoints()
    timeLeft = max(refProgram.getRPExpirationTime() - int(getServerUTCTime()), 0)
    configLimits = lobbyContext.getServerSettings().getRPConfig()
    passiveIncome = refProgram.getRPPassiveIncome()
    return {'rp_pgb_points': rpPgbPoints,
     'rp_points': rpPoints,
     'rp_pgb_limit_points': pgbLimitPoints,
     'rp_time_left': timeLeft,
     'rp_config_limits': {'pgbCapacity': configLimits.pgbCapacity,
                          'pgbDayLimit': configLimits.pgbDayLimit},
     'rp_passive_income': passiveIncome}
