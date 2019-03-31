# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/AccountPrebattle.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld, constants
from items import vehicles
from adisp import process, async
from debug_utils import LOG_ERROR
from gui import SystemMessages
from PlayerEvents import g_playerEvents

class AccountPrebattle:
    ROSTERS = (1, 17, 2, 18)
    ROSTERS2TEAMS = {1: (1, False),
     17: (1, True),
     2: (2, False),
     18: (2, True)}
    SUQAD_ROSTERID = 1
    TEAM_ROSTERSID = (1, 17)

    @staticmethod
    @async
    @process
    def create(type, callback, isOpen=True, comment='', arenaTypeID=None, roundLength=0):
        """
        Create prebbattle with specified parameters
        Example:
                success = yield AccountPrebbatle.create(constants.PREBATTLE_TYPE.SQUAD)
                if success:
                        #do somthing
        
        @param type: integer - prebattle type from constants.PREBATTLE_TYPE
        @param isOpen: boolean - (for COMPANY and TRAINING)True:everybody can join otherwise by invites only
        @param comment: string - (for COMPANY and TRAINING) user defined description
        @param arenaTypeID: integer - for TRAINING user defined arena
        @param roundLength: integer - for TRAINING user defined round legth in seconds
        """

        def onPrebattleJoined():
            g_playerEvents.onPrebattleJoined -= onPrebattleJoined
            g_playerEvents.onPrebattleJoinFailure -= onPrebattleJoinFailure
            callback(True)

        def onPrebattleJoinFailure(errorCode):
            g_playerEvents.onPrebattleJoined -= onPrebattleJoined
            g_playerEvents.onPrebattleJoinFailure -= onPrebattleJoinFailure
            message = '#system_messages:arena_start_errors/join/%s' % constants.JOIN_FAILURE_NAMES[errorCode]
            SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Error)
            callback(False)

        exitComplete = yield AccountPrebattle.__exitConfirmation()
        if exitComplete:
            g_playerEvents.onPrebattleJoined += onPrebattleJoined
            g_playerEvents.onPrebattleJoinFailure += onPrebattleJoinFailure
            if type == constants.PREBATTLE_TYPE.SQUAD:
                BigWorld.player().prb_createSquad()
            elif type == constants.PREBATTLE_TYPE.COMPANY:
                BigWorld.player().prb_createCompany(isOpen, comment)
            elif type == constants.PREBATTLE_TYPE.TRAINING:
                BigWorld.player().prb_createTraining(arenaTypeID, roundLength, isOpened, comment)
            else:
                LOG_ERROR('Unknown prebattle type')
                callback(False)
        else:
            callback(False)

    @staticmethod
    @async
    @process
    def join(prebattleID, callback):
        """
        Join prebbattle
        Example:
                success = yield AccountPrebbatle.join(123)
                if success:
                        #do somthing
        
        @param prebattleID: integer - prebattle id to join
        """

        def onPrebattleJoined():
            g_playerEvents.onPrebattleJoined -= onPrebattleJoined
            g_playerEvents.onPrebattleJoinFailure -= onPrebattleJoinFailure
            callback(True)

        def onPrebattleJoinFailure(errorCode):
            g_playerEvents.onPrebattleJoined -= onPrebattleJoined
            g_playerEvents.onPrebattleJoinFailure -= onPrebattleJoinFailure
            message = '#system_messages:arena_start_errors/join/%s' % constants.JOIN_FAILURE_NAMES[errorCode]
            SystemMessages.pushI18nMessage(message, type=SystemMessages.SM_TYPE.Error)
            callback(False)

        exitComplete = yield AccountPrebattle.__exitConfirmation()
        if exitComplete:
            BigWorld.player().prb_join(prebattleID)
        else:
            callback(False)

    @staticmethod
    @async
    def exit(callback):
        """
        Exit from prebattle if anny
        Example:
                success = yield AccountPrebattle.exit()
                if success:
                        #do somthing may create new prebattle
        """

        def onPrebattleLeaveResponse(errorCode):
            if errorCode < 0:
                LOG_ERROR('Server return error for prebattle leave request: responseCode=%s' % errorCode)
            callback(errorCode >= 0)

        if AccountPrebattle.get():
            BigWorld.player().prb_leave(onPrebattleLeaveResponse)
        else:
            callback(True)

    @staticmethod
    def getCurrentPlayerId():
        if BigWorld.player():
            return BigWorld.player().id

    @staticmethod
    def get():
        if hasattr(BigWorld.player(), 'prebattle'):
            return BigWorld.player().prebattle
        else:
            return None

    @staticmethod
    def isSquad():
        return AccountPrebattle.type() == constants.PREBATTLE_TYPE.SQUAD

    @staticmethod
    def isCompany():
        return AccountPrebattle.type() == constants.PREBATTLE_TYPE.COMPANY

    @staticmethod
    def isTraining():
        return AccountPrebattle.type() == constants.PREBATTLE_TYPE.TRAINING

    @staticmethod
    def isBattleSession():
        return AccountPrebattle.type() in (constants.PREBATTLE_TYPE.TOURNAMENT, constants.PREBATTLE_TYPE.CLAN)

    @staticmethod
    def isTeamReady():
        if AccountPrebattle.get() and AccountPrebattle.getMemberTeam():
            return AccountPrebattle.get().teamStates[AccountPrebattle.getMemberTeam()] in (constants.PREBATTLE_TEAM_STATE.LOCKED, constants.PREBATTLE_TEAM_STATE.READY)
        return False

    @staticmethod
    def isMemberReady(id=None):
        player = AccountPrebattle.getMember(AccountPrebattle.getCurrentPlayerId() if id is None else id)
        if player:
            return player['state'] == constants.PREBATTLE_ACCOUNT_STATE.READY
        else:
            return False

    @staticmethod
    def getMember(id):
        if AccountPrebattle.get():
            if AccountPrebattle.get().rosters:
                for roster in AccountPrebattle.ROSTERS:
                    member = AccountPrebattle.get().rosters.get(roster, {}).get(id, None)
                    if member:
                        return member

        return

    @staticmethod
    def getMemberTeam(id=None):
        roster = AccountPrebattle.getMemberRoster(id)
        return AccountPrebattle.ROSTERS2TEAMS.get(roster, (None, None))[0]

    @staticmethod
    def isMemberInKeyStaff(id=None):
        roster = AccountPrebattle.getMemberRoster(id)
        return not AccountPrebattle.ROSTERS2TEAMS.get(roster, (None, None))[1]

    @staticmethod
    def getMemberRoster(id=None):
        if AccountPrebattle.get():
            if AccountPrebattle.get().rosters:
                for roster in AccountPrebattle.ROSTERS:
                    if AccountPrebattle.get().rosters.get(roster, {}).get(AccountPrebattle.getCurrentPlayerId() if id is None else id, None):
                        return roster

        return

    @staticmethod
    def isCreator():
        member = AccountPrebattle.getMember(AccountPrebattle.getCurrentPlayerId())
        if member:
            settings = AccountPrebattle.get().settings
            if settings is None:
                return
            accRole = settings.get('roles', {}).get(member['dbID'], 0)
            if not accRole:
                accRole = settings.get('clanRoles', {}).get(member['clanDBID'], 0)
            if not accRole:
                accRole = settings.get('teamRoles', {}).get(AccountPrebattle.getMemberTeam(), 0)
            creatorRole = None
            if AccountPrebattle.isSquad():
                creatorRole = constants.PREBATTLE_ROLE.SQUAD_CREATOR
            elif AccountPrebattle.isCompany():
                creatorRole = constants.PREBATTLE_ROLE.COMPANY_CREATOR
            elif AccountPrebattle.isTraining():
                creatorRole = constants.PREBATTLE_ROLE.TRAINING_CREATOR
            elif AccountPrebattle.isBattleSession():
                if AccountPrebattle.getMemberTeam() == 1:
                    creatorRole = constants.PREBATTLE_ROLE.TEAM_READY_1
                else:
                    creatorRole = constants.PREBATTLE_ROLE.TEAM_READY_2
                return accRole & creatorRole != 0
            return accRole == creatorRole
        else:
            return False

    @staticmethod
    def type():
        if AccountPrebattle.get():
            if AccountPrebattle.get().settings:
                return AccountPrebattle.get().settings['type']
        return None

    @staticmethod
    def getBattleType():
        if AccountPrebattle.get():
            if AccountPrebattle.isSquad():
                return constants.ARENA_GUI_TYPE.RANDOM
            if AccountPrebattle.isCompany():
                return constants.ARENA_GUI_TYPE.COMPANY
            if AccountPrebattle.isTraining():
                return constants.ARENA_GUI_TYPE.TRAINING
            return constants.ARENA_GUI_TYPE.UNKNOWN
        return constants.ARENA_GUI_TYPE.RANDOM

    @staticmethod
    def getPlayersReadyStat(rosterId):
        prebattle = AccountPrebattle.get()
        notReadyCount = 0
        playerCount = 0
        limitMaxCount = 0
        haveInBattle = False
        if prebattle:
            players = prebattle.rosters.get(rosterId, {})
            playerCount = len(players)
            settings = prebattle.settings
            limitMaxCount = settings.get('limit_max_count', {}).get(rosterId, 0)
            for _, accInfo in players.iteritems():
                state = accInfo.get('state', constants.PREBATTLE_ACCOUNT_STATE.UNKNOWN)
                if not state & constants.PREBATTLE_ACCOUNT_STATE.READY:
                    notReadyCount += 1
                    if not haveInBattle and state & constants.PREBATTLE_ACCOUNT_STATE.IN_BATTLE:
                        haveInBattle = True

        return (notReadyCount,
         haveInBattle,
         playerCount,
         limitMaxCount)

    @staticmethod
    def getPrebattleLocalizedData(extraData=None):
        led = {}
        if extraData is None:
            if AccountPrebattle.get():
                if AccountPrebattle.get().settings:
                    extraData = AccountPrebattle.get().settings.get('extraData', {})
        if extraData:
            from helpers import getClientLanguage
            lng = getClientLanguage()
            ld = extraData.get('localized_data', {})
            if ld:
                if ld.get(lng, {}):
                    led = ld.get(lng, {})
                else:
                    led = ld.items()[0][1]
        return led

    @staticmethod
    def getPrebattleDescription(extraData=None):
        led = AccountPrebattle.getPrebattleLocalizedData(extraData)
        if led:
            return ': '.join([led.get('event_name', ''), led.get('session_name', '')]).strip()

    @staticmethod
    def getSettings():
        if AccountPrebattle.get():
            return AccountPrebattle.get().settings
        return {}

    @staticmethod
    def getLevelLimits():
        prbSettings = AccountPrebattle.getSettings()
        min, max = (1, 10)
        if prbSettings is not None:
            min, max = prbSettings.get('limit_level', (min, max))
        return (min, max)

    @staticmethod
    def getClassLevelLimits(classType):
        prbSettings = AccountPrebattle.getSettings()
        min, max = AccountPrebattle.getLevelLimits()
        if prbSettings is not None:
            if prbSettings.get('limit_class_level', {}).has_key(classType):
                min, max = prbSettings.get('limit_class_level', {})[classType]
        return (min, max)

    @staticmethod
    def setMemdberReady():
        notValidReason = 'no_readyVehicle'
        from CurrentVehicle import g_currentVehicle
        if g_currentVehicle.isReadyToFight():
            from prebattle_shared import isVehicleValid
            isV, notValidReason = isVehicleValid(g_currentVehicle.vehicle.descriptor, g_currentVehicle.vehicle.getShellsList(), AccountPrebattle.getSettings())
            if isV:
                BigWorld.player().prb_ready(g_currentVehicle.vehicle.inventoryId, AccountPrebattle.__onPrebattleReadyResponse)
                return
        if notValidReason in ('wrong_level', 'wrong_class_level'):
            if notValidReason == 'wrong_class_level':
                classTag = set(vehicles.VEHICLE_CLASS_TAGS.intersection(g_currentVehicle.vehicle.tags)).pop()
                minLevel, maxLevel = AccountPrebattle.getSettings().get('limit_class_level', {}).get(classTag, (0, 65535))
            else:
                minLevel, maxLevel = AccountPrebattle.getSettings().get('limit_level', (0, 65535))
            SystemMessages.pushI18nMessage('#system_messages:prebattleReady/%s' % notValidReason, minLevel, maxLevel, type=SystemMessages.SM_TYPE.Error)
            return
        SystemMessages.pushI18nMessage('#system_messages:prebattleReady/%s' % notValidReason, type=SystemMessages.SM_TYPE.Error)

    @staticmethod
    def __onPrebattleReadyResponse(code):
        import AccountCommands
        if code == AccountCommands.RES_FAILURE:
            from gui import SystemMessages
            SystemMessages.pushI18nMessage('#system_messages:prebattleReady/notSetReadyStatus', type=SystemMessages.SM_TYPE.Error)
        elif code < 0:
            from debug_utils import LOG_ERROR
            LOG_ERROR('Server return error for member ready request:  responseCode=%s' % code)

    @staticmethod
    @async
    @process
    def __exitConfirmation(callback):
        success = False
        if not AccountPrebattle.get():
            success = yield AccountPrebattle.exit()
        else:
            customMessage = '#dialogs:exitCurrentPrebattle/customMessage/%s' % constants.PREBATTLE_TYPE_NAMES[AccountPrebattle.type()]
            from gui.Scaleform.utils.functions import async_showConfirmDialog
            isConfirmedExit = yield async_showConfirmDialog('exitCurrentPrebattle', customMessage=customMessage)
            if isConfirmedExit:
                success = yield AccountPrebattle.exit()
        callback(success)
