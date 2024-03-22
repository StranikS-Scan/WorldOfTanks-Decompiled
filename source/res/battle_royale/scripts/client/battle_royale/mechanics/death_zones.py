# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/mechanics/death_zones.py
from collections import namedtuple
import CGF
import Math
import BigWorld
from death_zones_helpers import ZONE_STATE, idxFrom, zoneIdFrom, ZONES_SIZE
from constants import IS_CLIENT
from cgf_script.managers_registrator import Rule, registerManager, onProcessQuery, registerRule
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes
if IS_CLIENT:
    from gui.shared import g_eventBus, EVENT_BUS_SCOPE
    from battle_royale.gui.shared.events import DeathZoneEvent
    from ArenaInfoDeathZonesComponent import ArenaInfoDeathZonesComponent
else:

    class ArenaInfoDeathZonesComponent(object):
        pass


_INVISIBLE_RIGHT = 1
_INVISIBLE_LEFT = 2
_INVISIBLE_UP = 4
_INVISIBLE_DOWN = 8
_UPDATE_PERIOD = 0.1
DeathZoneWallParameters = namedtuple('DeathZoneWallParameters', ['enableCenter',
 'maxAlpha',
 'centerAlpha',
 'wallHeight',
 'centerHeight',
 'color',
 'groundLineHeight',
 'groundLineAlpha'])

class DeathZoneUpdaterManager(CGF.ComponentManager):

    @onProcessQuery(ArenaInfoDeathZonesComponent, tickGroup='Simulation', updatePeriod=_UPDATE_PERIOD)
    def onProcess(self, deathZones):
        if deathZones.updatedZones:
            g_eventBus.handleEvent(DeathZoneEvent(DeathZoneEvent.UPDATE_DEATH_ZONE, ctx={'deathZones': deathZones}), scope=EVENT_BUS_SCOPE.BATTLE)
            deathZones.updatedZones = []


class DeathZoneDrawManager(CGF.ComponentManager):

    def __init__(self, args):
        super(DeathZoneDrawManager, self).__init__(args)
        self.activeWall, self.waitingWall = args
        self.__hashedBoundingBox = None
        return

    def activate(self):
        boundingBox = self.__getBoundingBox()
        self._cornerPosition = Math.Vector3(boundingBox[0][0], 0, boundingBox[0][1])
        self._zoneSizeX, self._zoneSizeY = (boundingBox[1] - boundingBox[0]).tuple()
        self._zoneSizeX /= ZONES_SIZE
        self._zoneSizeY /= ZONES_SIZE
        halfSizeX = self._zoneSizeX * 0.5
        halfSizeY = self._zoneSizeY * 0.5
        self._zonePositionOffset = Math.Vector3(halfSizeX, 0, halfSizeY)
        self._zoneScale = Math.Vector4(-halfSizeX, -halfSizeY, halfSizeX, halfSizeY)
        g_eventBus.addListener(DeathZoneEvent.UPDATE_DEATH_ZONE, self._updateZones, scope=EVENT_BUS_SCOPE.BATTLE)

    def deactivate(self):
        g_eventBus.removeListener(DeathZoneEvent.UPDATE_DEATH_ZONE, self._updateZones, scope=EVENT_BUS_SCOPE.BATTLE)

    def _updateZones(self, event):
        deathZones = event.ctx['deathZones']
        for zoneID in deathZones.updatedZones:
            self._drawZones(zoneID, deathZones)

    def _drawZones(self, zoneID, deathZones):
        x, y = idxFrom(zoneID)
        state = deathZones.activeZones[zoneID]
        wall = self.activeWall if state == ZONE_STATE.CRITICAL else self.waitingWall
        position = self._cornerPosition + Math.Vector3(x * self._zoneSizeX, 0, y * self._zoneSizeY)
        position += self._zonePositionOffset
        spaceID = self.spaceID
        BigWorld.ArenaBorderHelper.setBorderBounds(spaceID, zoneID, position, self._zoneScale)
        BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, zoneID, state != ZONE_STATE.SAVE)
        BigWorld.ArenaBorderHelper.setBorderColor(spaceID, zoneID, wall.color)
        BigWorld.ArenaBorderHelper.setBorderMaxAlpha(spaceID, zoneID, wall.maxAlpha)
        BigWorld.ArenaBorderHelper.setBorderHeight(spaceID, zoneID, wall.wallHeight)
        BigWorld.ArenaBorderHelper.setBordersDistanceFadeEnabled(spaceID, False)
        BigWorld.ArenaBorderHelper.setOutsideShift(spaceID, zoneID, 0)
        BigWorld.ArenaBorderHelper.setGroundLineHeight(spaceID, zoneID, wall.groundLineHeight)
        BigWorld.ArenaBorderHelper.setGroundLineAlpha(spaceID, zoneID, wall.groundLineAlpha)
        if wall.enableCenter:
            BigWorld.ArenaBorderHelper.enableCenterPoint(spaceID, zoneID, True)
            BigWorld.ArenaBorderHelper.setCenterHeight(spaceID, zoneID, wall.centerHeight)
            BigWorld.ArenaBorderHelper.setCenterAlpha(spaceID, zoneID, wall.centerAlpha)
        visibilityMask = self._setBoundsVisibility(x, y, state, deathZones)
        BigWorld.ArenaBorderHelper.setBorderMask(spaceID, zoneID, visibilityMask)
        deathZones.visibilityMskZones[zoneID] = visibilityMask

    def _setBoundsVisibility(self, x, y, state, deathZones):
        visibilityMask = 0
        dxdy = ((-1, 0, (_INVISIBLE_RIGHT, _INVISIBLE_LEFT)),
         (1, 0, (_INVISIBLE_LEFT, _INVISIBLE_RIGHT)),
         (0, 1, (_INVISIBLE_DOWN, _INVISIBLE_UP)),
         (0, -1, (_INVISIBLE_UP, _INVISIBLE_DOWN)))
        for dx, dy, borderMsks in dxdy:
            _x, _y = x + dx, y + dy
            if 0 <= _x < ZONES_SIZE:
                if 0 <= _y < ZONES_SIZE:
                    self._checkSide(_x, _y, borderMsks[0], state, deathZones) and visibilityMask |= borderMsks[1]

        return visibilityMask

    def _checkSide(self, x, y, mask, state, deathZones):
        zId = zoneIdFrom(x, y)
        zState = deathZones.activeZones[zId]
        zBorderMask = deathZones.visibilityMskZones[zId]
        if zState == ZONE_STATE.SAVE:
            return False
        if state == ZONE_STATE.WARNING and zState == ZONE_STATE.CRITICAL:
            return True
        if state == zState:
            visibilityMask = zBorderMask | mask
            BigWorld.ArenaBorderHelper.setBorderMask(self.spaceID, zId, visibilityMask)
            deathZones.visibilityMskZones[zId] = visibilityMask
            return True
        return False

    def __getBoundingBox(self):
        if self.__hashedBoundingBox is None:
            self.__hashedBoundingBox = BigWorld.player().arena.arenaType.boundingBox
        return self.__hashedBoundingBox


