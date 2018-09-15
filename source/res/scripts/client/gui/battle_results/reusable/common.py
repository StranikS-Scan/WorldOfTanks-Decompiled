# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/common.py
from collections import defaultdict
from collections import namedtuple
import ArenaType
from constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE, FINISH_REASON
from debug_utils import LOG_ERROR
from gui.battle_control import arena_visitor
from gui.battle_results.reusable import shared
_BotInfo = namedtuple('BotInfo', 'intCD name')

class CommonInfo(shared.UnpackedInfo):
    """Class contains reusable information about arena.
    This information is fetched from battle_results['common']"""
    __slots__ = ('__arenaTypeID', '__winnerTeam', '__finishReason', '__arenaVisitor', '__bots')

    def __init__(self, arenaTypeID=0, guiType=ARENA_GUI_TYPE.UNKNOWN, bonusType=ARENA_BONUS_TYPE.UNKNOWN, winnerTeam=0, finishReason=FINISH_REASON.UNKNOWN, bots=None, **kwargs):
        super(CommonInfo, self).__init__()
        self.__arenaTypeID = arenaTypeID
        self.__winnerTeam = winnerTeam
        self.__finishReason = finishReason
        self.__bots = defaultdict(lambda : _BotInfo(0, ''))
        if bots is not None:
            for vehicleID, info in bots.iteritems():
                if len(info) > 1:
                    self.__bots[vehicleID] = _BotInfo(*info[:2])
                LOG_ERROR('Bot information can not be unpacked', info)
                break

        if self.__arenaTypeID and self.__arenaTypeID in ArenaType.g_cache:
            arenaType = ArenaType.g_cache[self.__arenaTypeID]
        else:
            arenaType = None
        self.__arenaVisitor = arena_visitor.createSkeleton(arenaType=arenaType, guiType=guiType, bonusType=bonusType)
        return

    @property
    def arenaVisitor(self):
        """Gets instance of _ClientArenaVisitor.
        :return: instance of _ClientArenaVisitor.
        """
        return self.__arenaVisitor

    @property
    def arenaTypeID(self):
        """Gets type ID of arena.
        :return: integer containing type ID.
        """
        return self.__arenaTypeID

    @property
    def arenaGuiType(self):
        """Gets gui type if arena.
        :return: integer containing one of ARENA_GUI_TYPE.*.
        """
        return self.__arenaVisitor.getArenaGuiType()

    @property
    def arenaBonusType(self):
        """Gets bonus type if arena.
        :return: integer containing one of ARENA_BONUS_TYPE.*.
        """
        return self.__arenaVisitor.getArenaBonusType()

    @property
    def arenaSubTypeName(self):
        return self.__arenaVisitor.type.getGamePlayName()

    @property
    def arenaType(self):
        """Gets instance of ArenaType where was the battle from cache.
        :return: instance of ArenaType.
        """
        return self.__arenaVisitor.type

    @property
    def winnerTeam(self):
        """Gets number of team to win the battle.
        :return: integer containing number of team.
        """
        return self.__winnerTeam

    @property
    def finishReason(self):
        """Gets Reason why arena was finished.
        :return: integer containing one of FINISH_REASON.*.
        """
        return self.__finishReason

    @property
    def isMultiTeamMode(self):
        """There was more than two team in the battle."""
        return self.__arenaVisitor.gui.isFalloutMultiTeam()

    def isSquadSupported(self):
        """Can some squad take part in the specified battle?"""
        return self.__arenaVisitor.bonus.isSquadSupported()

    def canTakeSquadXP(self):
        """Can players get xp bonuses for playing in squads?"""
        return self.__arenaVisitor.bonus.canTakeSquadXP()

    def getArenaIcon(self, iconKey):
        """Makes path to arena icon by specified key.
        :param iconKey: string containing path with placeholder for name of icon.
        :return: string containing path to arena icon.
        """
        return self.__arenaVisitor.getArenaIcon(iconKey)

    def getBotInfo(self, vehicleID):
        """Gets bot information if they have.
        :param vehicleID: long containing ID of vehicle.
        :return: instance of BotInfo.
        """
        return self.__bots[vehicleID]
