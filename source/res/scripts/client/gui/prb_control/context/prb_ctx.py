# Embedded file name: scripts/client/gui/prb_control/context/prb_ctx.py
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_TYPE, OBSERVER_VEH_INVENTORY_ID
from constants import PREBATTLE_COMMENT_MAX_LENGTH, PREBATTLE_COMPANY_DIVISION
from external_strings_utils import truncate_utf8
from gui.prb_control import prb_getters
from gui.prb_control import settings as prb_settings
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.shared.utils.decorators import ReprInjector
__all__ = ('JoinModeCtx', 'TrainingSettingsCtx', 'CompanySettingsCtx', 'JoinTrainingCtx', 'JoinCompanyCtx', 'LeavePrbCtx', 'AssignPrbCtx', 'SetTeamStateCtx', 'SetPlayerStateCtx', 'SwapTeamsCtx', 'ChangeOpenedCtx', 'ChangeCommentCtx', 'ChangeDivisionCtx', 'ChangeArenaVoipCtx', 'KickPlayerCtx', 'RequestCompaniesCtx', 'GetPrbRosterCtx')
_REQUEST_TYPE = prb_settings.REQUEST_TYPE
_CTRL_ENTITY_TYPE = prb_settings.CTRL_ENTITY_TYPE
_FUNCTIONAL_FLAG = prb_settings.FUNCTIONAL_FLAG

class _PrbRequestCtx(PrbCtrlRequestCtx):
    __slots__ = ()

    def __init__(self, **kwargs):
        super(_PrbRequestCtx, self).__init__(ctrlType=_CTRL_ENTITY_TYPE.PREBATTLE, **kwargs)

    def getPrbTypeName(self):
        return prb_getters.getPrebattleTypeName(self.getEntityType())


@ReprInjector.withParent()

class JoinModeCtx(_PrbRequestCtx):
    __slots__ = ()

    def __init__(self, prbType, waitingID = '', flags = _FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinModeCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)

    def getID(self):
        return 0


@ReprInjector.withParent(('isOpened', 'isOpened'), ('getComment', 'comment'))

