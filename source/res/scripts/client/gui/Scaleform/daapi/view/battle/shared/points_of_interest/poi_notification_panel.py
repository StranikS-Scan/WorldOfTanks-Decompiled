# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/points_of_interest/poi_notification_panel.py
import logging
import typing
import BigWorld
from Event import EventsSubscriber
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.constants import POI_TYPE_UI_MAPPING, POI_STATUS_UI_MAPPING
from gui.Scaleform.daapi.view.meta.PointsOfInterestNotificationPanelMeta import PointsOfInterestNotificationPanelMeta
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from helpers import dependency
from points_of_interest.components import PoiStateUpdateMask
from points_of_interest.mixins import PointsOfInterestListener
from points_of_interest_shared import ENEMY_VEHICLE_ID
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from points_of_interest.components import PoiStateComponent
    from points_of_interest_shared import PoiType
_logger = logging.getLogger(__name__)
_R_NOTIFICATION_PANEL = R.strings.points_of_interest.notificationPanel

class PointsOfInterestPanel(PointsOfInterestNotificationPanelMeta, PointsOfInterestListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        PointsOfInterestNotificationPanelMeta.__init__(self)
        PointsOfInterestListener.__init__(self)
        self.__es = EventsSubscriber()

    @property
    def __isAvatarReady(self):
        return BigWorld.player().userSeesWorld()

    def _populate(self):
        super(PointsOfInterestPanel, self)._populate()
        for poiState in self._poiStateQuery:
            self.onPoiAdded(poiState)

        self._registerPoiListener()
        self.__es.subscribeToEvent(self.__sessionProvider.dynamic.pointsOfInterest.onPoiCaptured, self.__onPoiCaptured)

    def _dispose(self):
        self.__es.unsubscribeFromAllEvents()
        self._unregisterPoiListener()
        super(PointsOfInterestPanel, self)._dispose()

    def onPoiAdded(self, poiState):
        poiVO = {'id': poiState.id,
         'type': POI_TYPE_UI_MAPPING[poiState.type],
         'status': POI_STATUS_UI_MAPPING[poiState.status.statusID],
         'isAlly': self.__isAlly(poiState),
         'progress': poiState.progress}
        self.as_addPoiStatusS(poiVO)

    def onProcessPoi(self, poiState):
        if poiState.updatedFields & (PoiStateUpdateMask.STATUS | PoiStateUpdateMask.INVADER):
            self.__updateStatus(poiState)
        if poiState.updatedFields & PoiStateUpdateMask.PROGRESS:
            self.__updateProgress(poiState)

    def __updateStatus(self, poiState):
        status = POI_STATUS_UI_MAPPING[poiState.status.statusID]
        isAlly = self.__isAlly(poiState)
        self.as_updatePoiStatusS(id=poiState.id, status=status, isAlly=isAlly)

    def __updateProgress(self, poiState):
        self.as_updatePoiProgressS(id=poiState.id, progress=poiState.progress)

    def __onPoiCaptured(self, poiID, vehicleID):
        if vehicleID == avatar_getter.getVehicleIDAttached():
            return
        elif not self.__isAvatarReady:
            return
        else:
            poiState = self.__sessionProvider.dynamic.pointsOfInterest.getPoiState(poiID)
            if poiState is None:
                _logger.error('Missing PointOfInterest id=%s.', poiID)
                return
            poiType = poiState.type
            isAlly = vehicleID != ENEMY_VEHICLE_ID
            message = self.__getPoiCapturedMessage(poiType, isAlly, vehicleID)
            self.as_addNotificationS(poiID, isAlly=isAlly, message=message)
            return

    @classmethod
    def __getPoiCapturedMessage(cls, poiType, isAlly, vehicleID):
        poiName = backport.text(R.strings.points_of_interest.type.dyn(poiType.name.lower())())
        if isAlly:
            playerName = cls.__sessionProvider.getCtx().getPlayerFullName(vehicleID, showVehShortName=False, showClan=False)
            message = backport.text(_R_NOTIFICATION_PANEL.poiCaptured.ally(), poiName=text_styles.poiCapturedBoldText(poiName), playerName=text_styles.poiCapturedBoldText(playerName))
        else:
            message = backport.text(_R_NOTIFICATION_PANEL.poiCaptured.enemy(), poiName=text_styles.poiCapturedBoldText(poiName))
        return text_styles.poiCapturedRegularText(message)

    @staticmethod
    def __isAlly(poiState):
        return bool(poiState.invader)
