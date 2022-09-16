# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/points_of_interest/minimap.py
import logging
import typing
import math_utils
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.constants import POI_TYPE_UI_MAPPING, POI_STATUS_UI_MAPPING
from gui.Scaleform.daapi.view.battle.shared.points_of_interest.poi_helpers import getPoiCooldownProgress
from points_of_interest.components import PoiStateUpdateMask
from points_of_interest.mixins import PointsOfInterestListener
from points_of_interest_shared import PoiStatus
if typing.TYPE_CHECKING:
    from points_of_interest.components import PoiStateComponent
_logger = logging.getLogger(__name__)
_POI_MINIMAP_ENTRY_SYMBOL = 'PoiMinimapEntry'

class PointsOfInterestPlugin(EntriesPlugin, PointsOfInterestListener):

    def __init__(self, parentObj):
        EntriesPlugin.__init__(self, parentObj)
        PointsOfInterestListener.__init__(self)

    def start(self):
        super(PointsOfInterestPlugin, self).start()
        for poiState in self._poiStateQuery:
            self.onPoiAdded(poiState)

        self._registerPoiListener()

    def stop(self):
        self._unregisterPoiListener()
        super(PointsOfInterestPlugin, self).stop()

    def onPoiAdded(self, poiState):
        poiID = poiState.id
        poi = self.sessionProvider.dynamic.pointsOfInterest.getPoiEntity(poiID)
        if poi is None:
            _logger.error('Missing PointOfInterest id=%s', poiID)
            return
        else:
            entry = self._addEntryEx(uniqueID=poiID, symbol=_POI_MINIMAP_ENTRY_SYMBOL, container=CONTAINER_NAME.TEAM_POINTS, matrix=math_utils.createTranslationMatrix(poi.position), active=True)
            entryID = entry.getID()
            self.__updateType(entryID, poiState)
            self.__updateStatus(entryID, poiState)
            self.__updateProgress(entryID, poiState)
            self.__updateTeam(entryID, poiState)
            if poiState.status.statusID == PoiStatus.COOLDOWN:
                self.__updateCooldownProgress(entryID, poiState)
            return

    def onPoiRemoved(self, poiState):
        self._delEntryEx(uniqueID=poiState.id)

    def onProcessPoi(self, poiState):
        entry = self._entries.get(poiState.id)
        if entry is None:
            return
        else:
            entryID = entry.getID()
            updatedFields = poiState.updatedFields
            if updatedFields & PoiStateUpdateMask.STATUS:
                self.__updateStatus(entryID, poiState)
            if updatedFields & (PoiStateUpdateMask.STATUS | PoiStateUpdateMask.PROGRESS):
                self.__updateProgress(entryID, poiState)
            if updatedFields & PoiStateUpdateMask.INVADER:
                self.__updateTeam(entryID, poiState)
            if poiState.status.statusID == PoiStatus.COOLDOWN:
                self.__updateCooldownProgress(entryID, poiState)
            return

    def __updateType(self, entryID, state):
        poiType = POI_TYPE_UI_MAPPING[state.type]
        self._invoke(entryID, 'setType', poiType)

    def __updateStatus(self, entryID, poiState):
        statusID = POI_STATUS_UI_MAPPING[poiState.status.statusID]
        self._invoke(entryID, 'setStatus', statusID)

    def __updateProgress(self, entryID, poiState):
        progress = poiState.progress
        self._invoke(entryID, 'setProgress', progress)

    def __updateTeam(self, entryID, poiState):
        isAlly = bool(poiState.invader)
        self._invoke(entryID, 'setIsAlly', isAlly)

    def __updateCooldownProgress(self, entryID, poiState):
        progress = getPoiCooldownProgress(poiState)
        self._invoke(entryID, 'setProgress', progress)
