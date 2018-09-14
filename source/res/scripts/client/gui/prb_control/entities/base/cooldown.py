# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/cooldown.py
from constants import JOIN_FAILURE, REQUEST_COOLDOWN
from debug_utils import LOG_WARNING
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES as I18N_SYSTEM_MESSAGES
from gui.prb_control.formatters import messages
from gui.prb_control.settings import REQUEST_TYPE_NAMES, REQUEST_TYPE
from gui.shared import rq_cooldown as _rqc
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE
from helpers import i18n

def validatePrbCreationCooldown():
    """
    Validates prebattle entity creation is in cooldown
    Returns:
        is creation in cooldown
    """
    if _rqc.isRequestInCoolDown(REQUEST_SCOPE.PRB_CONTROL, REQUEST_TYPE.CREATE):
        SystemMessages.pushMessage(messages.getJoinFailureMessage(JOIN_FAILURE.COOLDOWN), type=SystemMessages.SM_TYPE.Error)
        return True
    return False


def setPrbCreationCooldown():
    """
    Sets prebattle creation is in cooldown.
    """
    _rqc.setRequestCoolDown(REQUEST_SCOPE.PRB_CONTROL, REQUEST_TYPE.CREATE, coolDown=REQUEST_COOLDOWN.PREBATTLE_CREATION)


def getPrbRequestCoolDown(rqTypeID):
    """
    Gets cooldown time for give request type.
    Args:
        rqTypeID: request type
    
    Returns:
        cooldown time left
    """
    return _rqc.getRequestCoolDown(REQUEST_SCOPE.PRB_CONTROL, rqTypeID)


class PrbCooldownManager(RequestCooldownManager):
    """
    Manager for prebattle request cooldowns.
    """

    def __init__(self):
        super(PrbCooldownManager, self).__init__(REQUEST_SCOPE.PRB_CONTROL)

    def lookupName(self, rqTypeID):
        """
        Name for prebattle request action.
        Args:
            rqTypeID: request type identifier
        
        Returns:
            name for prebattle request
        """
        requestName = rqTypeID
        if rqTypeID in REQUEST_TYPE_NAMES:
            requestName = I18N_SYSTEM_MESSAGES.prebattle_request_name(REQUEST_TYPE_NAMES[rqTypeID])
            requestName = i18n.makeString(requestName)
        else:
            LOG_WARNING('Request type is not found', rqTypeID)
        return requestName

    def getDefaultCoolDown(self):
        """
        Getter for default cooldown.
        """
        return _rqc.DEFAULT_COOLDOWN_TO_REQUEST
