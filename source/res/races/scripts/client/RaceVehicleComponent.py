# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/RaceVehicleComponent.py
import logging
import CGF
import Math
from Triggers import CylinderAreaComponent, AreaTriggerComponent
from races_prefabs import LINK_DETECTOR
from races_common.races_constants import PATH_DETECTOR_RADIUS, PATH_DETECTOR_HEIGHT, PATH_DETECTOR_DEEP
from script_component.DynamicScriptComponent import DynamicScriptComponent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from races.gui.shared.event import RacesEvent
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class RaceVehicleComponent(DynamicScriptComponent):

    def __init__(self, *_, **__):
        super(RaceVehicleComponent, self).__init__(*_, **__)
        self._prevActiveTurretIdx = None
        self.pathProjectData = None
        self.currentDistanceToFinish = float('inf')
        self.__areaTriggerGO = None
        self.__links = []
        CGF.loadGameObjectIntoHierarchy(LINK_DETECTOR, self.vehicle.entityGameObject, Math.Vector3(0, -PATH_DETECTOR_DEEP, 0), self._linkDetectorLoaded)
        return

    @property
    def vehicle(self):
        return self.entity

    @property
    def linksInZone(self):
        area = self.__areaTriggerGO() if self.__areaTriggerGO is not None else None
        return area.objectsInProximity if area else []

    def setPathProject(self, projectData):
        self.projectData = projectData
        self.currentDistanceToFinish = projectData.getDistanceToLastNode()

    def set_raceFinishTime(self, _=None):
        if self.vehicle.isPlayerVehicle and self.raceFinishTime:
            g_eventBus.handleEvent(RacesEvent(RacesEvent.ON_RACE_FINISHED), scope=EVENT_BUS_SCOPE.BATTLE)
        _logger.debug('RaceVehicleComponent endTime=%s', self.raceFinishTime)

    def needPathProjectUpdate(self):
        return self.racePosition == 0 and self.__areaTriggerGO is not None and self.__areaTriggerGO() is not None

    def _linkDetectorLoaded(self, go):
        if self.vehicle.isDestroyed:
            return
        else:
            if go.findComponentByType(CylinderAreaComponent) is None:
                go.createComponent(CylinderAreaComponent, PATH_DETECTOR_RADIUS, PATH_DETECTOR_HEIGHT)
            self.__areaTriggerGO = CGF.ComponentLink(go, AreaTriggerComponent)
            return

    def set_gunProperties(self, _):
        descr = self.entity.typeDescriptor
        properties = self.gunProperties
        if not properties:
            if self._prevActiveTurretIdx is not None:
                descr.activeTurretPosition = self._prevActiveTurretIdx
                _logger.debug('[RaceVehicleComponent] - removed temporary gun')
                self._prevActiveTurretIdx = None
            return
        else:
            self._prevActiveTurretIdx = descr.activeTurretPosition
            newGun = descr.gun.copy()
            newGun.clip = (properties['clip'], properties['clipInterval'])
            newGun.burst = (properties['burst'], properties['burstInterval'])
            newGun.tags = set()
            if properties['clip'] > 1:
                newGun.tags.add('clip')
            descr.gun = newGun
            _logger.debug('[RaceVehicleComponent] - added new temporary gun')
            return
