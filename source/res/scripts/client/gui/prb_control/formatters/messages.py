# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/formatters/messages.py
from CurrentVehicle import g_currentVehicle
from constants import JOIN_FAILURE_NAMES, KICK_REASON_NAMES, PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control import prb_getters
from gui.prb_control.settings import PREBATTLE_RESTRICTION, CTRL_ENTITY_TYPE
from gui.prb_control.settings import UNIT_ERROR_NAMES, UNIT_BROWSER_ERROR_NAMES
from gui.prb_control.settings import UNIT_ERRORS_TRANSLATE_AS_WARNINGS
from helpers import i18n
from prebattle_shared import LIMIT_DEFAULTS, decodeRoster

def getJoinFailureMessage(errorCode):
    if errorCode in JOIN_FAILURE_NAMES:
        error = JOIN_FAILURE_NAMES[errorCode]
    else:
        error = errorCode
    return i18n.makeString('#system_messages:arena_start_errors/join/%s' % error)


def getKickReasonMessage(reasonCode):
    if reasonCode in KICK_REASON_NAMES:
        reason = KICK_REASON_NAMES[reasonCode]
    else:
        reason = reasonCode
        LOG_ERROR('Invalid sub key %s for localization #system_messages:arena_start_errors/kick/' % reason)
    return i18n.makeString('#system_messages:arena_start_errors/kick/%s' % reason)


def getPrbKickedFromQueueMessage(prbTypeName):
    guiName = prbTypeName.lower()
    if guiName != 'squad':
        guiName = 'default'
    return i18n.makeString('#system_messages:prebattle_start_failed/kickedFromQueue/{0:>s}'.format(guiName))


def getVehicleNotPresentMessage():
    return i18n.makeString('#system_messages:prebattle/vehicleInvalid/no_selectedVehicle')


def getVehicleNotReadyMessage():
    return i18n.makeString('#system_messages:prebattle/vehicleInvalid/no_readyVehicle')


def getVehicleNotSupportedMessage():
    return i18n.makeString('#system_messages:prebattle/vehicleInvalid/vehicleNotSupported')


def getClassLimitMessage4Vehicle(teamLimits):
    classesList = [ i18n.makeString('#menu:classes/%s' % clazz) for clazz in teamLimits['classes'] ]
    return i18n.makeString('#system_messages:prebattle/vehicleInvalid/limits/classes') % ', '.join(classesList)


def getNationLimitMessage4Vehicle(teamLimits):
    nationsList = [ i18n.makeString('#menu:nations/%s' % nation) for nation in teamLimits['nations'] ]
    return i18n.makeString('#system_messages:prebattle/vehicleInvalid/limits/nations') % ', '.join(nationsList)


def getLevelLimitMessage4Vehicle(teamLimits):
    minLevel, maxLevel = prb_getters.getLevelLimits(teamLimits)
    return i18n.makeString('#system_messages:prebattle/vehicleInvalid/limits/level', minLevel, maxLevel)


def getClassLevelLimitMessage4Vehicle(teamLimits):
    minLevel, maxLevel = prb_getters.getClassLevelLimits(teamLimits, g_currentVehicle.item.type)
    return i18n.makeString('#system_messages:prebattle/vehicleInvalid/limits/level', minLevel, maxLevel)


def getMinCountLimitMessage4Team(teamLimits):
    return i18n.makeString('#system_messages:prebattle/teamInvalid/limit/minCount', minCount=teamLimits['minCount'])


def getTotalLevelLimitMessage4Team(teamLimits):
    minTotalLevel, maxTotalLevel = prb_getters.getTotalLevelLimits(teamLimits)
    return i18n.makeString('#system_messages:prebattle/teamInvalid/limit/totalLevel', minTotalLevel=minTotalLevel, maxTotalLevel=maxTotalLevel)


def getLevelLimitMessage4Team(teamLimits):
    minLevel, maxLevel = prb_getters.getLevelLimits(teamLimits)
    return i18n.makeString('#system_messages:prebattle/teamInvalid/limits/level', minLevel=minLevel, maxLevel=maxLevel)


def getRotationVehicleIsLockedMessage():
    return i18n.makeString('#system_messages:rotation/vehicleIsLocked')


_INVALID_VEHICLE_STATE = {PREBATTLE_RESTRICTION.VEHICLE_NOT_PRESENT: getVehicleNotPresentMessage,
 PREBATTLE_RESTRICTION.VEHICLE_NOT_READY: getVehicleNotReadyMessage,
 PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED: getVehicleNotSupportedMessage,
 PREBATTLE_RESTRICTION.VEHICLE_ROTATION_GROUP_LOCKED: getRotationVehicleIsLockedMessage}
_INVALID_VEHICLE_IN_TEAM = {PREBATTLE_RESTRICTION.LIMIT_CLASSES: getClassLimitMessage4Vehicle,
 PREBATTLE_RESTRICTION.LIMIT_NATIONS: getNationLimitMessage4Vehicle,
 PREBATTLE_RESTRICTION.LIMIT_LEVEL: getLevelLimitMessage4Vehicle,
 PREBATTLE_RESTRICTION.LIMIT_CLASS_LEVEL: getClassLevelLimitMessage4Vehicle}
_INVALID_TEAM = {PREBATTLE_RESTRICTION.LIMIT_MIN_COUNT: getMinCountLimitMessage4Team,
 PREBATTLE_RESTRICTION.LIMIT_TOTAL_LEVEL: getTotalLevelLimitMessage4Team,
 PREBATTLE_RESTRICTION.LIMIT_LEVEL: getLevelLimitMessage4Team}

