# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/mechanics/death_zones.py
from __future__ import absolute_import
from collections import namedtuple
import CGF
import Math
import BigWorld
from death_zones_helpers import ZONE_STATE, idxFrom, zoneIdFrom, ZONES_SIZE
from constants import IS_CLIENT
from cgf_script.registration import ComponentProperty, registerComponent
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

@registerComponent
class DeathZoneComponentSettings(object):
    category = 'Steel Hunter'
    editorTitle = 'Death Zones Mechanics Rule'
    domain = CGF.Domain.Client
    activeEnableCenter = ComponentProperty(type=CGF.PropertyType.Bool, value=True, editorName='Active Enable Center Point')
    activeMaxAlpha = ComponentProperty(type=CGF.PropertyType.Float, value=0.5, editorName='Max Alpha')
    activeCentarAlpha = ComponentProperty(type=CGF.PropertyType.Float, value=0.35, editorName='Active Center Alpha')
    activeWallHeight = ComponentProperty(type=CGF.PropertyType.Float, value=32.0, editorName='Active Wall Height')
    activeCenterHeight = ComponentProperty(type=CGF.PropertyType.Float, value=16.0, editorName='Active Center Height')
    activeGroundLineHeight = ComponentProperty(type=CGF.PropertyType.Float, value=16.0, editorName='Active Ground Line Height')
    activeGroundLineAlpha = ComponentProperty(type=CGF.PropertyType.Float, value=16.0, editorName=' Active Ground Line Alpha')
    activeColor = ComponentProperty(type=CGF.PropertyType.Vector4, value=Math.Vector4(0.8, 0.0, 0.0, 0.0), editorName='Active color')
    waitingEnableCenter = ComponentProperty(type=CGF.PropertyType.Bool, value=False, editorName='Waiting Enable Center Point')
    waitingMaxAlpha = ComponentProperty(type=CGF.PropertyType.Float, value=0.5, editorName='Waiting Max Alpha')
    waitingCentarAlpha = ComponentProperty(type=CGF.PropertyType.Float, value=0.5, editorName='Waiting Center Alpha')
    waitingWallHeight = ComponentProperty(type=CGF.PropertyType.Float, value=16.0, editorName='Waiting Wall Height')
    waitingCenterHeight = ComponentProperty(type=CGF.PropertyType.Float, value=16.0, editorName='Waiting Center Height')
    waitingGroundLineHeight = ComponentProperty(type=CGF.PropertyType.Float, value=16.0, editorName='Waiting Ground Line Height')
    waitingGroundLineAlpha = ComponentProperty(type=CGF.PropertyType.Float, value=16.0, editorName='Waiting Ground Line Alpha')
    waitingColor = ComponentProperty(type=CGF.PropertyType.Vector4, value=Math.Vector4(1.0, 0.6, 0.0, 0.0), editorName='Waiting Color')


class DeathZoneDrawSystem(CGF.System):
    DeathZonesIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(ArenaInfoDeathZonesComponent))
    SettingsCreate = CGF.CreateReaction(CGF.ReactRw(DeathZoneComponentSettings))
    Reactions = CGF.Reactions(DeathZonesIterate, SettingsCreate)

    def commonUpdate(self):
        for settings in self.reaction(self.SettingsCreate):
            self.activeWall = DeathZoneWallParameters(settings.activeEnableCenter, settings.activeMaxAlpha, settings.activeCentarAlpha, settings.activeWallHeight, settings.activeCenterHeight, settings.activeColor, settings.activeGroundLineHeight, settings.activeGroundLineAlpha)
            self.waitingWall = DeathZoneWallParameters(settings.waitingEnableCenter, settings.waitingMaxAlpha, settings.waitingCentarAlpha, settings.waitingWallHeight, settings.waitingCenterHeight, settings.waitingColor, settings.waitingGroundLineHeight, settings.waitingGroundLineAlpha)

    def periodUpdate(self):
        for deathZone in self.reaction(self.DeathZonesIterate):
            self.onProcess(deathZone)

    def __init__(self):
        super(DeathZoneDrawSystem, self).__init__()
        self.activeWall = None
        self.waitingWall = None
        self.__hashedBoundingBox = None
        return

    def onMappingLoaded(self):
        boundingBox = self.__getBoundingBox()
        self._cornerPosition = Math.Vector3(boundingBox[0][0], 0, boundingBox[0][1])
        self._zoneSizeX, self._zoneSizeY = (boundingBox[1] - boundingBox[0]).tuple()
        self._zoneSizeX /= ZONES_SIZE
        self._zoneSizeY /= ZONES_SIZE
        halfSizeX = self._zoneSizeX * 0.5
        halfSizeY = self._zoneSizeY * 0.5
        self._zonePositionOffset = Math.Vector3(halfSizeX, 0, halfSizeY)
        self._zoneScale = Math.Vector4(-halfSizeX, -halfSizeY, halfSizeX, halfSizeY)

    def onProcess(self, zone):
        if zone.updatedZones:
            g_eventBus.handleEvent(DeathZoneEvent(DeathZoneEvent.UPDATE_DEATH_ZONE, ctx={'deathZones': zone}), scope=EVENT_BUS_SCOPE.BATTLE)
            self._updateZones(zone)
            zone.updatedZones = []

    def _updateZones(self, deathZones):
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
