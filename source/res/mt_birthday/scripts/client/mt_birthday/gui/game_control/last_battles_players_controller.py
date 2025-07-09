# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/game_control/last_battles_players_controller.py
import collections
import typing
from adisp import adisp_process
from chat_shared import SYS_MESSAGE_TYPE
from constants import ARENA_BONUS_TYPE, BATTLE_RESULTS_MAXIMUM_CACHE_SIZE
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from mt_birthday.gui.feature_types import BattlePlayerData, ArenaData
from mt_birthday.gui.shared.gui_items.processors.last_battles_players import LastBattlesPlayersProcessor
from mt_birthday.skeletons.mt_birthday_controller import ILastBattlesPlayersController
from mt_birthday.birthday_constants import LAST_BATTLES_PLAYERS_SAVE_COUNT
from queues.LRUCache import LRUCache
from skeletons.gui.battle_results import IBattleResultsService
from wg_async import wg_async, wg_await, await_callback
from BWUtil import AsyncReturn
if typing.TYPE_CHECKING:
    from typing import List
_TEAM_KEYS = {'team{}'.format(number) for number in (1, 2)}

class LastBattlesPlayersController(ILastBattlesPlayersController):
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self):
        self._lastArenas = LRUCache(LAST_BATTLES_PLAYERS_SAVE_COUNT)
        self.__additionalPlayers = {}
        self.__playersFromBattles = {}

    def init(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__onChatMessageReceived

    def fini(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__onChatMessageReceived

    def onAccountBecomePlayer(self):
        self.__battleResults.onResultPosted += self.__showBattleResults

    def onAvatarBecomePlayer(self):
        if self.__showBattleResults in self.__battleResults.onResultPosted:
            self.__battleResults.onResultPosted -= self.__showBattleResults

    def onDisconnected(self):
        if self.__showBattleResults in self.__battleResults.onResultPosted:
            self.__battleResults.onResultPosted -= self.__showBattleResults
        self.__clearCache()
        self._lastArenas.clear()

    @wg_async
    def getLastFightsPlayers(self):
        result = collections.OrderedDict(self.__additionalPlayers.copy())
        lastArenas = []
        for _, data in self._lastArenas:
            lastArenas.append(data)

        yield wg_await(self.__preparePlayersData(lastArenas))
        for data in reversed(lastArenas):
            if not data.isLost:
                for player in sorted(data.players, key=lambda p: p.name):
                    if player.spaID not in result:
                        result[player.spaID] = player

        raise AsyncReturn(result.values())

    def addLastFightsPlayerID(self, playerID):
        if playerID not in self.__additionalPlayers:
            self.__additionalPlayers[playerID] = BattlePlayerData(spaID=playerID, arenaUniqueID=0, name=None, clanAbbrev=None)
        return

    def addLastFightsPlayersIDs(self, playersIDs):
        for playerID in playersIDs:
            self.addLastFightsPlayerID(playerID)

    def __onChatMessageReceived(self, _, message):
        if message.type == SYS_MESSAGE_TYPE.battleResults.index():
            arenaUniqueID = message.data.get('arenaUniqueID', None)
            bonusType = message.data.get('bonusType')
            if arenaUniqueID and bonusType in ARENA_BONUS_TYPE.RANDOM_RANGE:
                players = self.__getPlayersFromBattleResults(arenaUniqueID) if self.__battleResults.areResultsPosted(arenaUniqueID) else []
                self._lastArenas.set(arenaUniqueID, ArenaData(arenaUniqueID, False, players))
        return

    def __clearCache(self):
        self.__additionalPlayers.clear()

    @adisp_process
    def __requestDataFromServer(self, arenaUniqueIDs, callback):
        result = yield LastBattlesPlayersProcessor(arenaUniqueIDs).request()
        if result is not None and result.success:
            callback(result.auxData)
        else:
            callback({})
        return

    @wg_async
    def __preparePlayersData(self, arenasData):
        arenasForRequests = {}
        for data in arenasData:
            if not data.isLost and not data.players:
                arenasForRequests[data.arenaUniqueID] = data

        if arenasForRequests:
            results = yield await_callback(self.__requestDataFromServer)(arenasForRequests.keys()[-BATTLE_RESULTS_MAXIMUM_CACHE_SIZE:])
            for arenaID, arenaData in arenasForRequests.iteritems():
                if arenaID in results:
                    arenaData.players = results[arenaID]
                arenaData.isLost = True

    def __getPlayersFromBattleResults(self, arenaUniqueID):
        vo = self.__battleResults.getResultsVO(arenaUniqueID)
        result = []
        for team in _TEAM_KEYS:
            for playerData in vo.get(team, []):
                userVO = playerData.get('userVO', {})
                playerId = playerData.get('playerId', 0)
                if userVO and playerId:
                    result.append(BattlePlayerData(name=userVO['userName'], clanAbbrev=userVO['clanAbbrev'], spaID=playerId, arenaUniqueID=arenaUniqueID))

        return result

    def __showBattleResults(self, reusableInfo, *_):
        arenaUniqueID = reusableInfo.arenaUniqueID
        arenaData = self._lastArenas.peek(arenaUniqueID)
        if arenaData and not arenaData.players:
            arenaData.players.extend(self.__getPlayersFromBattleResults(arenaUniqueID))
            arenaData.isLost = False
