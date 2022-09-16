# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/general/controller.py
import typing
from BWUtil import AsyncReturn
import wg_async
from gui.platform.base.statuses.controller_mixin import StatusesMixin
from gui.platform.wgnp.base.controller import WGNPRequestController
from gui.platform.wgnp.general.request import AccountCountryParams
from gui.platform.wgnp.general.statuses import GeneralAccountCountryStatus, createAccountCountryStatusFromResponse
from skeletons.gui.platform.wgnp_controllers import IWGNPGeneralRequestController
ACCOUNT_COUNTRY_CONTEXT = '<country>'

class WGNPGeneralRequestController(StatusesMixin, WGNPRequestController, IWGNPGeneralRequestController):

    @wg_async.wg_async
    def getAccountCountry(self, waitingID=None):
        status = self._getStatus(ACCOUNT_COUNTRY_CONTEXT)
        self._logger.debug('Getting account country from cache=%s, waitingID=%s.', status, waitingID)
        if status.isUndefined:
            response = yield self._request(AccountCountryParams(self.settings.getUrl()), waitingID=waitingID)
            status = createAccountCountryStatusFromResponse(response)
            self._updateStatus(status)
        raise AsyncReturn(status)
