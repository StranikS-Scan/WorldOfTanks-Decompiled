# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/manager.py
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.shared.gui_items.marker_items import MarkerParamsFactory, MarkerItem
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask as FLAG
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import markers as WhiteTigerMarkers
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.plugins import WhiteTigerVehicleMarkerPlugin, WhiteTigerEventBusPlugin, WhiteTigerBaseAreaMarkerPlugin
WT_MARKERS = {MarkerItem.ANOMALY: {FLAG.MINIMAP_MARKER: [{'clazz': WhiteTigerMarkers.AnomalyMarkerComponent,
                                             'symbol': 'WTAnomalyMinimapEntryUI',
                                             'container': CONTAINER_NAME.ICONS,
                                             'onlyTranslation': True}]},
 MarkerItem.GEN_ON: {FLAG.MARKER_2D: [{'symbol': WhiteTigerVehicleMarkerPlugin.WT_GENERATOR_MARKER,
                                       'clazz': WhiteTigerMarkers.World2DGeneratorMarkerComponentOn,
                                       'alpha': 1,
                                       'isSticky': True}],
                     FLAG.MINIMAP_MARKER: [{'clazz': WhiteTigerMarkers.MinimapGeneratorMarkerComponentOn,
                                            'symbol': 'WTGeneratorMinimapEntryUI',
                                            'container': CONTAINER_NAME.ICONS,
                                            'onlyTranslation': True,
                                            'alpha': 1}]},
 MarkerItem.GEN_OFF: {FLAG.MARKER_2D: [{'symbol': WhiteTigerVehicleMarkerPlugin.WT_GENERATOR_MARKER,
                                        'clazz': WhiteTigerMarkers.World2DGeneratorMarkerComponentOff,
                                        'alpha': 0.5,
                                        'isSticky': True}],
                      FLAG.MINIMAP_MARKER: [{'clazz': WhiteTigerMarkers.MinimapGeneratorMarkerComponentOff,
                                             'symbol': 'WTGeneratorMinimapEntryUI',
                                             'container': CONTAINER_NAME.ICONS,
                                             'onlyTranslation': True,
                                             'alpha': 0.5}]},
 MarkerItem.DOME: {'offset': (0, 20, 0),
                   FLAG.MARKER_2D: [{'symbol': WhiteTigerVehicleMarkerPlugin.WT_DOME_MARKER,
                                     'clazz': WhiteTigerMarkers.World2DIndexedMarkerComponent,
                                     'isSticky': False}]}}

class WhiteTigerMarkersManager(MarkersManager):
    MARKERS_MANAGER_SWF = 'white_tiger|white_tiger_battle_vehicle_markers.swf'

    def _setupPlugins(self, arenaVisitor):
        setup = super(WhiteTigerMarkersManager, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = WhiteTigerVehicleMarkerPlugin
        setup['eventBus'] = WhiteTigerEventBusPlugin
        setup['area_markers'] = WhiteTigerBaseAreaMarkerPlugin
        return setup

    def startPlugins(self):
        super(WhiteTigerMarkersManager, self).startPlugins()
        MarkerParamsFactory.MARKER_DATA.update(WT_MARKERS)
