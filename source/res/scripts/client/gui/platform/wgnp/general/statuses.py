# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/wgnp/general/statuses.py
import typing
from gui.platform.base.response import Codes
from gui.platform.base.statuses.constants import StatusTypes
from gui.platform.base.statuses.status import Status
if typing.TYPE_CHECKING:
    from gui.platform.wgnp.general.request import AccountCountryParams

class GeneralAccountCountryStatus(Status):
    __slots__ = ()

    @property
    def country(self):
        return self.data.get('country', '')


def createAccountCountryStatusFromResponse(response):
    statusType, data = StatusTypes.UNDEFINED, None
    if response.isSuccess():
        data = response.getData()
        if data:
            statusType = StatusTypes.ADDED
    else:
        data = {'error': Codes(response.code)}
    return GeneralAccountCountryStatus(statusType=statusType, data=data)
