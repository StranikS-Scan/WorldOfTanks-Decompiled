# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/common/races_common/races_common_cgf/races_path_mechanics.py
import heapq
import logging
from collections import namedtuple
import CGF
import GenericComponents
import Math
from Triggers import AreaTriggerTarget
from cache import cached_property
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, registerRule, registerManager, Rule, onProcessQuery
from constants import IS_EDITOR
from math_common import isAlmostZero
_logger = logging.getLogger(__name__)
if not IS_EDITOR:
    from RaceVehicleComponent import RaceVehicleComponent
PROJ_SEGMENT_TOLERANCE = 10.0

class RaceLinkProjection(namedtuple('RaceLinkProjection', ['raceLink', 'distanceToLineSqr', 't'])):

    def __cmp__(self, other):
        return cmp(self.distanceToLineSqr, other.distanceToLineSqr) if isinstance(other, RaceLinkProjection) else -1

    def getDistanceToLastNode(self):
        raceLink = self.raceLink
        return raceLink.fromLink().distanceToFinish - self.t

    def getClosestPointOnLine(self):
        raceLink = self.raceLink
        linkVector = raceLink.getLinkNormaliseVector
        startPoint = raceLink.fromLink().transformLink().worldPosition
        return startPoint + self.t * linkVector


def checkPointInCylinder(point, cylinderPosition, radius, height):
    localPosition = point - cylinderPosition
    return localPosition.y <= height and localPosition.x ** 2 + localPosition.z ** 2 <= radius ** 2


def linearProjectionToLink(position, raceLink):
    linkVector = raceLink.getLinkNormaliseVector
    startPoint = raceLink.fromLink().transformLink().worldPosition
    positionToNodeVector = position - startPoint
    t = positionToNodeVector.dot(linkVector)
    if -PROJ_SEGMENT_TOLERANCE <= t <= raceLink.distance + PROJ_SEGMENT_TOLERANCE:
        distanceToLineSqr = (positionToNodeVector * linkVector).lengthSquared
    else:
        distanceToLineSqr = float('inf')
    return RaceLinkProjection(raceLink, distanceToLineSqr, t)


def getClosestLinkProjection(position, raceLinkObjects):
    result = None
    for linkGO in raceLinkObjects:
        pathLink = linkGO.findComponentByType(RacePathLink)
        if pathLink:
            proj = linearProjectionToLink(position, pathLink)
            if proj.distanceToLineSqr != float('inf'):
                result = proj if result is None else min(proj, result, key=lambda x: x.distanceToLineSqr)

    return result


@registerComponent
class RacePathNode(object):
    MAX_DISTANCE = 1000000.0
    category = 'races'
    domain = CGF.DomainOption.DomainAll
    transformLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Link to Transform', value=GenericComponents.TransformComponent)
    distanceToFinish = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='distance to finish', value=MAX_DISTANCE)

    def getNodeId(self):
        return self.transformLink.gameObject.id

    @property
    def nextLinks(self):
        linksQuery = CGF.Query(self.spaceID, RacePathLink)
        for link in linksQuery:
            if link.fromLink.gameObject.id == self.getNodeId():
                yield link

    @property
    def prevLinks(self):
        linksQuery = CGF.Query(self.spaceID, RacePathLink)
        for link in linksQuery:
            if link.toLink.gameObject.id == self.getNodeId():
                yield link


@registerComponent
class RacePathLink(object):
    category = 'races'
    domain = CGF.DomainOption.DomainAll
    fromLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='from', value=RacePathNode)
    toLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='to', value=RacePathNode)
    distance = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='distance')

    @cached_property
    def linkWorldVector(self):
        vector = self.toLink().transformLink().worldPosition - self.fromLink().transformLink().worldPosition
        if isAlmostZero(vector.lengthSquared):
            _logger.error('Bad link vector. From: %s To %s', self.fromLink().getNodeId(), self.toLink().getNodeId())
        return vector

    @cached_property
    def getLinkNormaliseVector(self):
        worldVector = Math.Vector3(self.linkWorldVector)
        worldVector.normalise()
        return worldVector

    def getDistance(self):
        if self.distance == 0.0:
            self.distance = self.linkWorldVector.length
        return self.distance

    def getNodesIterator(self):
        yield self.fromLink()
        yield self.toLink()


