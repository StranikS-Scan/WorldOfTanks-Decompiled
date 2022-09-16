# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/status_notifications/poi_sn_items.py
import logging
import typing
from gui.Scaleform.daapi.view.battle.shared.status_notifications.components import StatusNotificationsGroup
from gui.Scaleform.daapi.view.battle.shared.status_notifications.sn_items import TimerSN
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES as _LINKS
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
from points_of_interest.poi_view_states import PointViewState, VehicleViewState
from points_of_interest_shared import PoiStatus, PoiType, PoiBlockReasons, INVALID_TIMESTAMP
from shared_utils import findFirst
_logger = logging.getLogger(__name__)

class PointOfInterestSN(TimerSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.POINT_OF_INTEREST_STATE

    def getIconNames(self, value=None):
        return (self.NOT_CHANGE_DEFAULT_ICON, self.NOT_CHANGE_DEFAULT_ICON)

    def _setIconName(self, iconName, iconSmallName):
        self._vo['iconName'] = iconName
        self._vo['iconSmallName'] = iconSmallName

    def _getPoiName(self, value):
        return '' if value is None else backport.text(R.strings.points_of_interest.type.dyn(self._getPoiType(value).name.lower())())

    def _getPoiType(self, value):
        if isinstance(value, PointViewState):
            return value.type
        elif isinstance(value, VehicleViewState):
            poiState = self._sessionProvider.dynamic.pointsOfInterest.getPoiState(value.id)
            return poiState.type
        else:
            return None

    def _isActive(self, value):
        raise NotImplementedError

    def _getTimeParams(self, value):
        return (0, 0) if value.status.endTime == INVALID_TIMESTAMP or value.status.startTime == INVALID_TIMESTAMP else (value.status.endTime - value.status.startTime, value.status.endTime)

    def _update(self, value=None):
        if value is None:
            self._setVisible(False)
            return
        else:
            isActive = self._isActive(value)
            self._setVisible(isActive)
            if isActive:
                self._updateTimeParams(*self._getTimeParams(value))
                self._setIconName(*self.getIconNames(value))
            self._sendUpdate()
            return


class PoICapturingSN(PointOfInterestSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.POI_CAPTURING

    def getIconNames(self, value=None):
        poiType = self._getPoiType(value)
        if poiType == PoiType.ARTILLERY:
            return (_LINKS.POI_GREEN_ARTILLERY_ICON, _LINKS.POI_GREEN_ARTILLERY_SMALL_ICON)
        return (_LINKS.POI_GREEN_RECON_ICON, _LINKS.POI_GREEN_RECON_SMALL_ICON) if poiType == PoiType.RECON else (self.NOT_CHANGE_DEFAULT_ICON, self.NOT_CHANGE_DEFAULT_ICON)

    def _isActive(self, value):
        return value.invader == self._sessionProvider.shared.vehicleState.getControllingVehicleID() and value.status.statusID is PoiStatus.CAPTURING

    def _getTitle(self, value):
        return backport.text(R.strings.points_of_interest.statusNotifications.capturing(), poiName=self._getPoiName(value))


class PoICooldownSN(PointOfInterestSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.POI_COOLDOWN

    def getIconNames(self, value=None):
        poiType = self._getPoiType(value)
        if poiType == PoiType.ARTILLERY:
            return (_LINKS.POI_ORANGE_ARTILLERY_ICON, _LINKS.POI_ORANGE_ARTILLERY_SMALL_ICON)
        return (_LINKS.POI_ORANGE_RECON_ICON, _LINKS.POI_ORANGE_RECON_SMALL_ICON) if poiType == PoiType.RECON else (self.NOT_CHANGE_DEFAULT_ICON, self.NOT_CHANGE_DEFAULT_ICON)

    def _isActive(self, value):
        return value.status.statusID is PoiStatus.COOLDOWN

    def _getTitle(self, value):
        return backport.text(R.strings.points_of_interest.statusNotifications.blocked.cooldown())


class PoIBlockedNotUsedAbilitySN(PointOfInterestSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.POINT_OF_INTEREST_VEHICLE_STATE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.POI_BLOCKED_NOT_USED_ABILITY

    def _getTimeParams(self, value):
        pass

    def getIconNames(self, value=None):
        poiType = self._getPoiType(value)
        if poiType == PoiType.ARTILLERY:
            return (_LINKS.POI_ORANGE_ARTILLERY_ICON, _LINKS.POI_ORANGE_ARTILLERY_SMALL_ICON)
        return (_LINKS.POI_ORANGE_RECON_ICON, _LINKS.POI_ORANGE_RECON_SMALL_ICON) if poiType == PoiType.RECON else (self.NOT_CHANGE_DEFAULT_ICON, self.NOT_CHANGE_DEFAULT_ICON)

    def _isActive(self, value):
        return any((reason for reason in value.blockReasons if reason.statusID is PoiBlockReasons.EQUIPMENT))

    def _getTitle(self, value):
        return backport.text(R.strings.points_of_interest.statusNotifications.blocked.equipmentNotUsed())


class PoICapturingInterruptedSN(PointOfInterestSN):

    def getItemID(self):
        return VEHICLE_VIEW_STATE.POINT_OF_INTEREST_VEHICLE_STATE

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.POI_CAPTURING_INTERRUPTED

    def _getTimeParams(self, value):
        blockReason = findFirst(lambda reason: reason.statusID is PoiBlockReasons.DAMAGE, value.blockReasons)
        if blockReason is not None:
            return (blockReason.endTime - blockReason.startTime, blockReason.endTime)
        else:
            _logger.error('Attempt to get time for PoICapturingInterruptedSN with no reason for it')
            return (None, None)

    def getIconNames(self, value=None):
        return (_LINKS.POI_ORANGE_CROSS_ICON, _LINKS.POI_ORANGE_CROSS_SMALL_ICON)

    def _isActive(self, value):
        return any((reason for reason in value.blockReasons if reason.statusID is PoiBlockReasons.DAMAGE))

    def _getTitle(self, value):
        return backport.text(R.strings.points_of_interest.statusNotifications.blocked.damage(), poiName=self._getPoiName(value))


class PoIBlockedNotInvaderSN(PointOfInterestSN):

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.POI_BLOCKED_NOT_INVADER

    def _getTimeParams(self, value):
        pass

    def getIconNames(self, value=None):
        poiType = self._getPoiType(value)
        if poiType == PoiType.ARTILLERY:
            return (_LINKS.POI_ORANGE_ARTILLERY_ICON, _LINKS.POI_ORANGE_ARTILLERY_SMALL_ICON)
        return (_LINKS.POI_ORANGE_RECON_ICON, _LINKS.POI_ORANGE_RECON_SMALL_ICON) if poiType == PoiType.RECON else (self.NOT_CHANGE_DEFAULT_ICON, self.NOT_CHANGE_DEFAULT_ICON)

    def _isActive(self, value):
        return value.invader != self._sessionProvider.shared.vehicleState.getControllingVehicleID() and value.status.statusID is PoiStatus.CAPTURING

    def _getTitle(self, value):
        return backport.text(R.strings.points_of_interest.statusNotifications.blocked.notInvader(), poiName=self._getPoiName(value))


class PoiNotificationsGroup(StatusNotificationsGroup):

    def __init__(self, updateCallback):
        super(PoiNotificationsGroup, self).__init__((PoICooldownSN,
         PoIBlockedNotUsedAbilitySN,
         PoICapturingInterruptedSN,
         PoIBlockedNotInvaderSN,
         PoICapturingSN), updateCallback)
