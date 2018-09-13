# Embedded file name: scripts/client/gui/prb_control/context/prb_ctx.py
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_TYPE, OBSERVER_VEH_INVENTORY_ID
from constants import PREBATTLE_COMMENT_MAX_LENGTH, PREBATTLE_COMPANY_DIVISION
from external_strings_utils import truncate_utf8
from gui.prb_control import getPrebattleType, getPrebattleID
from gui.prb_control import getPrebattleTypeName
from gui.prb_control import settings as prb_settings
from gui.prb_control.context import PrbCtrlRequestCtx
_REQUEST_TYPE = prb_settings.REQUEST_TYPE
_CTRL_ENTITY_TYPE = prb_settings.CTRL_ENTITY_TYPE

class _PrbRequestCtx(PrbCtrlRequestCtx):

    def getEntityType(self):
        return _CTRL_ENTITY_TYPE.PREBATTLE

    def getPrbType(self):
        return getPrebattleType()

    def getPrbTypeName(self):
        return getPrebattleTypeName(self.getPrbType())


class _PrbEntryCtx(_PrbRequestCtx):

    def __init__(self, waitingID = '', funcExit = prb_settings.FUNCTIONAL_EXIT.NO_FUNC, guiExit = prb_settings.GUI_EXIT.HANGAR):
        super(_PrbEntryCtx, self).__init__(waitingID=waitingID)
        self.__funcExit = funcExit
        self.__guiExit = guiExit

    def getFuncExit(self):
        return self.__funcExit

    def getGuiExit(self):
        return self.__guiExit


class TeamSettingsCtx(_PrbEntryCtx):

    def __init__(self, waitingID = '', isOpened = True, comment = '', isRequestToCreate = True, funcExit = prb_settings.FUNCTIONAL_EXIT.PREBATTLE, guiExit = prb_settings.GUI_EXIT.HANGAR):
        super(TeamSettingsCtx, self).__init__(waitingID=waitingID, funcExit=funcExit, guiExit=guiExit)
        self.__isOpened = isOpened
        self.__comment = truncate_utf8(comment, PREBATTLE_COMMENT_MAX_LENGTH)
        self.__isForced = False
        self._isRequestToCreate = isRequestToCreate

    def __repr__(self):
        return 'TeamSettingsCtx(waitingID = {0:>s}, isOpened = {1!r:s}, comment = {2:>s}, isRequestToCreate={3!r:s}'.format(self.getWaitingID(), self.__isOpened, self.__comment, self._isRequestToCreate)

    def getPrbType(self):
        return PREBATTLE_TYPE.COMPANY

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

    def isForced(self):
        return self.__isForced

    def setForced(self, flag):
        self.__isForced = flag

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


class TrainingSettingsCtx(TeamSettingsCtx):

    def __init__(self, waitingID = '', isOpened = True, comment = '', isRequestToCreate = True, arenaTypeID = 0, roundLen = 900):
        super(TrainingSettingsCtx, self).__init__(waitingID=waitingID, isOpened=isOpened, comment=comment, isRequestToCreate=isRequestToCreate)
        self.__arenaTypeID = arenaTypeID
        self.__roundLen = int(roundLen)

    def __repr__(self):
        return 'TrainingSettingsCtx(waitingID = {0:>s}, isOpen = {1!r:s}, comment = {2:>s}, arenaTypeID={3:n}, roundLen={4:n} sec., isRequestToCreate={5!r:s})'.format(self.getWaitingID(), self.isOpened(), self.getComment(), self.__arenaTypeID, self.__roundLen, self._isRequestToCreate)

    @classmethod
    def fetch(cls, settings):
        return TrainingSettingsCtx(isOpened=settings['isOpened'], comment=settings['comment'], isRequestToCreate=False, arenaTypeID=settings['arenaTypeID'], roundLen=settings['roundLength'])

    def getPrbType(self):
        return PREBATTLE_TYPE.TRAINING

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


