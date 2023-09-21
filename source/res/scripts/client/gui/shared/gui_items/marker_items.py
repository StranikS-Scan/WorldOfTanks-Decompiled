# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/marker_items.py
import copy
import Math
from constants import MarkerItem
from gui.Scaleform.daapi.view.battle.event import markers as EventMarkers
from gui.Scaleform.daapi.view.battle.shared.component_marker import markers_components
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask as FLAG
from gui.Scaleform.daapi.view.battle.shared.indicators import _DIRECT_INDICATOR_SWF, _DIRECT_INDICATOR_MC_NAME
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME, ENTRY_SYMBOL_NAME
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.impl import backport
from gui.impl.gen import R

class MarkerParamsFactory(object):
    ZONE_MARKER_DEFAULT_COLOR_SETTINGS = {'default': {'fillColor': 16729670,
                 'fillAlpha': 0.25,
                 'fillBlendMode': markers_components.PolygonalZoneMinimapMarkerComponent.Blending.NORMAL,
                 'outlineColor': 16740967,
                 'outlineAlpha': 0.45,
                 'outlineBlendMode': markers_components.PolygonalZoneMinimapMarkerComponent.Blending.NORMAL,
                 'lineThickness': 3.0},
     'colorBlind': {'fillColor': 6840319,
                    'fillAlpha': 0.4,
                    'fillBlendMode': markers_components.PolygonalZoneMinimapMarkerComponent.Blending.NORMAL,
                    'outlineColor': 11644159,
                    'outlineAlpha': 0.6,
                    'outlineBlendMode': markers_components.PolygonalZoneMinimapMarkerComponent.Blending.NORMAL,
                    'lineThickness': 3.0}}
    MARKER_DATA = {MarkerItem.DEFAULT: {'visible': True,
                          'areaRadius': 5.0,
                          'disappearingRadius': 0.0,
                          'reverseDisappearing': False,
                          'offset': (0, 10, 0),
                          FLAG.MARKER_2D: [{'shape': 'arrow',
                                            'min-distance': 0.0,
                                            'max-distance': 0.0,
                                            'distance': 0.0,
                                            'distanceFieldColor': 'white',
                                            'symbol': settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER}],
                          FLAG.DIRECTION_INDICATOR: [{'dIndicatorShapes': ('green', 'green'),
                                                      'swf': _DIRECT_INDICATOR_SWF,
                                                      'mcName': _DIRECT_INDICATOR_MC_NAME}],
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
     MarkerItem.STATIC_DEATH_ZONE_PROXIMITY: {'visible': True,
                                              'areaRadius': 0.0,
                                              'disappearingRadius': 50.0,
                                              'reverseDisappearing': True,
                                              'offset': (0, 10, 0),
                                              FLAG.MARKER_2D: [{'shape': 'deathZone',
                                                                'min-distance': 0.0,
                                                                'max-distance': 0.0,
                                                                'distance': 0.0,
                                                                'distanceFieldColor': 'orange',
                                                                'metersString': ' ' + backport.text(R.strings.ingame_gui.marker.meters())}]},
     MarkerItem.COMP7_RECON: {FLAG.MINIMAP_MARKER: [{'symbol': ENTRY_SYMBOL_NAME.COMP7_RECON,
                                                     'container': CONTAINER_NAME.EQUIPMENTS}]},
     MarkerItem.POLYGONAL_ZONE: {'visible': True,
                                 FLAG.MINIMAP_MARKER: [{'symbol': 'CustomDeathZoneMinimapEntryUI',
                                                        'container': CONTAINER_NAME.FLAGS,
                                                        'clazz': markers_components.PolygonalZoneMinimapMarkerComponent,
                                                        'color': ZONE_MARKER_DEFAULT_COLOR_SETTINGS}]},
     MarkerItem.STATIC_DEATH_ZONE: {'visible': True,
                                    FLAG.MINIMAP_MARKER: [{'symbol': 'CustomDeathZoneMinimapEntryUI',
                                                           'container': CONTAINER_NAME.FLAGS,
                                                           'clazz': markers_components.StaticDeathZoneMinimapMarkerComponent,
                                                           'color': ZONE_MARKER_DEFAULT_COLOR_SETTINGS}]},
     MarkerItem.GEN_ON: {FLAG.MARKER_2D: [{'symbol': settings.MARKER_SYMBOL_NAME.EVENT_GENERATOR_MARKER,
                                           'clazz': EventMarkers.World2DGeneratorMarkerComponentOn,
                                           'alpha': 1,
                                           'isSticky': True}],
                         FLAG.MINIMAP_MARKER: [{'clazz': EventMarkers.MinimapGeneratorMarkerComponentOn,
                                                'symbol': 'EventGeneratorMinimapEntryUI',
                                                'container': CONTAINER_NAME.ICONS,
                                                'onlyTranslation': True,
                                                'alpha': 1}]},
     MarkerItem.GEN_OFF: {FLAG.MARKER_2D: [{'symbol': settings.MARKER_SYMBOL_NAME.EVENT_GENERATOR_MARKER,
                                            'clazz': EventMarkers.World2DGeneratorMarkerComponentOff,
                                            'alpha': 0.5,
                                            'isSticky': True}],
                          FLAG.MINIMAP_MARKER: [{'clazz': EventMarkers.MinimapGeneratorMarkerComponentOff,
                                                 'symbol': 'EventGeneratorMinimapEntryUI',
                                                 'container': CONTAINER_NAME.ICONS,
                                                 'onlyTranslation': True,
                                                 'alpha': 0.5}]}}

    @classmethod
    def getMarkerParams(cls, matrix, markerStyle=MarkerItem.DEFAULT, bitMask=FLAG.NONE):
        params = copy.deepcopy(cls.MARKER_DATA.get(markerStyle, {}))
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
