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
    __slots__ = ()

    def __init__(self, **kwargs):
        super(LegacyRequestCtx, self).__init__(ctrlType=CTRL_ENTITY_TYPE.LEGACY, **kwargs)

    def getPrbTypeName(self):
        return prb_getters.getPrebattleTypeName(self.getEntityType())


@ReprInjector.withParent(('isOpened', 'isOpened'), ('getComment', 'comment'))
class TeamSettingsCtx(LegacyRequestCtx):
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
        return self.__isOpened != settings[prb_settings.PREBATTLE_SETTING_NAME.IS_OPENED]

    def isCommentChanged(self, settings):
        return self.__comment != settings[prb_settings.PREBATTLE_SETTING_NAME.COMMENT]

    def areSettingsChanged(self, settings):
        return self.isOpenedChanged(settings) or self.isCommentChanged(settings)


@ReprInjector.withParent(('__prbID', 'id'), ('__prbType', 'type'))
class JoinLegacyCtx(LegacyRequestCtx):
    __slots__ = ('__prbID',)

    def __init__(self, prbID, prbType, waitingID='', flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinLegacyCtx, self).__init__(entityType=int(prbType), waitingID=waitingID, flags=flags)
        self.__prbID = int(prbID)

    def getID(self):
        return self.__prbID

    def getRequestType(self):
        return _REQUEST_TYPE.JOIN