def getInvalidTeamMessage(reason, entity=None):
    if reason in PREBATTLE_RESTRICTION.SERVER_LIMITS:
        if reason in _INVALID_TEAM:
            if entity:
                teamLimits = entity.getSettings().getTeamLimits(entity.getPlayerTeam())
            else:
                LOG_ERROR('Entity is not defined')
                teamLimits = LIMIT_DEFAULTS
            message = _INVALID_TEAM[reason](teamLimits)
        else:
            message = i18n.makeString('#system_messages:prebattle/teamInvalid/{0:>s}'.format(reason))
    else:
        LOG_ERROR('Reason can not be converted', reason)
        message = reason
    return message


def getInvalidTeamServerMessage(errStr, entity=None):
    return i18n.makeString(SYSTEM_MESSAGES.PREBATTLE_TEAMINVALID_EVENT_BATTLE) if errStr in ('INVALID_EVENT_TEAM', 'EVENT_DISABLED') else None


def getInvalidVehicleMessage(reason, entity=None):
    if reason in _INVALID_VEHICLE_STATE:
        message = _INVALID_VEHICLE_STATE[reason]()
    elif reason in PREBATTLE_RESTRICTION.SERVER_LIMITS:
        if reason in _INVALID_VEHICLE_IN_TEAM:
            if entity:
                teamLimits = entity.getSettings().getTeamLimits(entity.getPlayerTeam())
            else:
                LOG_ERROR('Entity is not defined')
                teamLimits = LIMIT_DEFAULTS
            message = _INVALID_VEHICLE_IN_TEAM[reason](teamLimits)
        else:
            message = i18n.makeString('#system_messages:prebattle/vehicleInvalid/%s' % reason)
    else:
        LOG_ERROR('Reason can not be converted', reason)
        message = reason
    return message


def getPlayerStateChangedMessage(prbName, playerInfo):
    if playerInfo.isOffline():
        key = '#system_messages:{0:>s}/memberOffline'.format(prbName)
    elif playerInfo.isReady():
        key = '#system_messages:{0:>s}/memberReady'.format(prbName)
    else:
        key = '#system_messages:{0:>s}/memberNotReady'.format(prbName)
    return i18n.makeString(key, playerInfo.getFullName())


def getPlayerAddedMessage(prbName, playerInfo):
    return i18n.makeString('#system_messages:{0:>s}/memberJoined'.format(prbName), playerInfo.getFullName())


def getPlayerRemovedMessage(prbName, playerInfo):
    return i18n.makeString('#system_messages:{0:>s}/memberLeave'.format(prbName), playerInfo.getFullName())


def getPlayerAssignFlagChanged(actorInfo, playerInfo):
    _, assigned = decodeRoster(playerInfo.roster)
    if assigned:
        key = '#system_messages:memberRosterChangedMain'
    else:
        key = '#system_messages:memberRosterChangedSecond'
    return i18n.makeString(key, actorInfo.getFullName(), playerInfo.getFullName())


def getUnitMessage(errorCode, errorString):
    errorName = UNIT_ERROR_NAMES[errorCode]
    if errorCode in UNIT_ERRORS_TRANSLATE_AS_WARNINGS:
        msgType = SystemMessages.SM_TYPE.Warning
        errorKey = SYSTEM_MESSAGES.unit_warnings(errorName)
    else:
        msgType = SystemMessages.SM_TYPE.Error
        errorKey = SYSTEM_MESSAGES.unit_errors(errorName)
    if errorKey is not None:
        msgBody = i18n.makeString(errorKey)
    else:
        msgBody = errorName + '\n' + errorString
    return (msgType, msgBody)


def getUnitKickedReasonMessage(reasonStr):
    return getUnitWarningMessage(reasonStr)


def getUnitWarningMessage(key):
    return i18n.makeString(SYSTEM_MESSAGES.unit_warnings(key))


def getUnitBrowserMessage(errorCode, errorString):
    errorName = UNIT_BROWSER_ERROR_NAMES[errorCode]
    errorKey = SYSTEM_MESSAGES.unitbrowser_errors(errorName)
    if errorKey is not None:
        msgBody = i18n.makeString(errorKey)
    else:
        msgBody = errorName + '\n' + errorString
    return (SystemMessages.SM_TYPE.Error, msgBody)


def getUnitPlayerNotification(key, pInfo):
    return i18n.makeString(SYSTEM_MESSAGES.unit_notification(key), userName=pInfo.getFullName())


def makeEntityI18nKey(ctrlType, entityType, prefix):
    if ctrlType in (CTRL_ENTITY_TYPE.LEGACY, CTRL_ENTITY_TYPE.UNIT):
        if entityType in PREBATTLE_TYPE.SQUAD_PREBATTLES:
            name = 'squad'
        else:
            name = 'rally'
    elif ctrlType == CTRL_ENTITY_TYPE.PREQUEUE and entityType == QUEUE_TYPE.SANDBOX:
        name = 'sandBox'
    else:
        name = 'rally'
    return '{0}/{1}'.format(name, prefix)


def getLeaveDisabledMessage(ctrlType, entityType):
    return '#system_messages:{0}'.format(makeEntityI18nKey(ctrlType, entityType, 'leaveDisabled'))
