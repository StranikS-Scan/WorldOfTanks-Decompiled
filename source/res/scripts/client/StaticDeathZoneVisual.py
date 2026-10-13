# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StaticDeathZoneVisual.py
from __future__ import absolute_import, division
import enum
import BigWorld
import math
from Math import Vector3, Vector4
from Event import Event
from helpers import dependency
from gui.shared import g_eventBus
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.doc_loaders import GuiColorsLoader
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core import settings_constants
from script_component.DynamicScriptComponent import DynamicScriptComponent

class _DrawType(enum.IntEnum):
    NORMAL = 0
    STRIPES = 1


class StaticDeathZoneVisual(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    onShowDeathZone = Event()
    onHideDeathZone = Event()

    def __init__(self):
        super(StaticDeathZoneVisual, self).__init__()
        self._borders = _BordersHelperCircle() if self.isCircular else _BordersHelper()
        self._borders.init(self.entity.position, self.deathzone_size, 0)
        self._borderDrawType = _DrawType.NORMAL
        self._visible = False
        self._rotation = 0

    def onDestroy(self):
        g_eventBus.removeListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.entity.onActiveChanged -= self._onEntityActiveChanged

    def show(self):
        if self.drawBorder:
            self._drawBorders()
        StaticDeathZoneVisual.onShowDeathZone(self)

    def hide(self):
        if self.drawBorder:
            self._hideBorders()
        StaticDeathZoneVisual.onHideDeathZone()

    def getClosestPoint(self, point, _):
        closestPoint = self._borders.getClosestPoint(point)
        return (closestPoint, (point - closestPoint).length)

    def getClosestPointInverted(self, point, _):
        closestPoint = self._borders.getClosestPointInverted(point)
        return (closestPoint, (point - closestPoint).length)

    def getPolygon(self):
        return self._borders.polygon

    def getDimensions(self):
        return self.deathzone_size

    def resize(self, position, size, rotation):
        self.deathzone_size = size
        self._borders.init(position, size, rotation)
        self._rotation = rotation
        if self._visible:
            BigWorld.ArenaBorderHelper.setBorderGeometry(self._spaceID, self.zoneIndex, position, self._borders.bounds, self._rotation)

    def _onAvatarReady(self):
        super(StaticDeathZoneVisual, self)._onAvatarReady()
        if self.customBorder:
            borderModel = self.entity.getBorderModel(self.customBorder)
            spaceID = self._spaceID
            if borderModel and spaceID:
                BigWorld.ArenaBorderHelper.initCustomBorder(spaceID, self.zoneIndex, borderModel)
        g_eventBus.addListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.entity.onActiveChanged += self._onEntityActiveChanged
        arenaBorderCtrl = self.sessionProvider.shared.arenaBorder
        if arenaBorderCtrl:
            self._updateBorderDrawType(arenaBorderCtrl.getDrawType())
        if self.entity.isActive:
            self.show()

    def _onEntityActiveChanged(self, isActive):
        if isActive:
            self.show()
        else:
            self.hide()

    def _removeBorders(self):
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.removeBorder(spaceID, self.zoneIndex)

    def _drawBorders(self):
        spaceID = self._spaceID
        if spaceID:
            self._visible = True
            BigWorld.ArenaBorderHelper.setBorderGeometry(spaceID, self.zoneIndex, self.entity.position, self._borders.bounds, self._rotation)
            color = self.__getCurrentColor(self.settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND))
            BigWorld.ArenaBorderHelper.setBorderColor(spaceID, self.zoneIndex, color)
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self.zoneIndex, True)

    def _hideBorders(self):
        self._visible = False
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self.zoneIndex, False)

    def _updateBorderDrawType(self, arenaDrawType):
        self._borderDrawType = _DrawType.STRIPES if arenaDrawType == _DrawType.NORMAL else _DrawType.NORMAL
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.setBordersDrawType(spaceID, self.zoneIndex, self._borderDrawType)

    def _onArenaBorderTypeChanged(self, event):
        self._updateBorderDrawType(event.ctx['drawType'])

    @property
    def _spaceID(self):
        player = BigWorld.player()
        return player.spaceID if player and player.spaceID else None

    def __onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            color = self.__getCurrentColor(diff[settings_constants.GRAPHICS.COLOR_BLIND])
            spaceID = self._spaceID
            if spaceID:
                BigWorld.ArenaBorderHelper.setBorderColor(spaceID, self.zoneIndex, color)

    def __getCurrentColor(self, colorBlind):
        colors = GuiColorsLoader.load()
        scheme = colors.getSubScheme('areaBorder', 'color_blind' if colorBlind else 'default')
        color = scheme['rgba'] / 255
        return color


