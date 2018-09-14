# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/legacy/ctx.py
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_COMMENT_MAX_LENGTH
from external_strings_utils import truncate_utf8
from gui.prb_control import prb_getters
from gui.prb_control import settings as prb_settings
from gui.prb_control.entities.base.ctx import PrbCtrlRequestCtx
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared.utils.decorators import ReprInjector
_REQUEST_TYPE = prb_settings.REQUEST_TYPE
_CTRL_ENTITY_TYPE = prb_settings.CTRL_ENTITY_TYPE
_FUNCTIONAL_FLAG = prb_settings.FUNCTIONAL_FLAG

class LegacyRequestCtx(PrbCtrlRequestCtx):
    """
    Base context for legacy requests.
    """
    __slots__ = ()

    def __init__(self, **kwargs):
        super(LegacyRequestCtx, self).__init__(ctrlType=CTRL_ENTITY_TYPE.LEGACY, **kwargs)

    def getPrbTypeName(self):
        """
        Returns prebattle type name.
        """
        return prb_getters.getPrebattleTypeName(self.getEntityType())


@ReprInjector.withParent(('isOpened', 'isOpened'), ('getComment', 'comment'))
class TeamSettingsCtx(LegacyRequestCtx):
    """
    Set team settings legacy context.
    """
    __slots__ = ('__isOpened', '__comment', '_isRequestToCreate')

    def __init__(self, prbType, waitingID='', isOpened=True, comment='', isRequestToCreate=True, flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(TeamSettingsCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)
        self.__isOpened = isOpened
        self.__comment = truncate_utf8(comment, PREBATTLE_COMMENT_MAX_LENGTH)
        self._isRequestToCreate = isRequestToCreate

    def getRequestType(self):
        return _REQUEST_TYPE.CREATE if self._isRequestToCreate else _REQUEST_TYPE.CHANGE_SETTINGS

    def isOpened(self):
        return self.__isOpened

    def setOpened(self, isOpened):
        self.__isOpened = isOpened

    def getComment(self):
        return self.__comment

    def setComment(self, comment):
        self.__comment = truncate_utf8(comment, PREBATTLE_COMMENT_MAX_LENGTH)

    def isOpenedChanged(self, settings):
        """
        Is setting 'isOpened' changed.
        Args:
            settings: prebattle settings data
        
        Returns:
            was it changed
        """
        return self.__isOpened != settings[prb_settings.PREBATTLE_SETTING_NAME.IS_OPENED]

    def isCommentChanged(self, settings):
        """
        Is comment changed in prebattle.
        Args:
            settings: prebattle settings data
        
        Returns:
            was it changed
        """
        return self.__comment != settings[prb_settings.PREBATTLE_SETTING_NAME.COMMENT]

    def areSettingsChanged(self, settings):
        """
        Are any of the settings changed.
        Args:
            settings: prebattle settings data
        
        Returns:
            were they changed
        """
        return self.isOpenedChanged(settings) or self.isCommentChanged(settings)


@ReprInjector.withParent(('__prbID', 'id'), ('__prbType', 'type'))
class JoinLegacyCtx(LegacyRequestCtx):
    """
    Joining legacy request context.
    """
    __slots__ = ('__prbID',)

    def __init__(self, prbID, prbType, waitingID='', flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinLegacyCtx, self).__init__(entityType=int(prbType), waitingID=waitingID, flags=flags)
        self.__prbID = int(prbID)

    def getID(self):
        """
        Prebattle ID to join.
        """
        return self.__prbID

    def getRequestType(self):
        return _REQUEST_TYPE.JOIN


@ReprInjector.withParent(('getID', 'prbID'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'))
class LeaveLegacyCtx(LegacyRequestCtx):
    """
    Leaving legacy request context.
    """
    __slots__ = ()

    def getID(self):
        """
        Prebattle ID to leave.
        """
        return prb_getters.getPrebattleID()

    def getRequestType(self):
        return _REQUEST_TYPE.LEAVE


@ReprInjector.withParent(('__pID', 'pID'), ('__roster', 'roster'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'))
class AssignLegacyCtx(LegacyRequestCtx):
    """
    Assign member to team request context.
    """
    __slots__ = ('__pID', '__roster', '__errorString')

    def __init__(self, pID, roster, waitingID=''):
        super(AssignLegacyCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__pID = pID
        self.__roster = roster
        self.__errorString = ''

    def getPlayerID(self):
        """
        Player's ID.
        """
        return self.__pID

    def getRoster(self):
        """
        Player's assignment roster data.
        """
        return self.__roster

    def getLastErrorString(self):
        return self.__errorString

    def getRequestType(self):
        return _REQUEST_TYPE.ASSIGN

    def setErrorString(self, errorString):
        self.__errorString = errorString

    def onResponseReceived(self, code, errorStr=''):
        self.__errorString = errorStr
        super(AssignLegacyCtx, self).onResponseReceived(code)


@ReprInjector.withParent(('__team', 'team'), ('__isReadyState', 'isReadyState'), 'getPrbTypeName', ('getWaitingID', 'waitingID'), ('__isForced', 'isForced'), ('__gamePlayMask', 'gamePlayMask'))
class SetTeamStateCtx(LegacyRequestCtx):
    """
    Change team state request context.
    """
    __slots__ = ('__team', '__isReadyState', '__gamePlayMask')

    def __init__(self, team, isReadyState, waitingID='', isForced=True, gamePlayMask=0):
        super(SetTeamStateCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID, isForced=isForced)
        self.__team = team
        self.__isReadyState = isReadyState
        self.__gamePlayMask = gamePlayMask

    def getTeam(self):
        """
        Get team number.
        """
        return self.__team

    def isReadyState(self):
        """
        Is team ready.
        """
        return self.__isReadyState

    def getGamePlayMask(self):
        """
        Gets gameplay mask which is actually game modes selection mask.
        """
        return self.__gamePlayMask

    def getRequestType(self):
        return _REQUEST_TYPE.SET_TEAM_STATE


@ReprInjector.withParent(('getVehicleInventoryID', 'vInventoryID'), ('__isReadyState', 'isReadyState'), ('__isInitial', 'isInitial'), ('getWaitingID', 'waitingID'))
class SetPlayerStateCtx(LegacyRequestCtx):
    """
    Set player's state request context.
    """
    __slots__ = ('__isReadyState', '__isInitial', '__errorString')

    def __init__(self, isReadyState, isInitial=False, waitingID=''):
        super(SetPlayerStateCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__isReadyState = isReadyState
        self.__isInitial = isInitial
        self.__errorString = ''

    def doVehicleValidation(self):
        """
        Should we do vehicle validation during the
        set ready validation.
        """
        return True

    def isReadyState(self):
        """
        Getter for player's ready state.
        """
        return self.__isReadyState

    def isInitial(self):
        """
        Is this initial request context.
        """
        return self.__isInitial

    def getRequestType(self):
        return _REQUEST_TYPE.SET_PLAYER_STATE

    def getVehicleInventoryID(self):
        """
        Getter for selected vehicle inventory ID
        """
        return g_currentVehicle.invID

    def getLastErrorString(self):
        return self.__errorString

    def setErrorString(self, errorString):
        self.__errorString = errorString

    def onResponseReceived(self, code, errorStr=''):
        self.__errorString = errorStr
        super(SetPlayerStateCtx, self).onResponseReceived(code)


class SwapTeamsCtx(LegacyRequestCtx):
    """
    Teams swap request context.
    """
    __slots__ = ()

    def __init__(self, **kwargs):
        super(SwapTeamsCtx, self).__init__(entityType=prb_getters.getPrebattleType(), **kwargs)

    def getRequestType(self):
        return _REQUEST_TYPE.SWAP_TEAMS


@ReprInjector.withParent(('__isOpened', 'isOpened'), ('getWaitingID', 'waitingID'))
class ChangeOpenedCtx(LegacyRequestCtx):
    """
    Room opened state request context.
    """
    __slots__ = ('__isOpened',)

    def __init__(self, isOpened, waitingID=''):
        super(ChangeOpenedCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__isOpened = isOpened

    def isOpened(self):
        """
        Is it opened
        """
        return self.__isOpened

    def isOpenedChanged(self, settings):
        """
        Is setting 'isOpened' changed.
        Args:
            settings: prebattle settings data
        
        Returns:
            was it changed
        """
        return self.__isOpened != settings[prb_settings.PREBATTLE_SETTING_NAME.IS_OPENED]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_OPENED


@ReprInjector.withParent(('__comment', 'comment'), ('getWaitingID', 'waitingID'))
class ChangeCommentCtx(LegacyRequestCtx):
    """
    Room comment state request context.
    """
    __slots__ = ('__comment',)

    def __init__(self, comment, waitingID=''):
        super(ChangeCommentCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__comment = truncate_utf8(comment, PREBATTLE_COMMENT_MAX_LENGTH)

    def getComment(self):
        return self.__comment

    def isCommentChanged(self, settings):
        """
        Is comment changed in prebattle.
        Args:
            settings: prebattle settings data
        
        Returns:
            was it changed
        """
        return self.__comment != settings[prb_settings.PREBATTLE_SETTING_NAME.COMMENT]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_COMMENT


@ReprInjector.withParent(('__division', 'division'), ('getWaitingID', 'waitingID'))
class ChangeDivisionCtx(LegacyRequestCtx):
    """
    Room division state request context.
    """
    __slots__ = ('__division',)

    def __init__(self, division, waitingID=''):
        super(ChangeDivisionCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__division = int(division)

    def getDivision(self):
        return self.__division

    def isDivisionChanged(self, settings):
        """
        Is division changed in prebattle.
        Args:
            settings: prebattle settings data
        
        Returns:
            was it changed
        """
        return self.__division != settings[prb_settings.PREBATTLE_SETTING_NAME.DIVISION]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_DIVISION


@ReprInjector.withParent(('__pID', 'pID'))
class KickPlayerCtx(LegacyRequestCtx):
    """
    Player kick request context.
    """
    __slots__ = ('__pID',)

    def __init__(self, pID, waitingID=''):
        super(KickPlayerCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__pID = pID

    def getPlayerID(self):
        """
        Player ID to kick from prebattle.
        """
        return self.__pID

    def getRequestType(self):
        return _REQUEST_TYPE.KICK


@ReprInjector.withParent(('__prbID', 'prbID'), ('getWaitingID', 'waitingID'))
class GetLegacyRosterCtx(LegacyRequestCtx):
    """
    Roster getter request context.
    """
    __slots__ = ('__prbID',)

    def __init__(self, prbID, prbType, waitingID=''):
        super(GetLegacyRosterCtx, self).__init__(entityType=prbType, waitingID=waitingID)
        self.__prbID = prbID

    def getPrbID(self):
        return self.__prbID

    def getRequestType(self):
        return _REQUEST_TYPE.GET_ROSTER


class JoinLegacyModeCtx(LegacyRequestCtx):
    """
    Join legacy mode request context.
    """
    __slots__ = ()

    def __init__(self, prbType, waitingID='', flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinLegacyModeCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)

    def getID(self):
        """
        Stub to look like other join mode ctx.
        """
        pass
