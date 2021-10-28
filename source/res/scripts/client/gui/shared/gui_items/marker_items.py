# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/marker_items.py
from enum import IntEnum
import Math
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask as FLAG
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME, ENTRY_SYMBOL_NAME

class MarkerItem(IntEnum):
    DEFAULT = 0
    DEATHZONE = 1
    SAFEZONE = 2


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
     MarkerItem.SAFEZONE: {'visible': True,
                           'areaRadius': 0.0,
                           'disappearingRadius': 0.0,
                           'reverseDisappearing': False,
                           'offset': (0, 10, 0),
                           'size': (0, 0)}}

    @classmethod
    def getMarkerParams(cls, matrix, markerStyle=MarkerItem.DEFAULT, bitMask=FLAG.NONE):
        params = cls.MARKER_DATA.get(markerStyle, {})
        if bitMask == FLAG.NONE:
            bitMask = MarkerParamsFactory.buildBitMask(params)
        offset = params.get('offset', (0, 10, 0))
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