@registerComponent
class RacePathInitComponent(object):
    category = 'races'
    domain = CGF.DomainOption.DomainAll
    prefabFile = ComponentProperty(type=CGFMetaTypes.STRING, editorName='prefab path', value='')


@registerComponent
class RacePathConfig(object):
    category = 'races'
    domain = CGF.DomainOption.DomainAll
    startNodeLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='start Node', value=RacePathNode)
    finishNodeLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='finish Node', value=RacePathNode)


@registerComponent
class RacePath(object):
    domain = CGF.DomainOption.DomainAll

    def __init__(self):
        self.ready = False


class RacesPathController(CGF.ComponentManager):
    TICK_PERIOD = 0.3

    def getPathProject(self, position, zonePosition, zoneRaduis, zoneHeight):
        linksQuery = CGF.Query(self.spaceID, (CGF.GameObject, RacePathLink, GenericComponents.TransformComponent))
        result = None
        for go, link, transform in linksQuery:
            if checkPointInCylinder(transform.worldPosition, zonePosition, zoneRaduis, zoneHeight):
                proj = linearProjectionToLink(position, link)
                if proj.distanceToLineSqr != float('inf'):
                    result = proj if result is None else min(proj, result)

        return result

    @onAddedQuery(RacePathLink, CGF.GameObject)
    def onRaceLinkAdded(self, _, raceLinkGO):
        if raceLinkGO.findComponentByType(AreaTriggerTarget) is None:
            raceLinkGO.createComponent(AreaTriggerTarget)
        return

    @onProcessQuery(CGF.GameObject, RacePath, period=TICK_PERIOD)
    def detectPositions(self, go, path):
        if not path.ready or IS_EDITOR:
            return
        else:
            vehiclesQuery = CGF.Query(self.spaceID, RaceVehicleComponent)
            for raceVehicle in vehiclesQuery:
                if raceVehicle.needPathProjectUpdate():
                    closestNodeProject = getClosestLinkProjection(raceVehicle.vehicle.position, raceVehicle.linksInZone)
                    if closestNodeProject is not None:
                        raceVehicle.setPathProject(closestNodeProject)

            return


class RacesPathConstractor(CGF.ComponentManager):
    MAX_ITER_COUNT = 10000

    def _pathLoadedCallback(self, pathGO):
        if pathGO.findComponentByType(RacePath) is None:
            pathGO.createComponent(RacePath)
        return

    @onAddedQuery(RacePathLink, GenericComponents.TransformComponent, CGF.No(RacePathNode))
    def onRaceLinkAdded(self, raceLink, transform):
        raceNodeTransform = raceLink.fromLink().transformLink()
        transform.transform = raceNodeTransform.transform

    @onAddedQuery(RacePathInitComponent, CGF.GameObject)
    def onPathInit(self, racePathInit, go):
        CGF.loadGameObjectIntoHierarchy(racePathInit.prefabFile, go, Math.Vector3(0, 0, 0), self._pathLoadedCallback)

    @onAddedQuery(RacePath, RacePathConfig, CGF.GameObject)
    def onRacePathAdded(self, racePath, raceConfig, raceLinkGO):
        if not racePath.ready:
            self.configureDistance(raceConfig.finishNodeLink())
            racePath.ready = True

    def configureDistance(self, finishNode):
        visited = set()
        finishNode.distanceToFinish = 0.0
        queue = [(0.0, finishNode)]
        iterCount = 0
        while queue:
            iterCount += 1
            if iterCount >= self.MAX_ITER_COUNT:
                _logger.error('Race path is very deep. iterCount >= MAX_ITER_COUNT. Reduce the number of points')
                return
            currentDistance, currentNode = heapq.heappop(queue)
            if currentNode.getNodeId() not in visited:
                visited.add(currentNode.getNodeId())
                for link in currentNode.prevLinks:
                    nextNode = link.fromLink()
                    distance = currentDistance + link.getDistance()
                    if distance < nextNode.distanceToFinish:
                        nextNode.distanceToFinish = distance
                        heapq.heappush(queue, (distance, nextNode))


@registerRule
class RacePathRule(Rule):
    category = 'races'
    domain = CGF.DomainOption.DomainAll

    @registerManager(RacesPathController, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainServer)
    def racePathController(self):
        return None

    @registerManager(RacesPathConstractor, domain=CGF.DomainOption.DomainAll)
    def racePathConstractor(self):
        return None
