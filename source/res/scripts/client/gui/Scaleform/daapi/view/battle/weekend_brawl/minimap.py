# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/minimap.py
from collections import namedtuple
import logging
import Math
from gui.battle_control.battle_constants import UNDEFINED_VEHICLE_ID
from gui.battle_control.controllers.points_of_interest_ctrl import IPointOfInterestListener
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from weekend_brawl_common import POIActivityStatus
_logger = logging.getLogger(__name__)
_POI_STATES = {POIActivityStatus.ACTIVE: BATTLE_MINIMAP_CONSTS.STATE_ACTIVE,
 POIActivityStatus.CAPTURING: BATTLE_MINIMAP_CONSTS.STATE_NOT_ACTIVE,
 POIActivityStatus.COOLDOWN: BATTLE_MINIMAP_CONSTS.STATE_NOT_ACTIVE}
_PointsInfo = namedtuple('_PointsInfo', ('entryID', 'guiState'))

class WeekendBrawlEntries(object):
    INTEREST_POINT = 'InterestPointEntry'


class WeekendBrawlMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(WeekendBrawlMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['pointsOfInterest'] = PointOfInterestPlugin
        return setup


class PointOfInterestPlugin(EntriesPlugin, IPointOfInterestListener):
    __slots__ = ('__pointsOfInterest',)

    def __init__(self, parentObj):
        super(PointOfInterestPlugin, self).__init__(parentObj)
        self.__pointsOfInterest = {}

    def start(self):
        super(PointOfInterestPlugin, self).start()
        if self.sessionProvider.dynamic.pointsOfInterest is not None:
            self.sessionProvider.dynamic.pointsOfInterest.addPlugin(self)
        self.restart()
        return

    def stop(self):
        if self.sessionProvider.dynamic.pointsOfInterest is not None:
            self.sessionProvider.dynamic.pointsOfInterest.removePlugin(self)
        self.__pointsOfInterest = {}
        super(PointOfInterestPlugin, self).stop()
        return

    def restart(self):
        self.__clearPoints()
        self.__addPointsOfInterest()

    def updateState(self, pointID, newState, startTime, vehicleID=UNDEFINED_VEHICLE_ID):
        pointInfo = self.__pointsOfInterest.get(pointID)
        if pointInfo is None:
            _logger.error('Point of Interest with id=%s is not found on the minimap', pointID)
            return
        else:
            newGuiState = _POI_STATES[newState]
            if newGuiState != pointInfo.guiState:
                entryID = pointInfo.entryID
                self._invoke(entryID, BATTLE_MINIMAP_CONSTS.SET_STATE, newGuiState)
                self.__pointsOfInterest[pointID] = _PointsInfo(entryID, newGuiState)
            return

    def __addPointsOfInterest(self):
        pointsOfInterestCtrl = self.sessionProvider.dynamic.pointsOfInterest
        if pointsOfInterestCtrl is None:
            _logger.error('Controller for Points of Interests is not found')
            return
        else:
            for pointID, position, state in pointsOfInterestCtrl.getPointsOfInterest():
                matrix = Math.Matrix()
                matrix.setTranslate(Math.Vector3(position))
                entryID = self._addEntry(WeekendBrawlEntries.INTEREST_POINT, CONTAINER_NAME.TEAM_POINTS, matrix=matrix, active=True)
                guiState = _POI_STATES[state]
                self._invoke(entryID, BATTLE_MINIMAP_CONSTS.SET_STATE, guiState)
                self.__pointsOfInterest[pointID] = _PointsInfo(entryID, guiState)

            return

    def __clearPoints(self):
        for entryID, _ in self.__pointsOfInterest.values():
            self._delEntry(entryID)

        self.__pointsOfInterest = {}