class _TeamSettingsCtx(_PrbRequestCtx):
    __slots__ = ('__isOpened', '__comment', '_isRequestToCreate')

    def __init__(self, prbType, waitingID = '', isOpened = True, comment = '', isRequestToCreate = True, flags = _FUNCTIONAL_FLAG.UNDEFINED):
        super(_TeamSettingsCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)
        self.__isOpened = isOpened
        self.__comment = truncate_utf8(comment, PREBATTLE_COMMENT_MAX_LENGTH)
        self._isRequestToCreate = isRequestToCreate

    def getRequestType(self):
        if self._isRequestToCreate:
            return _REQUEST_TYPE.CREATE
        return _REQUEST_TYPE.CHANGE_SETTINGS

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
        
        @param settings: instance of prebattle_shared.PrebattleSettings.
        @return: True if setting 'isOpened' changed, otherwise - False.
        """
        return self.__isOpened != settings[prb_settings.PREBATTLE_SETTING_NAME.IS_OPENED]

    def isCommentChanged(self, settings):
        """
        Is comment changed in prebattle.
        
        @param settings: instance of prebattle_shared.PrebattleSettings.
        @return: True if setting 'comment' changed, otherwise - False.
        """
        return self.__comment != settings[prb_settings.PREBATTLE_SETTING_NAME.COMMENT]

    def areSettingsChanged(self, settings):
        return self.isOpenedChanged(settings) or self.isCommentChanged(settings)


@ReprInjector.simple(('getWaitingID', 'waitingID'), ('isOpened', 'isOpen'), ('getComment', 'comment'), ('__arenaTypeID', 'arenaTypeID'), ('__roundLen', 'roundLen'), ('_isRequestToCreate', 'isRequestToCreate'))

class TrainingSettingsCtx(_TeamSettingsCtx):
    __slots__ = ('__arenaTypeID', '__roundLen')

    def __init__(self, waitingID = '', isOpened = True, comment = '', isRequestToCreate = True, arenaTypeID = 0, roundLen = 900, flags = _FUNCTIONAL_FLAG.SWITCH):
        super(TrainingSettingsCtx, self).__init__(PREBATTLE_TYPE.TRAINING, waitingID=waitingID, isOpened=isOpened, comment=comment, isRequestToCreate=isRequestToCreate, flags=flags)
        self.__arenaTypeID = arenaTypeID
        self.__roundLen = int(roundLen)

    @classmethod
    def fetch(cls, settings):
        return TrainingSettingsCtx(isOpened=settings['isOpened'], comment=settings['comment'], isRequestToCreate=False, arenaTypeID=settings['arenaTypeID'], roundLen=settings['roundLength'])

    def getArenaTypeID(self):
        return self.__arenaTypeID

    def setArenaTypeID(self, arenaTypeID):
        self.__arenaTypeID = arenaTypeID

    def getRoundLen(self):
        return self.__roundLen

    def setRoundLen(self, roundLen):
        self.__roundLen = int(roundLen)

    def isArenaTypeIDChanged(self, settings):
        return self.__arenaTypeID != settings[prb_settings.PREBATTLE_SETTING_NAME.ARENA_TYPE_ID]

    def isRoundLenChanged(self, settings):
        return self.__roundLen != settings[prb_settings.PREBATTLE_SETTING_NAME.ROUND_LENGTH]

    def areSettingsChanged(self, settings):
        return super(TrainingSettingsCtx, self).areSettingsChanged(settings) or self.isArenaTypeIDChanged(settings) or self.isRoundLenChanged(settings)


@ReprInjector.simple(('getWaitingID', 'waitingID'), 'isOpened', ('getComment', 'comment'), ('__division', 'division'), ('_isRequestToCreate', 'isRequestToCreate'))

class CompanySettingsCtx(_TeamSettingsCtx):
    __slots__ = ('__division',)

    def __init__(self, waitingID = '', isOpened = True, comment = '', division = PREBATTLE_COMPANY_DIVISION.CHAMPION, isRequestToCreate = True, flags = _FUNCTIONAL_FLAG.SWITCH):
        super(CompanySettingsCtx, self).__init__(PREBATTLE_TYPE.COMPANY, waitingID, isOpened, comment, isRequestToCreate, flags)
        self.__division = division

    def getDivision(self):
        return self.__division

    def setDivision(self, division):
        self.__division = division

    def isDivisionChanged(self, settings):
        return self.__division != settings[prb_settings.PREBATTLE_SETTING_NAME.DIVISION]


@ReprInjector.withParent(('__prbID', 'id'), ('__prbType', 'type'))

class _JoinPrbCtx(_PrbRequestCtx):
    __slots__ = ('__prbID',)

    def __init__(self, prbID, prbType, waitingID = '', flags = _FUNCTIONAL_FLAG.UNDEFINED):
        super(_JoinPrbCtx, self).__init__(entityType=int(prbType), waitingID=waitingID, flags=flags)
        self.__prbID = int(prbID)

    def getID(self):
        return self.__prbID

    def getRequestType(self):
        return _REQUEST_TYPE.JOIN


@ReprInjector.simple(('getID', 'prbID'), ('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'))

class JoinTrainingCtx(_JoinPrbCtx):
    __slots__ = ()

    def __init__(self, prbID, waitingID = '', flags = _FUNCTIONAL_FLAG.SWITCH):
        super(JoinTrainingCtx, self).__init__(prbID, PREBATTLE_TYPE.TRAINING, waitingID=waitingID, flags=flags)


@ReprInjector.simple(('getID', 'prbID'), ('getWaitingID', 'waitingID'))

class JoinCompanyCtx(_JoinPrbCtx):
    __slots__ = ()

    def __init__(self, prbID, waitingID = '', flags = _FUNCTIONAL_FLAG.SWITCH):
        super(JoinCompanyCtx, self).__init__(prbID, PREBATTLE_TYPE.COMPANY, waitingID=waitingID, flags=flags)


@ReprInjector.simple(('getID', 'prbID'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'))

class LeavePrbCtx(_PrbRequestCtx):
    __slots__ = ()

    def __init__(self, waitingID = '', flags = _FUNCTIONAL_FLAG.UNDEFINED):
        super(LeavePrbCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID, flags=flags)

    def getRequestType(self):
        return _REQUEST_TYPE.LEAVE

    def getID(self):
        return prb_getters.getPrebattleID()


@ReprInjector.simple(('getID', 'prbID'), ('getPrbTypeName', 'type'), ('getWaitingID', 'waitingID'))

class JoinBattleSessionCtx(_JoinPrbCtx):
    __slots__ = ()

    def __init__(self, prbID, prbType, waitingID = '', flags = _FUNCTIONAL_FLAG.UNDEFINED):
        super(JoinBattleSessionCtx, self).__init__(prbID, prbType, waitingID=waitingID, flags=flags)


@ReprInjector.simple(('__pID', 'pID'), ('__roster', 'roster'), ('getPrbTypeName', 'prbType'), ('getWaitingID', 'waitingID'))

class AssignPrbCtx(_PrbRequestCtx):
    __slots__ = ('__pID', '__roster')

    def __init__(self, pID, roster, waitingID = ''):
        super(AssignPrbCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__pID = pID
        self.__roster = roster

    def getPlayerID(self):
        return self.__pID

    def getRoster(self):
        return self.__roster

    def getRequestType(self):
        return _REQUEST_TYPE.ASSIGN


@ReprInjector.simple(('__team', 'team'), ('__isReadyState', 'isReadyState'), 'getPrbTypeName', ('getWaitingID', 'waitingID'), ('__isForced', 'isForced'), ('__gamePlayMask', 'gamePlayMask'))

class SetTeamStateCtx(_PrbRequestCtx):
    __slots__ = ('__team', '__isReadyState', '__gamePlayMask')

    def __init__(self, team, isReadyState, waitingID = '', isForced = True, gamePlayMask = 0):
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


@ReprInjector.simple(('getVehicleInventoryID', 'vInventoryID'), ('__isReadyState', 'isReadyState'), ('getWaitingID', 'waitingID'))

class SetPlayerStateCtx(_PrbRequestCtx):
    __slots__ = ('__isReadyState',)

    def __init__(self, isReadyState, waitingID = ''):
        super(SetPlayerStateCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__isReadyState = isReadyState

    def doVehicleValidation(self):
        return True

    def isReadyState(self):
        return self.__isReadyState

    def getRequestType(self):
        return _REQUEST_TYPE.SET_PLAYER_STATE

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID


class SwapTeamsCtx(_PrbRequestCtx):
    __slots__ = ()

    def __init__(self, **kwargs):
        super(SwapTeamsCtx, self).__init__(entityType=prb_getters.getPrebattleType(), **kwargs)

    def getRequestType(self):
        return _REQUEST_TYPE.SWAP_TEAMS


@ReprInjector.simple(('__channels', 'channels'), ('getWaitingID', 'waitingID'))

class ChangeArenaVoipCtx(_PrbRequestCtx):
    __slots__ = ('__channels',)

    def __init__(self, channels, waitingID = ''):
        super(ChangeArenaVoipCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__channels = int(channels)

    def getChannels(self):
        return self.__channels

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_ARENA_VOIP


@ReprInjector.simple(('__isObserver', 'isObserver'), ('getWaitingID', 'waitingID'))

class SetPlayerObserverStateCtx(SetPlayerStateCtx):
    __slots__ = ('__isObserver',)

    def __init__(self, isObserver, isReadyState, waitingID = ''):
        super(SetPlayerObserverStateCtx, self).__init__(isReadyState, waitingID)
        self.__isObserver = isObserver

    def doVehicleValidation(self):
        return False

    def isObserver(self):
        return self.__isObserver

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_USER_STATUS

    def getVehicleInventoryID(self):
        return OBSERVER_VEH_INVENTORY_ID


@ReprInjector.simple(('__isOpened', 'isOpened'), ('getWaitingID', 'waitingID'))

class ChangeOpenedCtx(_PrbRequestCtx):
    __slots__ = ('__isOpened',)

    def __init__(self, isOpened, waitingID = ''):
        super(ChangeOpenedCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__isOpened = isOpened

    def isOpened(self):
        return self.__isOpened

    def isOpenedChanged(self, settings):
        return self.__isOpened != settings[prb_settings.PREBATTLE_SETTING_NAME.IS_OPENED]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_OPENED


@ReprInjector.simple(('__comment', 'comment'), ('getWaitingID', 'waitingID'))

class ChangeCommentCtx(_PrbRequestCtx):
    __slots__ = ('__comment',)

    def __init__(self, comment, waitingID = ''):
        super(ChangeCommentCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__comment = truncate_utf8(comment, PREBATTLE_COMMENT_MAX_LENGTH)

    def getComment(self):
        return self.__comment

    def isCommentChanged(self, settings):
        return self.__comment != settings[prb_settings.PREBATTLE_SETTING_NAME.COMMENT]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_COMMENT


@ReprInjector.simple(('__division', 'division'), ('getWaitingID', 'waitingID'))

class ChangeDivisionCtx(_PrbRequestCtx):
    __slots__ = ('__division',)

    def __init__(self, division, waitingID = ''):
        super(ChangeDivisionCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__division = int(division)

    def getDivision(self):
        return self.__division

    def isDivisionChanged(self, settings):
        return self.__division != settings[prb_settings.PREBATTLE_SETTING_NAME.DIVISION]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_DIVISION


@ReprInjector.withParent(('__pID', 'pID'))

class KickPlayerCtx(_PrbRequestCtx):
    __slots__ = ('__pID',)

    def __init__(self, pID, waitingID = ''):
        super(KickPlayerCtx, self).__init__(entityType=prb_getters.getPrebattleType(), waitingID=waitingID)
        self.__pID = pID

    def getPlayerID(self):
        return self.__pID

    def getRequestType(self):
        return _REQUEST_TYPE.KICK


@ReprInjector.simple('isNotInBattle', 'division', 'creatorMask')

class RequestCompaniesCtx(_PrbRequestCtx):
    __slots__ = ('isNotInBattle', 'division', 'creatorMask')

    def __init__(self, isNotInBattle = False, division = 0, creatorMask = '', waitingID = ''):
        super(RequestCompaniesCtx, self).__init__(entityType=PREBATTLE_TYPE.COMPANY, waitingID=waitingID)
        self.isNotInBattle = isNotInBattle
        self.creatorMask = creatorMask
        if division in PREBATTLE_COMPANY_DIVISION.RANGE:
            self.division = division
        else:
            self.division = 0

    def getRequestType(self):
        return _REQUEST_TYPE.PREBATTLES_LIST

    def byDivision(self):
        return self.division in PREBATTLE_COMPANY_DIVISION.RANGE

    def byName(self):
        return self.creatorMask is not None and len(self.creatorMask) > 0


@ReprInjector.simple(('__prbID', 'prbID'), ('getWaitingID', 'waitingID'))

class GetPrbRosterCtx(_PrbRequestCtx):
    __slots__ = ('__prbID',)

    def __init__(self, prbID, prbType, waitingID = ''):
        super(GetPrbRosterCtx, self).__init__(entityType=prbType, waitingID=waitingID)
        self.__prbID = prbID

    def getPrbID(self):
        return self.__prbID

    def getRequestType(self):
        return _REQUEST_TYPE.GET_ROSTER
