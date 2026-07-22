# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/shared/gui_items/processors/last_battles_players.py
import BigWorld
from gui.shared.gui_items.processors import Processor, makeSuccess
from helpers import dependency
from mt_birthday.gui.feature_types import BattlePlayerData
from skeletons.gui.battle_results import IBattleResultsService

class LastBattlesPlayersProcessor(Processor):
    __slots__ = ('__arenaUniqueIDs',)
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, arenaUniqueIDs):
        super(LastBattlesPlayersProcessor, self).__init__()
        self.__arenaUniqueIDs = arenaUniqueIDs

    def _request(self, callback):
        BigWorld.player().TanksBirthdayAccountComponent.getPlayersFromBattles(self.__arenaUniqueIDs, lambda requestID, resultID, errorStr, ctx=None: self._response(resultID, callback, errorStr, ctx))
        return

    def _successHandler(self, code, ctx=None):
        results = {}
        if ctx is not None:
            for arenaUniqueID, playersData in ctx.iteritems():
                results[arenaUniqueID] = [ BattlePlayerData(name=realName, clanAbbrev=clanAbbrev, spaID=accountDBID, arenaUniqueID=arenaUniqueID) for accountDBID, realName, clanAbbrev in playersData ]

        return makeSuccess(auxData=results)
