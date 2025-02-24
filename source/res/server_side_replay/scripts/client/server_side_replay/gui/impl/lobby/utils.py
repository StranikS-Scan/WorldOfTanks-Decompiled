# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/lobby/utils.py
import logging
import nations
from WebBrowser import getWebCache
from adisp import adisp_async
from ..gen.view_models.views.lobby.enums import TankmanLocation
from ..gen.view_models.views.lobby.filter_toggle_group_model import ToggleGroupType
from ..gen.view_models.views.lobby.popovers.replays_filter_popover_model import VehicleSortColumn
from .filter import GRADE_PREMIUM, GRADE_ELITE, GRADE_PRIMARY
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.CallbackDelayer import CallbackDelayer
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
_logger = logging.getLogger(__name__)

def getRentCriteria():
    return REQ_CRITERIA.CUSTOM(lambda item: item.isRented and not item.isWotPlus)


def buildPopoverTankKeySortCriteria(field):
    if field == VehicleSortColumn.TIER.value:
        return REQ_CRITERIA.CUSTOM(lambda item: item.level)
    if field == VehicleSortColumn.NAME.value:
        return REQ_CRITERIA.CUSTOM(lambda item: item.searchableUserName)
    if field == VehicleSortColumn.TYPE.value:
        criteria = REQ_CRITERIA.CUSTOM(lambda item: VEHICLE_TYPES_ORDER_INDICES[item.type])
        return criteria | REQ_CRITERIA.CUSTOM(lambda item: item.isPremium)


def buildPopoverTankFilterCriteria(filters):
    criteria = ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
    criteria |= ~getRentCriteria()
    criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
    criteria |= ~REQ_CRITERIA.VEHICLE.COMP7
    criteria |= ~REQ_CRITERIA.VEHICLE.EPIC_BATTLE
    criteria |= ~REQ_CRITERIA.VEHICLE.MAPS_TRAINING
    criteria |= ~REQ_CRITERIA.VEHICLE.FUN_RANDOM
    criteria |= ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
    for field, value in filters.items():
        if not value:
            continue
        if field == ToggleGroupType.NATION.value:
            criteria |= REQ_CRITERIA.NATIONS(tuple((nations.INDICES[item] for item in value)))
        if field == ToggleGroupType.VEHICLETYPE.value and value:
            criteria |= REQ_CRITERIA.VEHICLE.CLASSES(tuple(value))
        if field == ToggleGroupType.TANKMANROLE.value and value:
            roleCriteria = REQ_CRITERIA.NONE
            for role in value:
                roleCriteria ^= REQ_CRITERIA.VEHICLE.HAS_ROLE(role)

            criteria |= roleCriteria
        if field == ToggleGroupType.VEHICLETIER.value and value:
            criteria |= REQ_CRITERIA.VEHICLE.LEVELS(tuple((int(item) for item in value)))
        if field == ToggleGroupType.VEHICLEGRADE.value and value:
            value = value - {TankmanLocation.INTANK.value, TankmanLocation.INBARRACKS.value}
            if not value:
                continue
            gradeCriteria = REQ_CRITERIA.NONE
            if GRADE_PREMIUM in value:
                gradeCriteria ^= REQ_CRITERIA.VEHICLE.PREMIUM
            if GRADE_ELITE in value:
                gradeCriteria ^= REQ_CRITERIA.CUSTOM(lambda vehicle: vehicle.isElite and not vehicle.isPremium)
            if GRADE_PRIMARY in value:
                gradeCriteria ^= REQ_CRITERIA.VEHICLE.FAVORITE
            criteria |= gradeCriteria

    return criteria


class WebReplaysHelper(object):
    __slots__ = ('__callbackMethod', '__imageUrl', '__callbackDelayer', '__webCache', '__defLocalDirPath')
    __DEFAULT_TIMEOUT = 10.0

    def __init__(self, defLocalDirPath='server_replays'):
        self.__callbackMethod = None
        self.__imageUrl = ''
        self.__callbackDelayer = CallbackDelayer()
        self.__webCache = None
        self.__defLocalDirPath = defLocalDirPath
        return

    @adisp_async
    def getRelativePath(self, imageUrl, callback=lambda x: None):
        self.__imageUrl = imageUrl
        self.__callbackMethod = callback
        self.__webCache = getWebCache()
        if self.__webCache is None:
            _logger.error('Failed to get web cache. Using empty image path.')
            self.__callbackDelayer.destroy()
            self.__callMethod('')
            return
        else:
            relativePath = self.__webCache.getRelativePath(self.__imageUrl, appName=self.__defLocalDirPath) or ''
            newPath = relativePath.replace('\\', '/')
            if newPath:
                _logger.debug('Got replay path %s for url %s', newPath, self.__imageUrl)
                self.__callbackDelayer.destroy()
                self.__webCache = None
                self.__callMethod(str(newPath))
                return
            _logger.debug('Failed to get image from web cache by url %s. Downloading initialized.', self.__imageUrl)
            self.__webCache.loadCustomUrls([self.__imageUrl], self.__defLocalDirPath)
            self.__webCache.onDownloadFinished += self.__stop
            self.__callbackDelayer.delayCallback(self.__DEFAULT_TIMEOUT, self.__stop)
            return

    def __stop(self):
        self.__callbackDelayer.destroy()
        self.__webCache.onDownloadFinished -= self.__stop
        relativePath = self.__webCache.getRelativePath(self.__imageUrl, appName=self.__defLocalDirPath) or ''
        newPath = relativePath.replace('\\', '/')
        _logger.debug('Got replay path %s for url %s', newPath, self.__imageUrl)
        self.__webCache = None
        self.__callMethod(str(newPath))
        return

    def __onTimer(self):
        _logger.warning('Web Cache download timed out. Failed to load image from url: %s', self.__imageUrl)
        self.__stop()

    def __callMethod(self, localPath):
        callback = self.__callbackMethod
        self.__callbackMethod = None
        if callback is not None and callable(callback):
            callback(localPath)
        return
