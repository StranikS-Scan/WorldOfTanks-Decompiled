# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/entity_markers/__init__.py
from constants import MarkerItem
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from halloween.gui.Scaleform.daapi.view.battle.entity_markers import markers_components
HW_MARKERS = {MarkerItem.HW_PICKUP_PLACEMENT: {ComponentBitMask.MARKER_2D: [{'displayDistance': True,
                                                                'isSticky': True,
                                                                'distanceFieldColor': 'white',
                                                                'clazz': markers_components.HWPickupPlacementMarkerComponent}],
                                  ComponentBitMask.MINIMAP_MARKER: [{'symbol': 'HWBuffMinimapEntryUI',
                                                                     'container': CONTAINER_NAME.EQUIPMENTS,
                                                                     'clazz': markers_components.HWPickupPlacementMinimapMarkerComponent,
                                                                     'onlyTranslation': True}]},
 MarkerItem.HW_PICKUP_SPAWNED: {ComponentBitMask.MARKER_2D: [{'displayDistance': True,
                                                              'isSticky': True,
                                                              'distanceFieldColor': 'white',
                                                              'clazz': markers_components.HWPickupSpawnedMarkerComponent}],
                                ComponentBitMask.MINIMAP_MARKER: [{'symbol': 'HWBuffMinimapEntryUI',
                                                                   'container': CONTAINER_NAME.EQUIPMENTS,
                                                                   'clazz': markers_components.HWPickupSpawnedMinimapMarkerComponent,
                                                                   'onlyTranslation': True}]},
 MarkerItem.HW_TEAM_BASE: {'offset': settings.MARKER_POSITION_ADJUSTMENT,
                           ComponentBitMask.MARKER_2D: [{'displayDistance': True,
                                                         'isSticky': True,
                                                         'distanceFieldColor': 'white',
                                                         'clazz': markers_components.HWTeamBaseMarkerComponent}],
                           ComponentBitMask.MINIMAP_MARKER: [{'symbol': 'HWSectorBaseMinimapAllyEntryUI',
                                                              'container': CONTAINER_NAME.TEAM_POINTS,
                                                              'clazz': markers_components.HWTeamBaseMinimapMarkerComponent,
                                                              'onlyTranslation': True}]}}
