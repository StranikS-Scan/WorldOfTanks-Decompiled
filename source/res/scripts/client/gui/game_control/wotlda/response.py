# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wotlda/response.py
import httplib
from typing import Dict, Optional, TYPE_CHECKING
from gui.game_control.wotlda.constants import LAST_UPDATE_TIMESTAMP, SupportedWotldaLoadoutType
if TYPE_CHECKING:
    from gui.shared.utils.requesters.abstract import Response

class WotldaResponse(object):

    def __init__(self, response):
        self._response = response
        self._exception = None
        return

    def getData(self):
        return self._response.getData() if self.isSuccess() else {}

    def setException(self, exception):
        self._exception = exception

    def isSuccess(self):
        return self._response.getExtraCode() == httplib.OK if self._response else False

    def isNotModified(self):
        return self._response.getExtraCode() == httplib.NOT_MODIFIED if self._response else False

    def isServiceUnavailable(self):
        return self._response.getExtraCode() == httplib.SERVICE_UNAVAILABLE if self._response else True

    def hasRequestFailed(self):
        return self._exception or not self.isSuccess() and not self.isNotModified()

    def getLoadoutsByType(self, loadoutType):
        return self.getData().get(loadoutType, {})

    def getTimestamp(self):
        return self.getData().get(LAST_UPDATE_TIMESTAMP, 0)
