# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarCommendations.py
import logging
from typing import TYPE_CHECKING
import AccountCommands
from Event import Event
from constants import CommendationsState
from script_component.DynamicScriptComponent import DynamicScriptComponent
if TYPE_CHECKING:
    from typing import Dict, List
    from commendations_common.CommendationHelpers import CommendationStateType, CommendationsSource
_logger = logging.getLogger(__name__)

class AvatarCommendations(DynamicScriptComponent):

    def __init__(self):
        super(AvatarCommendations, self).__init__()
        _logger.debug('CommendationsController initialised!')
        self._messageStateMap = {}
        self.onStateUpdate = Event()

    def onDestroy(self):
        super(AvatarCommendations, self).onDestroy()
        self.onStateUpdate.clear()

    def set_commendationsState(self, oldState):
        self.updateMessageStateMap()

    def setNested_commendationsState(self, path, oldState):
        self.updateMessageStateMap()

    def updateMessageStateMap(self):
        self._messageStateMap = {state['vehID']:CommendationsState(state['messageState']) for state in self.commendationsState}
        self.onStateUpdate()

    def getMessageStateForVehID(self, vehID):
        return self._messageStateMap.get(vehID, CommendationsState.UNSENT)

    def sendCommendation(self, recipientID, source):
        self.cell.sendCommendation(recipientID, source)

    def clearMessageState(self, callback=None):
        if callback is None:

            def __defaultLogger(resultID, errorCode):
                _logger.debug('Action performed: "activateGoodie" resultID=%s, errorCode=%s', resultID, errorCode)

            callback = __defaultLogger
        self.entity._doCmdNoArgs(AccountCommands.CMD_CLEAR_COMMENDATIONS_MESSAGE_STATE, lambda requestID, resultID, errorCode, ext=None: callback(resultID, errorCode))
        return
