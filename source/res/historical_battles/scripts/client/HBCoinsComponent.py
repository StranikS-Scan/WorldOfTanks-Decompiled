# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBCoinsComponent.py
import sys
from datetime import datetime
import typing
import BigWorld
from Event import Event
from PlayerEvents import g_playerEvents
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from historical_battles_common import account_commands
from historical_battles_common.hb_constants import HB_COINS_GAME_PARAMS_KEY
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class HBCoinsComponent(BigWorld.StaticScriptComponent):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__tokens = None
        self.onCoinsCountChanged = Event()
        g_clientUpdateManager.addCallback('tokens', self.__handleTokensUpdate)
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        return

    def getName(self, tokenID):
        return next((name for name, cfg in self.__getCfg().iteritems() if cfg.get('token', {}).get('id') == tokenID), None)

    def getNameAndCount(self, tokenID):
        name = self.getName(tokenID)
        return (None, 0) if name is None else (name, self.__itemsCache.items.tokens.getTokenCount(tokenID))

    def getTokenName(self, coinName):
        return self.__getCoinCfg(coinName).get('token', {}).get('id')

    def getCount(self, name):
        tokenID = self.getTokenName(name)
        return 0 if tokenID is None else self.__itemsCache.items.tokens.getTokenCount(tokenID)

    def isExchangeEnabled(self, coinName):
        return self.__getCoinCfg(coinName).get('exchange', {}).get('enabled', False)

    def isExchangeStarted(self, coinName):
        startDate = self.__getCoinCfg(coinName).get('exchange', {}).get('startDate', sys.maxint)
        return datetime.utcfromtimestamp(startDate) <= datetime.utcnow()

    def getExchangePrice(self, coinName):
        cfg = self.__getCoinCfg(coinName).get('exchange', {}).get('price')
        return (None, None) if cfg is None else (cfg['currency'], cfg['amount'])

    def exchange(self, coinsToGive, coinsToGet, count, callback=None):
        self.entity._doCmdIntStrArr(account_commands.CMD_HB_EXCHANGE_COINS, count, [coinsToGive, coinsToGet], callback)

    def addDev(self, name, count):
        self.entity._doCmdIntStr(account_commands.CMD_HB_ADD_COINS_DEV, count, name, None)
        return

    def drawDev(self, name, count):
        self.entity._doCmdIntStr(account_commands.CMD_HB_DRAW_COINS_DEV, count, name, None)
        return

    def __getCfg(self):
        settings = self.__lobbyContext.getServerSettings().getSettings()
        return settings.get(HB_COINS_GAME_PARAMS_KEY, {})

    def __getCoinCfg(self, name):
        return self.__getCfg().get(name, {})

    def __handleTokensUpdate(self, diff):
        if not self.__tokens:
            self.__tokens = {cfg['token']['id']:name for name, cfg in self.__getCfg().iteritems()}
        for token in diff.iterkeys():
            name = self.__tokens.get(token)
            if name is not None:
                self.onCoinsCountChanged(name)

        return

    def __onAccountBecomeNonPlayer(self):
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        g_clientUpdateManager.removeCallback('tokens', self.__handleTokensUpdate)
        self.onCoinsCountChanged.clear()