@ReprInjector.withParent(('getID', 'prbID'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'))
class LeaveLegacyCtx(LegacyRequestCtx):
    __slots__ = ()

    def getID(self):
        return prb_getters.getPrebattleID()

    def getRequestType(self):
        return _REQUEST_TYPE.LEAVE


@ReprInjector.withParent(('__pID', 'pID'), ('__roster', 'roster'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'))
class AssignLegacyCtx(LegacyRequestCtx):
    __slots__ = ('__pID', '__roster', '__errorString')

    def __init__(self, pID, roster, waitingID=''):
        super(AssignLegacyCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__pID = pID
        self.__roster = roster
        self.__errorString = ''

    def getPlayerID(self):
        return self.__pID

    def getRoster(self):
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


@ReprInjector.withParent(('__roster', 'roster'), ('__fromLane', 'fromLane'), ('__toLane', 'toLane'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'))
class GroupSwapInTeamLegacyCtx(LegacyRequestCtx):
    __slots__ = ('__roster', '__fromLane', '__toLane')

    def __init__(self, roster, fLane, tLane, waitingID=''):
        super(GroupSwapInTeamLegacyCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__roster = roster
        self.__fromLane = fLane
        self.__toLane = tLane

    def getRoster(self):
        return self.__roster

    def getGroups(self):
        return (self.__fromLane, self.__toLane)

    def getRequestType(self):
        return _REQUEST_TYPE.EPIC_SWAP_IN_TEAM


@ReprInjector.withParent(('__lane', 'toLane'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'))
class GroupSwapBetweenTeamLegacyCtx(LegacyRequestCtx):
    __slots__ = ('__lane',)

    def __init__(self, lane, waitingID=''):
        super(GroupSwapBetweenTeamLegacyCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__lane = lane

    def getGroup(self):
        return self.__lane

    def getRequestType(self):
        return _REQUEST_TYPE.EPIC_SWAP_BETWEEN_TEAM


@ReprInjector.withParent(('__pID', 'pID'), ('__roster', 'roster'), ('__group', 'group'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'))
class GroupAssignLegacyCtx(LegacyRequestCtx):
    __slots__ = ('__pID', '__roster', '__group')

    def __init__(self, pID, roster, group, waitingID=''):
        super(GroupAssignLegacyCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__group = group
        self.__pID = pID
        self.__roster = roster

    def getPlayerID(self):
        return self.__pID

    def getRoster(self):
        return self.__roster

    def getRequestType(self):
        return _REQUEST_TYPE.ASSIGN

    def getGroup(self):
        return self.__group


@ReprInjector.withParent(('__team', 'team'), ('__isReadyState', 'isReadyState'), 'getPrbTypeName', ('getWaitingID', 'waitingID'), ('__isForced', 'isForced'), ('__gamePlayMask', 'gamePlayMask'))
class SetTeamStateCtx(LegacyRequestCtx):
    __slots__ = ('__team', '__isReadyState', '__gamePlayMask')

    def __init__(self, team, isReadyState, waitingID='', isForced=True, gamePlayMask=0):
        super(SetTeamStateCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID, isForced=isForced)
        self.__team = team
        self.__isReadyState = isReadyState
        self.__gamePlayMask = gamePlayMask

    def getTeam(self):
        return self.__team

    def isReadyState(self):
        return self.__isReadyState

    def getGamePlayMask(self):
        return self.__gamePlayMask

    def getRequestType(self):
        return _REQUEST_TYPE.SET_TEAM_STATE


@ReprInjector.withParent(('getVehicleInventoryID', 'vInventoryID'), ('__isReadyState', 'isReadyState'), ('__isInitial', 'isInitial'), ('getWaitingID', 'waitingID'))
class SetPlayerStateCtx(LegacyRequestCtx):
    __slots__ = ('__isReadyState', '__isInitial', '__errorString')

    def __init__(self, isReadyState, isInitial=False, waitingID=''):
        super(SetPlayerStateCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__isReadyState = isReadyState
        self.__isInitial = isInitial
        self.__errorString = ''

    def doVehicleValidation(self):
        return True

    def isReadyState(self):
        return self.__isReadyState

    def isInitial(self):
        return self.__isInitial

    def getRequestType(self):
        return _REQUEST_TYPE.SET_PLAYER_STATE

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID

    def getLastErrorString(self):
        return self.__errorString

    def setErrorString(self, errorString):
        self.__errorString = errorString

    def onResponseReceived(self, code, errorStr=''):
        self.__errorString = errorStr
        super(SetPlayerStateCtx, self).onResponseReceived(code)


class SwapTeamsCtx(LegacyRequestCtx):
    __slots__ = ()

    def __init__(self, **kwargs):
        super(SwapTeamsCtx, self).__init__(entityType=prb_getters.getPrebattleType(), **kwargs)

    def getRequestType(self):
        return _REQUEST_TYPE.SWAP_TEAMS


@ReprInjector.withParent(('__isOpened', 'isOpened'), ('getWaitingID', 'waitingID'))
class ChangeOpenedCtx(LegacyRequestCtx):
    __slots__ = ('__isOpened',)

    def __init__(self, isOpened, waitingID=''):
        super(ChangeOpenedCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__isOpened = isOpened

    def isOpened(self):
        return self.__isOpened

    def isOpenedChanged(self, settings):
        return self.__isOpened != settings[prb_settings.PREBATTLE_SETTING_NAME.IS_OPENED]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_OPENED


@ReprInjector.withParent(('__comment', 'comment'), ('getWaitingID', 'waitingID'))
class ChangeCommentCtx(LegacyRequestCtx):
    __slots__ = ('__comment',)

    def __init__(self, comment, waitingID=''):
        super(ChangeCommentCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__comment = truncate_utf8(comment, PREBATTLE_COMMENT_MAX_LENGTH)

    def getComment(self):
        return self.__comment

    def isCommentChanged(self, settings):
        return self.__comment != settings[prb_settings.PREBATTLE_SETTING_NAME.COMMENT]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_COMMENT


@ReprInjector.withParent(('__division', 'division'), ('getWaitingID', 'waitingID'))
class ChangeDivisionCtx(LegacyRequestCtx):
    __slots__ = ('__division',)

    def __init__(self, division, waitingID=''):
        super(ChangeDivisionCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__division = int(division)

    def getDivision(self):
        return self.__division

    def isDivisionChanged(self, settings):
        return self.__division != settings[prb_settings.PREBATTLE_SETTING_NAME.DIVISION]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_DIVISION


@ReprInjector.withParent(('__pID', 'pID'))
class KickPlayerCtx(LegacyRequestCtx):
    __slots__ = ('__pID',)

    def __init__(self, pID, waitingID=''):
        super(KickPlayerCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__pID = pID

    def getPlayerID(self):
        return self.__pID

    def getRequestType(self):
        return _REQUEST_TYPE.KICK


@ReprInjector.withParent(('__prbID', 'prbID'), ('getWaitingID', 'waitingID'))
class GetLegacyRosterCtx(LegacyRequestCtx):
    __slots__ = ('__prbID',)

    def __init__(self, prbID, prbType, waitingID=''):
        super(GetLegacyRosterCtx, self).__init__(entityType=prbType, waitingID=waitingID)
        self.__prbID = prbID

    def getPrbID(self):
        return self.__prbID

    def getRequestType(self):
        return _REQUEST_TYPE.GET_ROSTER


class JoinLegacyModeCtx(LegacyRequestCtx):
    __slots__ = ()

    def __init__(self, prbType, waitingID='', flags=_FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinLegacyModeCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)

    def getID(self):
        pass
