# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/minimap.py
import typing
import CommandMapping
import GUI
from aih_constants import CTRL_MODE_NAME
from constants import PVE_MINIMAP_DEFAULT_ZOOM, PVE_MINIMAP_DEFAULT_BORDERS
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import PersonalEntriesPlugin
from gui.Scaleform.daapi.view.meta.PveMinimapMeta import PveMinimapMeta
from gui.battle_control import avatar_getter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ScalableBattleMinimapEvent
from gui.shared.utils.key_mapping import getReadableKey
from helpers import dependency
from pve_battle_hud import WidgetType, getPveHudLogger
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from Math import Vector2
_S_NAME = settings.ENTRY_SYMBOL_NAME
_logger = getPveHudLogger()

class PveMinimapGlobalSettingsPlugin(GlobalSettingsPlugin):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _toogleVisible(self):
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl is not None:
            minimapSettings = settingsCtrl.getSettings(WidgetType.MINIMAP)
            if minimapSettings and minimapSettings.canToggleFullMap:
                return
        super(PveMinimapGlobalSettingsPlugin, self)._toogleVisible()
        return


class PveScaleCenteredPersonalEntriesPlugin(PersonalEntriesPlugin):
    __slots__ = ()

    def initControlMode(self, mode, available):
        super(PveScaleCenteredPersonalEntriesPlugin, self).initControlMode(mode, available)
        self._centerMapBasedOnMode()

    def updateControlMode(self, mode, vehicleID):
        super(PveScaleCenteredPersonalEntriesPlugin, self).updateControlMode(mode, vehicleID)
        self._centerMapBasedOnMode()

    def start(self):
        super(PveScaleCenteredPersonalEntriesPlugin, self).start()
        g_eventBus.addListener(ScalableBattleMinimapEvent.BORDERS_UPDATED, self._onMinimapBordersUpdated, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(ScalableBattleMinimapEvent.ZOOM_UPDATED, self._onZoomLevelUpdated, EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        super(PveScaleCenteredPersonalEntriesPlugin, self).stop()
        g_eventBus.removeListener(ScalableBattleMinimapEvent.BORDERS_UPDATED, self._onMinimapBordersUpdated, EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(ScalableBattleMinimapEvent.ZOOM_UPDATED, self._onZoomLevelUpdated, EVENT_BUS_SCOPE.BATTLE)

    def _onMinimapBordersUpdated(self, event):
        self._parentObj.setVisibleRect(*event.ctx.get('minimapBorders', PVE_MINIMAP_DEFAULT_BORDERS))

    def _onZoomLevelUpdated(self, event):
        zoomLevel = event.ctx.get('zoomLevel', 0)
        if zoomLevel < PVE_MINIMAP_DEFAULT_ZOOM:
            _logger.warn('zoomLevel is out of scope: %f', zoomLevel)
        self._centerMapBasedOnMode()
        self._parentObj.setZoom(max(PVE_MINIMAP_DEFAULT_ZOOM, zoomLevel))

    def _getPostmortemCenterEntry(self):
        iah = avatar_getter.getInputHandler()
        if iah and iah.ctrls[CTRL_MODE_NAME.POSTMORTEM].altTargetMode == CTRL_MODE_NAME.DEATH_FREE_CAM:
            newEntryID = self._getViewPointID()
        else:
            newEntryID = self._getDeadPointID()
        return newEntryID

    def _centerMapBasedOnMode(self):
        if self._isInPostmortemMode():
            newEntryID = self._getPostmortemCenterEntry()
        elif self._isInStrategicMode():
            newEntryID = self._getCameraIDs()[_S_NAME.STRATEGIC_CAMERA]
        elif self._isInArcadeMode():
            newEntryID = self._getViewPointID()
        elif self._isInVideoMode():
            newEntryID = self._getCameraIDs()[_S_NAME.VIDEO_CAMERA]
        else:
            newEntryID = None
        if newEntryID is not None:
            self._parentObj.setMinimapCenterEntry(newEntryID)
        return


class PveMinimapComponent(PveMinimapMeta):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PveMinimapComponent, self).__init__()
        self._canToggleFullMap = False

    def setVisibleRect(self, bl, tr):
        self.getComponent().setVisibleRect(bl, tr)

    def setZoom(self, zoom):
        self.getComponent().setZoom(zoom)

    def setMinimapCenterEntry(self, entityID):
        self.getComponent().setMinimapCenterEntry(entityID)

    def _createFlashComponent(self):
        return GUI.WGPveMinimapGUIComponentAS3(self.app.movie, settings.MINIMAP_COMPONENT_PATH)

    def _setupPlugins(self, arenaVisitor):
        setup = super(PveMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = PveMinimapGlobalSettingsPlugin
        setup['personal'] = PveScaleCenteredPersonalEntriesPlugin
        return setup

    def _populate(self):
        super(PveMinimapComponent, self)._populate()
        self.as_setGridS(self.getMinimapDimensions(), self.getMinimapDimensions())
        CommandMapping.g_instance.onMappingChanged += self._mappingChangeHandler
        self._setMinimapShortcutLabel()
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged += self._settingsChangeHandler
        self._settingsChangeHandler(WidgetType.MINIMAP)

    def _dispose(self):
        CommandMapping.g_instance.onMappingChanged -= self._mappingChangeHandler
        settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
        if settingsCtrl:
            settingsCtrl.onSettingsChanged -= self._settingsChangeHandler
        super(PveMinimapComponent, self)._dispose()

    def _mappingChangeHandler(self, *_):
        self._setMinimapShortcutLabel()

    def _setMinimapShortcutLabel(self):
        self.as_setShorcutLabelS('' if not self._canToggleFullMap else getReadableKey(CommandMapping.CMD_MINIMAP_VISIBLE))

    def _settingsChangeHandler(self, settingsID):
        if settingsID == WidgetType.MINIMAP:
            settingsCtrl = self._sessionProvider.dynamic.vseHUDSettings
            if settingsCtrl is None:
                return
            minimapSettings = settingsCtrl.getSettings(WidgetType.MINIMAP)
            if not minimapSettings:
                return
            self.as_showGridS(minimapSettings.showGrid)
            self.getComponent().setAnimationParameters(minimapSettings.minimumAnimationDuration, minimapSettings.maximumAnimationDuration, minimapSettings.animationDurationPerMeter, minimapSettings.minimumAnimationDistance)
            if self._canToggleFullMap == minimapSettings.canToggleFullMap:
                return
            self._canToggleFullMap = minimapSettings.canToggleFullMap
            self._setMinimapShortcutLabel()
        return
