# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EntityAreaBorderComponent.py
import BigWorld
from Math import Vector3
from cache import cached_property
from script_component.DynamicScriptComponent import DynamicScriptComponent
from account_helpers.settings_core import ISettingsCore, settings_constants
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent

class EntityAreaBorderComponent(DynamicScriptComponent):
    DRAW_TYPE_NORMAL = 0
    COLOR_BLINDNESS_MATERIAL_PARAM_NAME = 'g_isColorBlind'
    STRIPES_ENABLED_MATERIAL_PARAM_NAME = 'g_stripesEnabled'
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EntityAreaBorderComponent, self).__init__()
        self._border = None
        return

    def onDestroy(self):
        super(EntityAreaBorderComponent, self).onDestroy()
        self.settingsCore.onSettingsChanged -= self._onSettingsChanged
        g_eventBus.removeListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
        self._border = None
        return

    def set_isVisible(self, oldValue):
        self.updateBorderVisibility()

    @property
    def isBorderVisible(self):
        return self.isVisible

    def updateBorderVisibility(self):
        if not self._border:
            return
        self._border.setVisibility(self.isBorderVisible)

    def updateColorBlindness(self):
        isColorBlind = self.settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND)
        self._border.setMaterialBoolParam(self.COLOR_BLINDNESS_MATERIAL_PARAM_NAME, isColorBlind)

    def getClosestPoint(self, pos, searchRadius):
        return self._border.getClosestPoint(pos, searchRadius) if self._border else None

    def updateDrawStyle(self):
        arenaBorderCtrl = self.sessionProvider.shared.arenaBorder
        if arenaBorderCtrl:
            stripesEnabled = arenaBorderCtrl.getDrawType() == self.DRAW_TYPE_NORMAL
            self._border.setMaterialBoolParam(self.STRIPES_ENABLED_MATERIAL_PARAM_NAME, stripesEnabled)

    def getDimensions(self):
        return Vector3() if not self._border else self._border.getDimensions()

    @cached_property
    def polygonCenter(self):
        udo = BigWorld.userDataObjects.get(self.udoGuid, None)
        if not udo:
            return Vector3()
        else:
            cX, cZ = [], []
            for x, z in udo.minimapMarkerPolygon:
                cX.append(x)
                cZ.append(z)

            resX = (min(cX) + max(cX)) / 2
            resZ = (min(cZ) + max(cZ)) / 2
            return Vector3(resX, 0, -resZ) + udo.position

    def _onAvatarReady(self):
        super(EntityAreaBorderComponent, self)._onAvatarReady()
        self.settingsCore.onSettingsChanged += self._onSettingsChanged
        udo = BigWorld.userDataObjects.get(self.udoGuid, None)
        if udo is None:
            return
        else:
            self._border = BigWorld.PolygonalAreaBorder(self.spaceID, self.udoGuid)
            self.updateBorderVisibility()
            self.updateColorBlindness()
            self.updateDrawStyle()
            g_eventBus.addListener(GameEvent.ARENA_BORDER_TYPE_CHANGED, self._onArenaBorderTypeChanged, scope=EVENT_BUS_SCOPE.BATTLE)
            return

    def _onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            self.updateColorBlindness()

    def _onArenaBorderTypeChanged(self, event):
        self.updateDrawStyle()
