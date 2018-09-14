# Embedded file name: scripts/client/gui/shared/rq_cooldown.py
import BigWorld
import math
from debug_utils import LOG_WARNING
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES as I18N_SYSTEM_MESSAGES
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import i18n
DEFAULT_COOLDOWN_TO_REQUEST = 5.0

class REQUEST_SCOPE(object):
    GLOBAL = 0
    PRB_CONTROL = 1
    FORTIFICATION = 2
    BW_CHAT2 = 3


_REQUEST_SCOPE_TO_EVENT = {REQUEST_SCOPE.GLOBAL: events.CoolDownEvent.GLOBAL,
 REQUEST_SCOPE.PRB_CONTROL: events.CoolDownEvent.PREBATTLE,
 REQUEST_SCOPE.FORTIFICATION: events.CoolDownEvent.FORTIFICATION,
 REQUEST_SCOPE.BW_CHAT2: events.CoolDownEvent.BW_CHAT2}
_g_coolDowns = {}

def isRequestInCoolDown(scopeID, rqTypeID):
    global _g_coolDowns
    result = False
    uniqueID = (scopeID, rqTypeID)
    if uniqueID in _g_coolDowns:
        result = _g_coolDowns[uniqueID] > BigWorld.time()
    return result


def getRequestCoolDown(scopeID, rqTypeID):
    result = 0
    uniqueID = (scopeID, rqTypeID)
    if uniqueID in _g_coolDowns:
        result = max(0, math.ceil(_g_coolDowns[uniqueID] - BigWorld.time()))
    return result


def getRequestInCoolDownMessage(requestName, coolDown = DEFAULT_COOLDOWN_TO_REQUEST):
    return i18n.makeString(I18N_SYSTEM_MESSAGES.REQUEST_ISINCOOLDOWN, request=requestName, coolDown=coolDown)


def setRequestCoolDown(scopeID, rqTypeID, coolDown = DEFAULT_COOLDOWN_TO_REQUEST):
    _g_coolDowns[scopeID, rqTypeID] = BigWorld.time() + coolDown
    fireCoolDownEvent(scopeID, rqTypeID, coolDown=coolDown)


def adjustRequestCoolDown(scopeID, rqTypeID, coolDown = DEFAULT_COOLDOWN_TO_REQUEST):
    _g_coolDowns[scopeID, rqTypeID] = BigWorld.time() + coolDown


def fireCoolDownEvent(scopeID, rqTypeID, coolDown = DEFAULT_COOLDOWN_TO_REQUEST):
    if scopeID not in _REQUEST_SCOPE_TO_EVENT:
        LOG_WARNING('Type of event is not found, it is ignored', scopeID)
        return
    g_eventBus.handleEvent(events.CoolDownEvent(_REQUEST_SCOPE_TO_EVENT[scopeID], rqTypeID, coolDown), scope=EVENT_BUS_SCOPE.LOBBY)


class RequestCooldownManager(object):

    def __init__(self, scopeID):
        super(RequestCooldownManager, self).__init__()
        self._scopeID = scopeID

    def lookupName(self, rqTypeID):
        raise NotImplementedError

    def getDefaultCoolDown(self):
        raise NotImplementedError

    def isInProcess(self, rqTypeID):
        return isRequestInCoolDown(self._scopeID, rqTypeID)

    def getTime(self, rqTypeID):
        return getRequestCoolDown(self._scopeID, rqTypeID)

    def getCoolDownMessage(self, rqTypeID, coolDown = None):
        requestName = self.lookupName(rqTypeID)
        if coolDown is None:
            coolDown = self.getDefaultCoolDown()
        return i18n.makeString(I18N_SYSTEM_MESSAGES.REQUEST_ISINCOOLDOWN, request=requestName, coolDown=BigWorld.wg_getNiceNumberFormat(coolDown))

    def process(self, rqTypeID, coolDown = None):
        if coolDown is None:
            coolDown = self.getDefaultCoolDown()
        setRequestCoolDown(self._scopeID, rqTypeID, coolDown)
        return

    def adjust(self, rqTypeID, coolDown = None):
        if coolDown is None:
            coolDown = self.getDefaultCoolDown()
        adjustRequestCoolDown(self._scopeID, rqTypeID, coolDown)
        return

    def reset(self, rqTypeID):
        setRequestCoolDown(self._scopeID, rqTypeID, -1)

    def validate(self, rqTypeID, coolDown = None):
        result = False
        if self.isInProcess(rqTypeID):
            SystemMessages.pushMessage(self.getCoolDownMessage(rqTypeID, coolDown), type=SystemMessages.SM_TYPE.Error)
            result = True
        return result

    def fireEvent(self, rqTypeID, coolDown = None):
        if coolDown is None:
            coolDown = self.getDefaultCoolDown()
        fireCoolDownEvent(self._scopeID, rqTypeID, coolDown)
        return