class CompanySettingsCtx(TeamSettingsCtx):

    def __init__(self, waitingID = '', isOpened = True, comment = '', division = PREBATTLE_COMPANY_DIVISION.CHAMPION, isRequestToCreate = True):
        super(CompanySettingsCtx, self).__init__(waitingID, isOpened, comment, isRequestToCreate)
        self.__division = division

    def __repr__(self):
        return 'CompanySettingsCtx(waitingID = {0:>s}, isOpened = {1!r:s}, comment = {2:>s}, division = {3:n}, isRequestToCreate={4!r:s})'.format(self.getWaitingID(), self.isOpened(), self.getComment(), self.__division, self._isRequestToCreate)

    def getPrbType(self):
        return PREBATTLE_TYPE.COMPANY

    def getDivision(self):
        return self.__division

    def setDivision(self, division):
        self.__division = division

    def isDivisionChanged(self, settings):
        return self.__division != settings[prb_settings.PREBATTLE_SETTING_NAME.DIVISION]


class SquadSettingsCtx(_PrbRequestCtx):

    def __repr__(self):
        return 'SquadSettingsCtx(waitingID = {0:>s})'.format(self.getWaitingID())

    def getPrbType(self):
        return PREBATTLE_TYPE.SQUAD

    def getRequestType(self):
        return _REQUEST_TYPE.CREATE


class _JoinPrbCtx(_PrbEntryCtx):

    def __init__(self, prbID, prbType, waitingID = '', funcExit = prb_settings.FUNCTIONAL_EXIT.NO_FUNC, guiExit = prb_settings.GUI_EXIT.HANGAR):
        super(_JoinPrbCtx, self).__init__(waitingID=waitingID, funcExit=funcExit, guiExit=guiExit)
        self.__prbID = int(prbID)
        self.__prbType = int(prbType)
        self.__isForced = False

    def getID(self):
        return self.__prbID

    def getRequestType(self):
        return _REQUEST_TYPE.JOIN

    def getPrbType(self):
        return self.__prbType

    def isForced(self):
        return self.__isForced

    def setForced(self, flag):
        self.__isForced = flag


class JoinTrainingCtx(_JoinPrbCtx):

    def __init__(self, prbID, waitingID = ''):
        super(JoinTrainingCtx, self).__init__(prbID, PREBATTLE_TYPE.TRAINING, waitingID, prb_settings.FUNCTIONAL_EXIT.PREBATTLE)

    def __repr__(self):
        return 'JoinTrainingCtx(prbID = {0:n}, waitingID = {1:>s})'.format(self.getID(), self.getWaitingID())


class JoinCompanyCtx(_JoinPrbCtx):

    def __init__(self, prbID, waitingID = ''):
        super(JoinCompanyCtx, self).__init__(prbID, PREBATTLE_TYPE.COMPANY, waitingID, prb_settings.FUNCTIONAL_EXIT.PREBATTLE)

    def __repr__(self):
        return 'JoinCompanyCtx(prbID = {0:n}, waitingID = {1:>s})'.format(self.getID(), self.getWaitingID())


class LeavePrbCtx(_PrbEntryCtx):

    def __init__(self, waitingID = '', funcExit = prb_settings.FUNCTIONAL_EXIT.NO_FUNC, guiExit = prb_settings.GUI_EXIT.HANGAR):
        super(LeavePrbCtx, self).__init__(waitingID, funcExit=funcExit, guiExit=guiExit)

    def __repr__(self):
        return 'LeavePrbCtx(prbID = {0:n}, prbType = {1:>s}, waitingID = {2:>s}, exit = {3!r:s}/{4!r:s})'.format(self.getID(), self.getPrbTypeName(), self.getWaitingID(), self.getFuncExit(), self.getGuiExit())

    def getRequestType(self):
        return _REQUEST_TYPE.LEAVE

    def getID(self):
        return getPrebattleID()


class JoinBattleSessionCtx(_JoinPrbCtx):

    def __init__(self, prbID, prbType, waitingID):
        super(JoinBattleSessionCtx, self).__init__(prbID, prbType, waitingID, prb_settings.FUNCTIONAL_EXIT.PREBATTLE)

    def __repr__(self):
        return 'JoinBattleSessionCtx(prbID = {0:n}, type = {1:n}, waitingID = {2:>s})'.format(self.getID(), self.getPrbType(), self.getWaitingID())


