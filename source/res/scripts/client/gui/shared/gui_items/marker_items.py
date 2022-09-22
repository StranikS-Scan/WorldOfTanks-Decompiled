# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/marker_items.py
from enum import IntEnum, unique
import Math
from gui.Scaleform.daapi.view.battle.event import markers as EventMarkers
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask as FLAG
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME, ENTRY_SYMBOL_NAME

@unique
class MarkerItem(IntEnum):
    DEFAULT = 1
    DEATHZONE = 2
    BOMB = 3
    CAMP = 4
    GEN_ON = 5
    GEN_OFF = 6


class MarkerParamsFactory(object):
    MARKER_DATA = {MarkerItem.DEFAULT: {'visible': True,
                          'areaRadius': 5.0,
                          'disappearingRadius': 0.0,
                          'reverseDisappearing': False,
                          'offset': (0, 10, 0),
                          FLAG.MARKER_2D: [{'shape': 'arrow',
                                            'min-distance': 0.0,
                                            'max-distance': 0.0,
                                            'distance': 0.0,
                                            'distanceFieldColor': 'white'}],
                          FLAG.DIRECTION_INDICATOR: [{'dIndicatorShapes': ('green', 'green')}],
                          FLAG.MINIMAP_MARKER: [{'symbol': ENTRY_SYMBOL_NAME.ARTY_MARKER,
                                                 'container': CONTAINER_NAME.PERSONAL,
                                                 'onlyTranslation': False}, {'symbol': ENTRY_SYMBOL_NAME.BOMBER_ENTRY,
                                                 'container': CONTAINER_NAME.EQUIPMENTS,
                                                 'onlyTranslation': True}],
                          FLAG.ANIM_SEQUENCE_MARKER: [{'path': 'content/Interface/Arrow/animations/bootcamp_arrow.seq'}],
                          FLAG.TERRAIN_MARKER: [{'path': 'content/Interface/TargetPoint/TargetPoint_red.visual',
                                                 'size': (50.0, 20.0),
                                                 'direction': (1.0, 0.0, 0.0),
                                                 'objDirection': True,
                                                 'color': 4294967295L}]},
     MarkerItem.DEATHZONE: {'visible': True,
                            'areaRadius': 5.0,
                            'disappearingRadius': 50.0,
                            'reverseDisappearing': True,
                            'offset': (0, 10, 0),
                            FLAG.MARKER_2D: [{'shape': 'deathZone',
                                              'min-distance': 0.0,
                                              'max-distance': 0.0,
                                              'distance': 0.0,
                                              'distanceFieldColor': 'white'}]},
     MarkerItem.BOMB: {FLAG.MINIMAP_MARKER: [{'clazz': EventMarkers.MinimapBombMarkerComponent,
                                              'symbol': 'EventBombMinimapEntryUI',
                                              'container': CONTAINER_NAME.PERSONAL,
                                              'onlyTranslation': True}],
                       FLAG.MARKER_2D: [{'clazz': EventMarkers.World2DBombMarkerComponent,
                                         'isSticky': True}]},
     MarkerItem.CAMP: {FLAG.MINIMAP_MARKER: [{'clazz': EventMarkers.MinimapCampMarkerComponent,
                                              'symbol': 'EventCampMinimapEntryUI',
                                              'container': CONTAINER_NAME.ICONS,
                                              'onlyTranslation': True}],
                       FLAG.MARKER_2D: [{'clazz': EventMarkers.World2DCampMarkerComponent,
                                         'isSticky': True,
                                         'alpha': 1.0}]},
     MarkerItem.GEN_ON: {FLAG.MINIMAP_MARKER: [{'clazz': EventMarkers.MinimapGeneratorMarkerComponent,
                                                'symbol': 'EventGeneratorMinimapEntryUI',
                                                'container': CONTAINER_NAME.ICONS,
                                                'onlyTranslation': True,
                                                'alpha': 1.0}],
                         FLAG.MARKER_2D: [{'clazz': EventMarkers.World2DGeneratorMarkerComponent,
                                           'isSticky': True,
                                           'alpha': 1.0}]},
     MarkerItem.GEN_OFF: {FLAG.MINIMAP_MARKER: [{'clazz': EventMarkers.MinimapGeneratorMarkerComponent,
                                                 'symbol': 'EventGeneratorMinimapEntryUI',
                                                 'container': CONTAINER_NAME.ICONS,
                                                 'onlyTranslation': True,
                                                 'alpha': 0.5}],
                          FLAG.MARKER_2D: [{'clazz': EventMarkers.World2DGeneratorMarkerComponent,
                                            'isSticky': False,
                                            'alpha': 0.5}]}}

    @classmethod
    def getMarkerParams(cls, matrix, markerStyle=MarkerItem.DEFAULT, bitMask=FLAG.NONE):
        params = cls.MARKER_DATA.get(markerStyle, {})
        if bitMask == FLAG.NONE:
            bitMask = MarkerParamsFactory.buildBitMask(params)
        offset = params.get('offset', (0, 0, 0))
        mp = Math.MatrixProduct()
        mp.a = matrix
        mp.b = Math.Matrix()
        mp.b.translation = offset
        params.update({'matrixProduct': mp,
         'bitMask': bitMask})
        return params

    @classmethod
    def buildBitMask(cls, params):
        bitMask = FLAG.NONE
        for key in params.iterkeys():
            if key in FLAG.LIST:
                bitMask |= key

        return bitMask
