# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/stats_exchange/__init__.py
import weakref
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import broker
from gui.Scaleform.daapi.view.battle.shared.stats_exchange import player
from gui.Scaleform.daapi.view.battle.shared.stats_exchange.stats_ctrl import BattleStatisticsDataController
__all__ = ('BattleStatisticsDataController', 'createExchangeBroker')

def createExchangeBroker(exchangeCtx):
    proxy = weakref.proxy(exchangeCtx)
    exchangeBroker = broker.ExchangeBroker(exchangeCtx)
    exchangeBroker.setPlayerStatusExchange(player.PlayerStatusComponent())
    exchangeBroker.setUsersTagsExchange(player.UsersTagsListExchangeData(proxy))
    exchangeBroker.setInvitationsExchange(player.InvitationsExchangeBlock())
    return exchangeBroker