class AssignPrbCtx(_PrbRequestCtx):

    def __init__(self, pID, roster, waitingID = ''):
        super(AssignPrbCtx, self).__init__(waitingID)
        self.__pID = pID
        self.__roster = roster

    def __repr__(self):
        return 'AssignPrbCtx(pID = {0:n}, roster = 0x{1:X}, prbType = {2:>s}, waitingID = {3:>s})'.format(self.__pID, self.__roster, self.getPrbTypeName(), self.getWaitingID())

    def getPlayerID(self):
        return self.__pID

    def getRoster(self):
        return self.__roster

    def getRequestType(self):
        return _REQUEST_TYPE.ASSIGN


class SetTeamStateCtx(_PrbRequestCtx):

    def __init__(self, team, isReadyState, waitingID = '', isForced = True, gamePlayMask = 0):
        super(SetTeamStateCtx, self).__init__(waitingID)
        self.__team = team
        self.__isReadyState = isReadyState
        self.__isForced = isForced
        self.__gamePlayMask = gamePlayMask

    def __repr__(self):
        return 'SetTeamStateCtx(team = {0:n}, isReadyState = {1!r:s}, waitingID = {3:>s}, isForced = {4!r:s}, gamePlayMask = {5:n})'.format(self.__team, self.__isReadyState, self.getPrbTypeName(), self.getWaitingID(), self.__isForced, self.__gamePlayMask)

    def getTeam(self):
        return self.__team

    def isReadyState(self):
        return self.__isReadyState

    def isForced(self):
        return self.__isForced

    def getGamePlayMask(self):
        return self.__gamePlayMask

    def getRequestType(self):
        return _REQUEST_TYPE.SET_TEAM_STATE


class SetPlayerStateCtx(_PrbRequestCtx):

    def __init__(self, isReadyState, waitingID = ''):
        super(SetPlayerStateCtx, self).__init__(waitingID)
        self.__isReadyState = isReadyState

    def __repr__(self):
        return 'SetPlayerStateCtx(vInventoryID = {0:n}, isReadyState = {1!r:s}, waitingID = {2:>s})'.format(self.getVehicleInventoryID(), self.__isReadyState, self.getWaitingID())

    def doVehicleValidation(self):
        return True

    def isReadyState(self):
        return self.__isReadyState

    def getRequestType(self):
        return _REQUEST_TYPE.SET_PLAYER_STATE

    def getVehicleInventoryID(self):
        return g_currentVehicle.invID


class SwapTeamsCtx(_PrbRequestCtx):

    def __repr__(self):
        return 'SwapTeamsCtx(waitingID = {0:>s})'.format(self.getWaitingID())

    def getRequestType(self):
        return _REQUEST_TYPE.SWAP_TEAMS


class ChangeArenaVoipCtx(_PrbRequestCtx):

    def __init__(self, channels, waitingID = ''):
        super(ChangeArenaVoipCtx, self).__init__(waitingID)
        self.__channels = int(channels)

    def __repr__(self):
        return 'ChangeArenaVoipCtx(channels = {0:n}, waitingID = {1:>s})'.format(self.__channels, self.getWaitingID())

    def getChannels(self):
        return self.__channels

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_ARENA_VOIP


class SetPlayerObserverStateCtx(SetPlayerStateCtx):

    def __init__(self, isObserver, isReadyState, waitingID = ''):
        super(SetPlayerObserverStateCtx, self).__init__(isReadyState, waitingID)
        self.__isObserver = isObserver

    def __repr__(self):
        return 'ChangeUserStatus(isObserver = {0:n}, waitingID = {1:>s})'.format(self.__isObserver, self.getWaitingID())

    def doVehicleValidation(self):
        return False

    def isObserver(self):
        return self.__isObserver

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_USER_STATUS

    def getVehicleInventoryID(self):
        return OBSERVER_VEH_INVENTORY_ID


