# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/players.py
import typing
from collections import namedtuple
from gui.battle_results.components import style
from gui.battle_results.reusable import shared
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
_ClanInfo = namedtuple('_ClanInfo', 'clanDBID clanAbbrev')

class PlayerInfo(shared.ItemInfo):
    __slots__ = ('__dbID', '__team', '__fakeName', '__realName', '__prebattleID', '__igrType', '__clanInfo', '__isTeamKiller', 'squadIndex', '__tags', '__weakref__')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, dbID=0, team=0, name='', realName=style.getUnknownPlayerName(), prebattleID=0, igrType=0, clanAbbrev='', clanDBID=0, wasInBattle=True):
        super(PlayerInfo, self).__init__(wasInBattle=wasInBattle)
        self.__dbID = dbID
        self.__team = team
        self.__fakeName = name or realName
        self.__realName = realName
        self.__prebattleID = prebattleID
        self.__igrType = igrType
        self.__clanInfo = _ClanInfo(clanDBID, clanAbbrev)
        self.__isTeamKiller = False
        self.__tags = set()
        self.squadIndex = 0

    @property
    def dbID(self):
        return self.__dbID

    @property
    def team(self):
        return self.__team

    @property
    def fakeName(self):
        return self.__fakeName

    @property
    def prebattleID(self):
        return self.__prebattleID

    @property
    def igrType(self):
        return self.__igrType

    @property
    def clanInfo(self):
        return self.__clanInfo

    @property
    def clanDBID(self):
        return self.__clanInfo.clanDBID

    @property
    def clanAbbrev(self):
        return self.__clanInfo.clanAbbrev

    @property
    def realName(self):
        return self.__realName

    @property
    def tags(self):
        return self.__tags

    def addTag(self, tag):
        self.__tags.add(tag)

    def getFullName(self):
        return self.lobbyContext.getPlayerFullName(self.__realName, clanAbbrev=self.clanAbbrev, pDBID=self.__dbID)

    def getRegionCode(self):
        return self.lobbyContext.getRegionCode(self.__dbID)


class PlayersInfo(shared.UnpackedInfo):
    __slots__ = ('__players',)

    def __init__(self, players):
        super(PlayersInfo, self).__init__()

        def _convert(item):
            dbID, info = item
            if info is None:
                self._addUnpackedItemID(dbID)
                info = {}
            return (item[0], PlayerInfo(dbID, **info))

        self.__players = dict(map(_convert, players.iteritems()))

    def getPlayerInfo(self, dbID):
        if dbID in self.__players:
            info = self.__players[dbID]
        else:
            info = PlayerInfo(dbID=dbID, wasInBattle=False)
        return info

    @staticmethod
    def makePlayerInfo(dbID=0, realName='', fakeName='', isEnemy=False, wasInBattle=False):
        unknownPlayerName = style.getUnknownPlayerName(isEnemy=isEnemy)
        return PlayerInfo(dbID=dbID, name=fakeName or unknownPlayerName, realName=realName or unknownPlayerName, wasInBattle=wasInBattle)

    def setSquadIndex(self, dbID, index):
        if dbID in self.__players:
            self.__players[dbID].squadIndex = index

    def getPlayerInfoIterator(self):
        for dbID, info in self.__players.iteritems():
            yield (dbID, info)

    def getFirstAllyClan(self, team):
        result = findFirst(lambda player: player.clanDBID and player.team == team, self.__players.itervalues(), PlayerInfo())
        return result.clanInfo

    def getFirstEnemyClan(self, team):
        result = findFirst(lambda player: player.clanDBID and player.team != team, self.__players.itervalues(), PlayerInfo())
        return result.clanInfo
