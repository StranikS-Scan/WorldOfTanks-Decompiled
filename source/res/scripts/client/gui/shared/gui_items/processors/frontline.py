# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/frontline.py
import logging
import typing
import BigWorld
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getEpicGamePlayerPrestigePoints
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getFrontlineRewardVehPrice
from gui.SystemMessages import SM_TYPE
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeI18nSuccess
from helpers import time_utils
from messenger.formatters import TimeFormatter
_logger = logging.getLogger(__name__)

class FrontlineBuyRewardVehicle(Processor):

    def __init__(self, vehicle):
        self.__vehicle = vehicle
        super(FrontlineBuyRewardVehicle, self).__init__((PrestigePointsValidator(self.__vehicle),))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='frontline_buy_vehicle/server_error', type=SM_TYPE.Error, **self.__getMsgCtx())

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='frontline_buy_vehicle/buy', type=SM_TYPE.FrontlineVehicleRewards, **self.__getMsgCtx())

    def _request(self, callback):
        _logger.debug('Make server request to buy frontline reward vehicle, vehicleIntCD: %s', self.__vehicle.intCD)
        BigWorld.player().epicMetaGame.buyFrontlineRewardVehicle(self.__vehicle.intCD, lambda code, errCode: self._response(code, callback, errStr=errCode))

    def __getMsgCtx(self):
        return {'veh_name': self.__vehicle.shortUserName,
         'count': getFrontlineRewardVehPrice(self.__vehicle.intCD),
         'date': self.__formatTime()}

    @staticmethod
    def __formatTime():
        operationTime = time_utils.getServerRegionalTime()
        return TimeFormatter.getLongDatetimeFormat(operationTime) if operationTime else 'N/A'


class PrestigePointsValidator(plugins.SyncValidator):

    def __init__(self, vehicle):
        super(PrestigePointsValidator, self).__init__()
        self.__vehicle = vehicle

    def _validate(self):
        storedPoints = getEpicGamePlayerPrestigePoints()
        price = getFrontlineRewardVehPrice(self.__vehicle.intCD)
        return plugins.makeSuccess() if price and storedPoints >= price else plugins.makeError('ne_points')
