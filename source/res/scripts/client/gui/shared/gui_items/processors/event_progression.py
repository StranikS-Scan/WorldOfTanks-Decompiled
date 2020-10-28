# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/event_progression.py
import logging
import typing
import BigWorld
from gui.SystemMessages import SM_TYPE
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeI18nSuccess
from helpers import time_utils, dependency
from messenger.formatters import TimeFormatter
from skeletons.gui.game_control import IEventProgressionController
_logger = logging.getLogger(__name__)

class EventProgressionBuyRewardVehicle(Processor):
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def __init__(self, vehicle):
        self.__vehicle = vehicle
        super(EventProgressionBuyRewardVehicle, self).__init__((RewardPointsValidator(self.__vehicle),))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='event_progression_buy_vehicle/server_error', type=SM_TYPE.Error, **self.__getMsgCtx())

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='event_progression_buy_vehicle/buy', type=SM_TYPE.FrontlineVehicleRewards, **self.__getMsgCtx())

    def _request(self, callback):
        _logger.debug('Make server request to buy event progression vehicle, vehicleIntCD: %s', self.__vehicle.intCD)
        BigWorld.player().epicMetaGame.buyFrontlineRewardVehicle(self.__vehicle.intCD, lambda code, errCode: self._response(code, callback, errStr=errCode))

    def __getMsgCtx(self):
        return {'veh_name': self.__vehicle.shortUserName,
         'count': self.__eventProgression.getRewardVehiclePrice(self.__vehicle.intCD),
         'date': self.__formatTime()}

    @staticmethod
    def __formatTime():
        operationTime = time_utils.getCurrentLocalServerTimestamp()
        return TimeFormatter.getLongDatetimeFormat(operationTime) if operationTime else 'N/A'


class RewardPointsValidator(plugins.SyncValidator):
    __eventProgression = dependency.descriptor(IEventProgressionController)

    def __init__(self, vehicle):
        super(RewardPointsValidator, self).__init__()
        self.__vehicle = vehicle

    def _validate(self):
        storedPoints = self.__eventProgression.actualRewardPoints
        price = self.__eventProgression.getRewardVehiclePrice(self.__vehicle.intCD)
        return plugins.makeSuccess() if price and storedPoints >= price else plugins.makeError('ne_points')