@registerRule
class DeathZonesRule(Rule):
    category = 'Steel Hunter'
    editorTitle = 'Death Zones Mechanics Rule'
    domain = CGF.DomainOption.DomainAll
    activeEnableCenter = ComponentProperty(type=CGFMetaTypes.BOOL, value=True, editorName='Active Enable Center Point')
    activeMaxAlpha = ComponentProperty(type=CGFMetaTypes.FLOAT, value=0.5, editorName='Max Alpha')
    activeCentarAlpha = ComponentProperty(type=CGFMetaTypes.FLOAT, value=0.35, editorName='Active Center Alpha')
    activeWallHeight = ComponentProperty(type=CGFMetaTypes.FLOAT, value=32.0, editorName='Active Wall Height')
    activeCenterHeight = ComponentProperty(type=CGFMetaTypes.FLOAT, value=16.0, editorName='Active Center Height')
    activeGroundLineHeight = ComponentProperty(type=CGFMetaTypes.FLOAT, value=16.0, editorName='Active Ground Line Height')
    activeGroundLineAlpha = ComponentProperty(type=CGFMetaTypes.FLOAT, value=16.0, editorName=' Active Ground Line Alpha')
    activeColor = ComponentProperty(type=CGFMetaTypes.VECTOR4, value=Math.Vector4(0.8, 0.0, 0.0, 0.0), editorName='Active color')
    waitingEnableCenter = ComponentProperty(type=CGFMetaTypes.BOOL, value=False, editorName='Waiting Enable Center Point')
    waitingMaxAlpha = ComponentProperty(type=CGFMetaTypes.FLOAT, value=0.5, editorName='Waiting Max Alpha')
    waitingCentarAlpha = ComponentProperty(type=CGFMetaTypes.FLOAT, value=0.5, editorName='Waiting Center Alpha')
    waitingWallHeight = ComponentProperty(type=CGFMetaTypes.FLOAT, value=16.0, editorName='Waiting Wall Height')
    waitingCenterHeight = ComponentProperty(type=CGFMetaTypes.FLOAT, value=16.0, editorName='Waiting Center Height')
    waitingGroundLineHeight = ComponentProperty(type=CGFMetaTypes.FLOAT, value=16.0, editorName='Waiting Ground Line Height')
    waitingGroundLineAlpha = ComponentProperty(type=CGFMetaTypes.FLOAT, value=16.0, editorName='Waiting Ground Line Alpha')
    waitingColor = ComponentProperty(type=CGFMetaTypes.VECTOR4, value=Math.Vector4(1.0, 0.6, 0.0, 0.0), editorName='Waiting Color')

    @registerManager(DeathZoneDrawManager)
    def registerDeathZonesDrawManager(self):
        return (DeathZoneWallParameters(self.activeEnableCenter, self.activeMaxAlpha, self.activeCentarAlpha, self.activeWallHeight, self.activeCenterHeight, self.activeColor, self.activeGroundLineHeight, self.activeGroundLineAlpha), DeathZoneWallParameters(self.waitingEnableCenter, self.waitingMaxAlpha, self.waitingCentarAlpha, self.waitingWallHeight, self.waitingCenterHeight, self.waitingColor, self.waitingGroundLineHeight, self.waitingGroundLineAlpha))

    @registerManager(DeathZoneUpdaterManager)
    def registerDeathZoneUpdaterManager(self):
        return None