class ChangeOpenedCtx(_PrbRequestCtx):

    def __init__(self, isOpened, waitingID = ''):
        super(ChangeOpenedCtx, self).__init__(waitingID)
        self.__isOpened = isOpened

    def __repr__(self):
        return 'ChangeOpenedCtx(isOpened = {0!r:s}, waitingID = {1:>s})'.format(self.__isOpened, self.getWaitingID())

    def isOpened(self):
        return self.__isOpened

    def isOpenedChanged(self, settings):
        return self.__isOpened != settings[prb_settings.PREBATTLE_SETTING_NAME.IS_OPENED]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_OPENED


class ChangeCommentCtx(_PrbRequestCtx):

    def __init__(self, comment, waitingID = ''):
        super(ChangeCommentCtx, self).__init__(waitingID)
        self.__comment = truncate_utf8(comment, PREBATTLE_COMMENT_MAX_LENGTH)

    def __repr__(self):
        return 'ChangeCommentCtx(comment = {0:>s}, waitingID = {1:>s})'.format(self.__comment, self.getWaitingID())

    def getComment(self):
        return self.__comment

    def isCommentChanged(self, settings):
        return self.__comment != settings[prb_settings.PREBATTLE_SETTING_NAME.COMMENT]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_COMMENT


class ChangeDivisionCtx(_PrbRequestCtx):

    def __init__(self, division, waitingID = ''):
        super(ChangeDivisionCtx, self).__init__(waitingID)
        self.__division = int(division)

    def __repr__(self):
        return 'ChangeArenaVoipCtx(division = {0:n}, waitingID = {1:>s})'.format(self.__division, self.getWaitingID())

    def getDivision(self):
        return self.__division

    def isDivisionChanged(self, settings):
        return self.__division != settings[prb_settings.PREBATTLE_SETTING_NAME.DIVISION]

    def getRequestType(self):
        return _REQUEST_TYPE.CHANGE_DIVISION


class KickPlayerCtx(_PrbRequestCtx):

    def __init__(self, pID, waitingID = ''):
        super(KickPlayerCtx, self).__init__(waitingID)
        self.__pID = pID

    def __repr__(self):
        return 'KickPlayerCtx(pID = {0:n}, waitingID = {1:>s})'.format(self.__pID, self.getWaitingID())

    def getPlayerID(self):
        return self.__pID

    def getRequestType(self):
        return _REQUEST_TYPE.KICK


class RequestCompaniesCtx(object):
    __slots__ = ('isNotInBattle', 'division', 'creatorMask')

    def __init__(self, isNotInBattle = False, division = 0, creatorMask = ''):
        super(RequestCompaniesCtx, self).__init__()
        self.isNotInBattle = isNotInBattle
        self.creatorMask = creatorMask
        if division in PREBATTLE_COMPANY_DIVISION.RANGE:
            self.division = division
        else:
            self.division = 0

    def __repr__(self):
        return 'RequestCompaniesCtx(isNotInBattle = {0!r:s}, division = {1:n}, creatorMask = {2:>s})'.format(self.isNotInBattle, self.division, self.creatorMask)

    def byDivision(self):
        return self.division in PREBATTLE_COMPANY_DIVISION.RANGE

    def byName(self):
        return self.creatorMask is not None and len(self.creatorMask)


class OpenPrbListCtx(_PrbRequestCtx):

    def __init__(self, prbType, waitingID = ''):
        super(OpenPrbListCtx, self).__init__(waitingID)
        self.__prbType = prbType

    def getPrbType(self):
        return self.__prbType


__all__ = ('TeamSettingsCtx', 'TrainingSettingsCtx', 'CompanySettingsCtx', 'SquadSettingsCtx', 'JoinTrainingCtx', 'JoinCompanyCtx', 'LeavePrbCtx', 'AssignPrbCtx', 'SetTeamStateCtx', 'SetPlayerStateCtx', 'SwapTeamsCtx', 'ChangeOpenedCtx', 'ChangeCommentCtx', 'ChangeDivisionCtx', 'ChangeArenaVoipCtx', 'KickPlayerCtx', 'RequestCompaniesCtx', 'OpenPrbListCtx')
