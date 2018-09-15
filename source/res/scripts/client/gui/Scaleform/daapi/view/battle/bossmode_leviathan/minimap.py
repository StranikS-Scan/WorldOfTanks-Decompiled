# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/minimap.py
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent, GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import common, entries, plugins, settings
from gui.battle_control import minimap_utils
import Math
LEVIATHAN_HEALTH_POWERUP_STATIC_MARKER = 'leviathanHealthPowerupStaticMarker'
LEVIATHAN_PORTAL_ICON_STATIC_MARKER = 'leviathanPortalIconStaticMarker'
_C_NAME = settings.CONTAINER_NAME
_HALLOWEEN_MINIMAP_TO_FLASH_SYMBOL_NAME_MAPPING = {LEVIATHAN_HEALTH_POWERUP_STATIC_MARKER: settings.ENTRY_SYMBOL_NAME.LEVIATHAN_HEALTH_MARKER,
 LEVIATHAN_PORTAL_ICON_STATIC_MARKER: settings.ENTRY_SYMBOL_NAME.LEVIATHAN_PORTAL_MARKER}

class BossModeLeviathanMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(BossModeLeviathanMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['halloweenpowerups'] = PowerupIconsPlugin
        setup['points'] = PortalBasePointsPlugin
        return setup


class PowerupIconsPlugin(common.EntriesPlugin):
    """
    Any static marker on minimap corresponding to some position on terrain.
    """

    def start(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__addStaticMarker
            ctrl.onStaticMarkerRemoved += self.__delStaticMarker
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__addStaticMarker
            ctrl.onStaticMarkerRemoved -= self.__delStaticMarker
        super(PowerupIconsPlugin, self).stop()
        return

    def __addStaticMarker(self, objectID, position, markerSymbolName, show3DMarker=True):
        if markerSymbolName in _HALLOWEEN_MINIMAP_TO_FLASH_SYMBOL_NAME_MAPPING:
            self._addEntryEx(objectID, _HALLOWEEN_MINIMAP_TO_FLASH_SYMBOL_NAME_MAPPING[markerSymbolName], settings.CONTAINER_NAME.EQUIPMENTS, matrix=minimap_utils.makePositionMatrix(position), active=True)

    def __delStaticMarker(self, objectID):
        self._delEntryEx(objectID)


class PortalBasePointsPlugin(common.SimplePlugin):
    __slots__ = ('__entries',)

    def __init__(self, parentObj):
        super(PortalBasePointsPlugin, self).__init__(parentObj)
        self.__entries = []

    def start(self):
        super(PortalBasePointsPlugin, self).start()
        self.restart()

    def restart(self):
        for x in self.__entries:
            self._delEntry(x)

        self.__entries = []
        self.__addControlPoints()

    def __addPointEntry(self, symbol, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _C_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if entryID:
            self.__entries.append(entryID)

    def __addControlPoints(self):
        points = self._arenaVisitor.type.getControlPointsIterator()
        for position, number in points:
            self.__addPointEntry(_HALLOWEEN_MINIMAP_TO_FLASH_SYMBOL_NAME_MAPPING[LEVIATHAN_PORTAL_ICON_STATIC_MARKER], position)
