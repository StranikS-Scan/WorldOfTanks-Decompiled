# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/StaticDeathZoneVisual.py
import enum
import BigWorld
from Math import Vector3, Vector4
from Event import Event
from helpers import dependency
from PlayerEvents import g_playerEvents
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
        self._borders = _BordersHelper()
        self._borders.init(self.entity.position, self.deathzone_size)
        self._borderDrawType = _DrawType.NORMAL

    def onDestroy(self):
        self.hide()
        g_eventBus.removeListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.entity.onActiveChanged -= self._onEntityActiveChanged

    def show(self):
        self._drawBorders()
        StaticDeathZoneVisual.onShowDeathZone(self.entity.zoneId, self)

    def hide(self):
        self._hideBorders()
        StaticDeathZoneVisual.onHideDeathZone(self.entity.zoneId)

    def getClosestPoint(self, point, _):
        return self._borders.getClosestPoint(point)

    def getCorners(self):
        return self._borders.rect

    def _onAvatarReady(self):
        super(StaticDeathZoneVisual, self)._onAvatarReady()
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

    def _activateDeathZone(self):
        g_playerEvents.onStaticDeathZoneActivated(self)
        self._drawBorders()
        self._createMarker()

    def _deactivateDeathZone(self):
        g_playerEvents.onStaticDeathZoneDeactivated(self.zoneId)
        self._hideBorders()
        self._removeMarker()

    def _drawBorders(self):
        spaceID = self._spaceID
        if spaceID:
            BigWorld.ArenaBorderHelper.setBorderBounds(spaceID, self.zoneIndex, self.entity.position, self._borders.bounds)
            color = self.__getCurrentColor(self.settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND))
            BigWorld.ArenaBorderHelper.setBorderColor(spaceID, self.zoneIndex, color)
            BigWorld.ArenaBorderHelper.setBorderVisible(spaceID, self.zoneIndex, True)

    def _hideBorders(self):
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

    def init(self, center, size):
        self._bounds = Vector4(-size.x / 2, -size.z / 2, size.x / 2, size.z / 2)
        self._min = Vector3(center.x + self._bounds[0], center.y, center.z + self._bounds[3])
        self._max = Vector3(center.x + self._bounds[2], center.y, center.z + self._bounds[1])

    def getClosestPoint(self, point):
        x = min(max(point[0], self._min.x), self._max.x)
        y = min(max(point[2], self._max.z), self._min.z)
        return Vector3(x, point.y, y)

    @property
    def rect(self):
        return (self._min, self._max)

    @property
    def bounds(self):
        return self._bounds
