# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/players.py
from collections import namedtuple
from gui.LobbyContext import g_lobbyContext
from gui.battle_results.components import style
from gui.battle_results.reusable import shared
from shared_utils import findFirst
_ClanInfo = namedtuple('_ClanInfo', 'clanDBID clanAbbrev')

class PlayerInfo(shared.ItemInfo):
    """"Shared information about each player which took part in a battle."""
    __slots__ = ('__dbID', '__team', '__name', '__prebattleID', '__igrType', '__clanInfo', 'squadIndex', '__weakref__')

    def __init__(self, dbID=0, team=0, name=style.getUnknownPlayerName(), prebattleID=0, igrType=0, clanAbbrev='', clanDBID=0, wasInBattle=True):
        super(PlayerInfo, self).__init__(wasInBattle=wasInBattle)
        self.__dbID = dbID
        self.__team = team
        self.__name = name
        self.__prebattleID = prebattleID
        self.__igrType = igrType
        self.__clanInfo = _ClanInfo(clanDBID, clanAbbrev)
        self.squadIndex = 0

    @property
    def dbID(self):
        """Returns account's database ID."""
        return self.__dbID

    @property
    def team(self):
        """Returns number of player's team."""
        return self.__team

    @property
    def name(self):
        """Returns player's name."""
        return self.__name

    @property
    def prebattleID(self):
        """Returns unique ID of prebattle (unit) if player joined it."""
        return self.__prebattleID

    @property
    def igrType(self):
        """Returns type of IRG room."""
        return self.__igrType

    @property
    def clanInfo(self):
        """Returns short information about player's clan."""
        return self.__clanInfo

    @property
    def clanDBID(self):
        """Returns database ID of player's clan."""
        return self.__clanInfo.clanDBID

    @property
    def clanAbbrev(self):
        """Returns abbreviate of player's clan."""
        return self.__clanInfo.clanAbbrev

    def getFullName(self):
        """Gets player's full name.
        :return: string containing player's full name.
        """
        return g_lobbyContext.getPlayerFullName(self.__name, clanAbbrev=self.clanAbbrev, pDBID=self.__dbID)

    def getRegionCode(self):
        """Gets player's region code if they are in roaming.
        :return: string containing player's region code.
        """
        return g_lobbyContext.getRegionCode(self.__dbID)


class PlayersInfo(shared.UnpackedInfo):
    """Class contains reusable information about players.
    This information is fetched from battle_results['players']"""
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
        """Gets player's information by specified account's database ID.
        :param dbID: long containing account's database ID.
        :return: instance of PlayerInfo.
        """
        if dbID in self.__players:
            info = self.__players[dbID]
        else:
            info = PlayerInfo(dbID=dbID, wasInBattle=False)
        return info

    @staticmethod
    def makePlayerInfo(dbID=0, name='', isEnemy=False, wasInBattle=False):
        return PlayerInfo(dbID=dbID, name=name or style.getUnknownPlayerName(isEnemy=isEnemy), wasInBattle=wasInBattle)

    def setSquadIndex(self, dbID, index):
        """Sets index of player's squad.
        :param dbID: long containing account's database ID.
        :param index: index of squad.
        :return:
        """
        if dbID in self.__players:
            self.__players[dbID].squadIndex = index

    def getPlayerInfoIterator(self):
        """Gets generator to fetch information about all players in results.
        :return: generator.
        """
        for dbID, info in self.__players.iteritems():
            yield (dbID, info)

    def getFirstAllyClan(self, team):
        """Gets first information about ally clan by specified team.
        :param team: integer containing number of
        :return: instance of _ClanInfo.
        """
        result = findFirst(lambda player: player.clanDBID and player.team == team, self.__players.itervalues(), PlayerInfo())
        return result.clanInfo

    def getFirstEnemyClan(self, team):
        """Gets first information about enemy clan by specified team.
        :param team: integer containing number of
        :return: instance of _ClanInfo.
        """
        result = findFirst(lambda player: player.clanDBID and player.team != team, self.__players.itervalues(), PlayerInfo())
        return result.clanInfo
