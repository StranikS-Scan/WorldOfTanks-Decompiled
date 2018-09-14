# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/e_sport/unit/club/ctx.py
from constants import PREBATTLE_TYPE, REQUEST_COOLDOWN
from gui.clubs.settings import CLUB_REQUEST_TYPE
from gui.prb_control.entities.base.unit.ctx import UnitRequestCtx
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('__isRated', 'isRated'))
class ChangeRatedUnitCtx(UnitRequestCtx):
    """
    Context to change rated state of club
    """
    __slots__ = ('__isRated',)

    def __init__(self, isRated, waitingID=''):
        super(ChangeRatedUnitCtx, self).__init__(waitingID=waitingID)
        self.__isRated = isRated

    def getRequestType(self):
        return REQUEST_TYPE.CHANGE_RATED

    def isRated(self):
        """
        Change it to rated or unrated
        """
        return self.__isRated


@ReprInjector.withParent(('__battleID', 'battleID'), ('__slotIdx', 'slotIdx'))
class JoinClubBattleCtx(UnitRequestCtx):
    """
    Used to connect to the club battle room through
    standard prb dispatcher (periphery reconnecting allowed)
    """

    def __init__(self, clubDbID, joinTime, allowDelay=True, waitingID='', isUpdateExpected=False):
        super(JoinClubBattleCtx, self).__init__(entityType=PREBATTLE_TYPE.CLUBS, waitingID=waitingID)
        self.__clubDbID = clubDbID
        self.__joinTime = joinTime
        self.__isUpdateExpected = isUpdateExpected
        self.__allowDelay = allowDelay

    def getCooldown(self):
        return REQUEST_COOLDOWN.CLUBS_ANY_CMD_COOLDOWN

    def getRequestType(self):
        return REQUEST_TYPE.JOIN

    def getID(self):
        """
        Gets the ID of club entity that we're joining
        """
        return self.__clubDbID

    def isUpdateExpected(self):
        """
        Is update after operation expected
        """
        return self.__isUpdateExpected

    def isAllowDelay(self):
        """
        Is delay of operation allowed
        """
        return self.__allowDelay

    def getClubDbID(self):
        """
        Getter for club database ID
        """
        return self.__clubDbID

    def getJoiningTime(self):
        """
        Getter for time of player's club joining
        """
        return self.__joinTime

    def _setUpdateExpected(self, value):
        """
        Setter for update expected flag
        Args:
            value: new flag value
        """
        self.__isUpdateExpected = value