class _BordersHelper(object):

    def __init__(self):
        self._bounds = Vector4(0, 0, 0, 0)
        self._min = Vector3(0, 0, 0)
        self._max = Vector3(0, 0, 0)
        self._center = Vector3(0, 0, 0)
        self._rotation = 0
        self._polygon = []

    def init(self, center, size, rotation):
        self._center = center
        self._rotation = rotation
        self._halfSize = size / 2
        self._cos = math.cos(rotation)
        self._sin = math.sin(rotation)
        self._polygon = [(-self._halfSize.x * self._cos - self._halfSize.z * self._sin, -self._halfSize.x * self._sin + self._halfSize.z * self._cos),
         (-self._halfSize.x * self._cos + self._halfSize.z * self._sin, -self._halfSize.x * self._sin - self._halfSize.z * self._cos),
         (self._halfSize.x * self._cos + self._halfSize.z * self._sin, self._halfSize.x * self._sin - self._halfSize.z * self._cos),
         (self._halfSize.x * self._cos - self._halfSize.z * self._sin, self._halfSize.x * self._sin + self._halfSize.z * self._cos)]
        self._bounds = Vector4(-self._halfSize.x, -self._halfSize.z, self._halfSize.x, self._halfSize.z)
        self._min = Vector3(center.x - self._halfSize.x, center.y, center.z + self._halfSize.z)
        self._max = Vector3(center.x + self._halfSize.x, center.y, center.z - self._halfSize.z)

    def getClosestPoint(self, point):
        if not self._rotation:
            x = min(max(point.x, self._min.x), self._max.x)
            z = min(max(point.z, self._max.z), self._min.z)
            if x != point.x or z != point.z:
                return Vector3(x, point.y, z)
            return self._max
        dx = point.x - self._center.x
        dz = point.z - self._center.z
        rx = dx * self._cos - dz * self._sin
        rz = dx * self._sin + dz * self._cos
        x = min(max(rx, self._min.x), self._max.x)
        z = min(max(rz, self._max.z), self._min.z)
        return Vector3(self._center.x + x * self._cos + z * self._sin, point.y, self._center.z - x * self._sin + z * self._cos)

    def getClosestPointInverted(self, point):
        dx = point.x - self._center.x
        dz = point.z - self._center.z
        rx = dx * self._cos - dz * self._sin
        rz = dx * self._sin + dz * self._cos
        options = [(rx + self._halfSize.x, -self._halfSize.x, rz),
         (self._halfSize.x - rx, self._halfSize.x, rz),
         (rz + self._halfSize.z, rx, -self._halfSize.z),
         (self._halfSize.z - rz, rx, self._halfSize.z)]
        _, x, z = min(options)
        return Vector3(self._center.x + x * self._cos + z * self._sin, point.y, self._center.z - x * self._sin + z * self._cos)

    @property
    def polygon(self):
        return self._polygon

    @property
    def bounds(self):
        return self._bounds


class _BordersHelperCircle(_BordersHelper):
    _EPSILON = 0.01

    def __init__(self):
        super(_BordersHelperCircle, self).__init__()
        self._centerX = 0
        self._centerZ = 0
        self._R = 0

    def init(self, center, size, rotation):
        super(_BordersHelperCircle, self).init(center, size, rotation)
        self._centerX, _, self._centerZ = center
        self._R = size[0] / 2

    def getClosestPoint(self, point):
        x, y, z = point
        dx = x - self._centerX
        dz = z - self._centerZ
        dist = math.sqrt(dx ** 2 + dz ** 2)
        if dist < self._EPSILON:
            return Vector3(self._centerX, y, self._centerZ + self._R)
        scale = self._R / dist
        return Vector3(self._centerX + dx * scale, y, self._centerZ + dz * scale)

    def getClosestPointInverted(self, point):
        return self.getClosestPoint(point)
