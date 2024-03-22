# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/component_marker/markers_components.py
import math
import weakref
import AnimationSequence
import BigWorld
import Math
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from chat_commands_consts import INVALID_TARGET_ID, MarkerType
from ids_generators import SequenceIDGenerator
from account_helpers.settings_core import ISettingsCore, settings_constants
from helpers import dependency
from shared_utils import BitmaskHelper
from vehicle_systems.stricted_loading import makeCallbackWeak
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import ReplyStateForMarker
from gui.Scaleform.daapi.view.battle.shared.indicators import _DIRECT_INDICATOR_SWF as SWF, _DIRECT_INDICATOR_MC_NAME as MC_NAME
from gui.Scaleform.daapi.view.battle.shared.markers2d.settings import MARKER_SYMBOL_NAME, CommonMarkerType
from gui.impl import backport
from gui.impl.gen import R
from debug_utils import LOG_CURRENT_EXCEPTION
import CombatSelectedArea
from gui.battle_control import minimap_utils

def _getDirectionIndicator(swf, mcName):
    indicator = None
    try:
        indicator = indicators.createDirectIndicator(swf, mcName)
    except Exception:
        LOG_CURRENT_EXCEPTION()

    return indicator


class ComponentBitMask(BitmaskHelper):
    NONE = 0
    MARKER_2D = 1
    MINIMAP_MARKER = 2
    DIRECTION_INDICATOR = 4
    ANIM_SEQUENCE_MARKER = 8
    TERRAIN_MARKER = 16
    FULLSCREEN_MAP_MARKER = 32
    LIST = (MARKER_2D,
     MINIMAP_MARKER,
     DIRECTION_INDICATOR,
     ANIM_SEQUENCE_MARKER,
     TERRAIN_MARKER,
     FULLSCREEN_MAP_MARKER)


COMPONENT_MARKER_TYPE_NAMES = dict([ (k, v) for k, v in ComponentBitMask.__dict__.iteritems() if isinstance(v, int) ])
COMPONENT_MARKER_TYPE_IDS = dict([ (v, k) for k, v in COMPONENT_MARKER_TYPE_NAMES.iteritems() ])

class _IMarkerComponentBase(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    _idGen = SequenceIDGenerator()

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(_IMarkerComponentBase, self).__init__()
        self._componentID = self._idGen.next()
        self._config = config
        self._matrixProduct = matrixProduct
        self._isVisible = isVisible
        self._targetID = targetID
        self._entity = weakref.proxy(entity) if entity else None
        return

    @property
    def isVisible(self):
        return self._isVisible

    @property
    def componentID(self):
        return self._componentID

    @property
    def position(self):
        return Math.Matrix(self._matrixProduct.a).translation

    @property
    def positionWithOffset(self):
        return Math.Matrix(self._matrixProduct).translation

    @property
    def maskType(self):
        raise NotImplementedError

    @property
    def bcMarkerType(self):
        return MarkerType.INVALID_MARKER_TYPE

    def update(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def setVisible(self, isVisible):
        pass

    def attachGUI(self, guiProvider, **kwargs):
        pass

    def detachGUI(self):
        pass

    def setMarkerMatrix(self, matrix):
        self._matrixProduct.a = matrix

    def setMarkerEntity(self, entity):
        self._entity = weakref.proxy(entity)

    def setMarkerPosition(self, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        self.setMarkerMatrix(matrix)

    @classmethod
    def configReader(cls, section):
        raise NotImplementedError


class World2DMarkerComponent(_IMarkerComponentBase):
    _METERS_STRING = ' ' + backport.text(R.strings.ingame_gui.marker.meters())

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(World2DMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self._gui = lambda : None
        self._isMarkerExists = False
        self._displayDistance = self._config.get('display_distance', True)
        self._distance = self._config.get('distance', 0)
        self._symbol = self._config['symbol']

    @classmethod
    def configReader(cls, section):
        config = {'shape': section.readString('shape', 'arrow'),
         'min_distance': section.readFloat('min_distance', 0.0),
         'max_distance': section.readFloat('max_distance', 0.0),
         'distance': section.readFloat('distance', 0.0),
         'distanceFieldColor': section.readString('distanceFieldColor', 'yellow'),
         'display_distance': section.readBool('display_distance', True),
         'symbol': section.readString('symbol', MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER)}
        return config

    @property
    def maskType(self):
        return ComponentBitMask.MARKER_2D

    @property
    def guiMarkerType(self):
        return CommonMarkerType.NORMAL

    @property
    def symbol(self):
        return self._symbol

    def attachGUI(self, guiProvider, **kwargs):
        self._gui = weakref.ref(guiProvider.getMarkers2DPlugin())
        self.settingsCore.onSettingsChanged += self._onSettingsChanged
        self._createMarker(**kwargs)
        return self._isMarkerExists

    def detachGUI(self):
        self.settingsCore.onSettingsChanged -= self._onSettingsChanged
        self.clear()

    def clear(self):
        self._deleteMarker()
        self._gui = lambda : None

    def setVisible(self, isVisible):
        if self._isVisible == isVisible:
            return
        else:
            self._isVisible = isVisible
            gui = self._gui()
            if gui is None:
                return
            gui.setMarkerActive(self._componentID, self._isVisible)
            return

    def update(self, distance, *args, **kwargs):
        self._distance = distance
        gui = self._gui()
        if not self._displayDistance:
            distance = -1
        if self._isVisible and self._isMarkerExists and gui:
            gui.markerSetDistance(self._componentID, distance)

    def setMarkerMatrix(self, matrix):
        super(World2DMarkerComponent, self).setMarkerMatrix(matrix)
        gui = self._gui()
        if gui and not self._isMarkerExists:
            gui.setMarkerMatrix(self._componentID, matrix)

    def _createMarker(self, **kwargs):
        gui = self._gui()
        if gui and not self._isMarkerExists:
            self._isMarkerExists = gui.createMarker(self._componentID, self._targetID, self.symbol, self._matrixProduct, self._isVisible, self.bcMarkerType, self.guiMarkerType)
            if self._isMarkerExists:
                self._setupMarker(gui, **kwargs)

    def _deleteMarker(self):
        gui = self._gui()
        if self._isMarkerExists and gui:
            gui.deleteMarker(self._componentID)
        self._isMarkerExists = False
        self._isVisible = False

    def _setupMarker(self, gui, **kwargs):
        config = self._config
        gui.invokeMarker(self._componentID, 'init', config['shape'], config['min_distance'], config['max_distance'], self._distance, self._METERS_STRING, config['distanceFieldColor'])
        return True

    def _onSettingsChanged(self, diff):
        pass


class World2DActionMarkerComponent(World2DMarkerComponent):
    MARKER_CULL_DISTANCE = 1800
    MARKER_MIN_SCALE = 60.0
    MARKER_BOUNDS = Math.Vector4(30, 30, 30, 30)
    MARKER_INNER_BOUNDS = Math.Vector4(17, 17, 18, 18)
    MARKER_BOUND_MIN_SCALE = Math.Vector2(1.0, 1.0)

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(World2DActionMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self._isStickyFromConfig = config.get('is_sticky', True)

    @classmethod
    def configReader(cls, section):
        config = {'shape': section.readString('shape', 'targetPoint'),
         'shapeReplyMe': section.readString('shapeReplyMe', 'targetPointReplyMe'),
         'shapeHighlight': section.readString('shapeHighlight', 'targetPointHighlight'),
         'min_distance': section.readFloat('min_distance', 0.0),
         'max_distance': section.readFloat('max_distance', 0.0),
         'distance': section.readFloat('distance', 0.0),
         'distanceFieldColor': section.readString('distanceFieldColor', 'yellow'),
         'display_distance': section.readBool('display_distance', True),
         'symbol': section.readString('symbol', MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER),
         'is_sticky': section.readBool('is_sticky', True),
         'cull_distance': section.readFloat('cull_distance', cls.MARKER_CULL_DISTANCE),
         'min_scale': section.readFloat('min_scale', cls.MARKER_MIN_SCALE),
         'bounds': section.readVector4('bounds', cls.MARKER_BOUNDS),
         'inner_bounds': section.readVector4('inner_bounds', cls.MARKER_INNER_BOUNDS),
         'bounds_min_scale': section.readVector2('bounds_min_scale', cls.MARKER_BOUND_MIN_SCALE)}
        return config

    @property
    def guiMarkerType(self):
        return CommonMarkerType.TARGET_POINT

    @property
    def bcMarkerType(self):
        return MarkerType.TARGET_POINT_MARKER_TYPE

    @property
    def symbol(self):
        return self._symbol or MARKER_SYMBOL_NAME.TARGET_POINT_MARKER

    def _setupMarker(self, gui, **kwargs):
        config = self._config
        gui.invokeMarker(self._componentID, 'init', config['shape'], config['shapeReplyMe'], config['shapeHighlight'], config['min_distance'], config['max_distance'], self._distance, self._METERS_STRING, config['distanceFieldColor'])
        isSticky = config['is_sticky'] & bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_STICKY_MARKERS))
        gui.setMarkerSticky(self.componentID, isSticky)
        gui.setActiveState(self._componentID, ReplyStateForMarker.CREATE_STATE)
        gui.setMarkerRenderInfo(self._componentID, config['min_scale'], config['bounds'], config['inner_bounds'], config['cull_distance'], config['bounds_min_scale'])
        gui.setMarkerBoundEnabled(self._componentID, True)
        return True

    def _deleteMarker(self):
        gui = self._gui()
        if self._isMarkerExists and gui:
            gui.setMarkerSticky(self._componentID, False)
            gui.setActiveState(self._componentID, ReplyStateForMarker.CREATE_STATE)
            gui.setMarkerReplied(self._componentID, False)
            gui.setMarkerBoundEnabled(self._componentID, False)
            gui.deleteMarker(self._componentID)
        self._isMarkerExists = False
        self._isVisible = False

    def _onSettingsChanged(self, diff):
        gui = self._gui()
        if not gui:
            return
        addSettings = {}
        for item in diff:
            if item in (BattleCommStorageKeys.SHOW_STICKY_MARKERS,):
                addSettings[item] = diff[item]

        if not addSettings:
            return
        newIsSticky = bool(addSettings.get(BattleCommStorageKeys.SHOW_STICKY_MARKERS, self._isStickyFromConfig))
        gui.setMarkerSticky(self.componentID, newIsSticky & self._isStickyFromConfig)


class World2DLocationMarkerComponent(World2DMarkerComponent):
    CULL_DISTANCE = 1800
    MIN_SCALE = 50.0
    BOUNDS = Math.Vector4(30, 30, 90, -15)
    INNER_BOUNDS = Math.Vector4(15, 15, 70, -35)
    BOUNDS_MIN_SCALE = Math.Vector2(1.0, 0.8)
    MIN_Y_OFFSET = 1.2
    MAX_Y_OFFSET = 3.2
    DISTANCE_FOR_MIN_Y_OFFSET = 400
    MAX_Y_BOOST = 1.4
    BOOST_START = 120

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(World2DLocationMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self._isStickyFromConfig = config.get('is_sticky', True)

    @classmethod
    def configReader(cls, section):
        config = {'symbol': section.readString('symbol', MARKER_SYMBOL_NAME.LOCATION_MARKER),
         'cull_distance': section.readFloat('cull_distance', cls.CULL_DISTANCE),
         'min_scale': section.readFloat('min_scale', cls.MIN_SCALE),
         'bounds': section.readVector4('bounds', cls.BOUNDS),
         'inner_bounds': section.readVector4('inner_bounds', cls.INNER_BOUNDS),
         'bounds_min_scale': section.readVector2('bounds_min_scale', cls.BOUNDS_MIN_SCALE),
         'is_sticky': section.readBool('is_sticky', True),
         'min_y_offset': section.readFloat('min_y_offset', cls.MIN_Y_OFFSET),
         'max_y_offset': section.readFloat('max_y_offset', cls.MAX_Y_OFFSET),
         'max_y_boost': section.readFloat('max_y_boost', cls.MAX_Y_BOOST),
         'distance_for_min_y_offset': section.readFloat('distance_for_min_y_offset', cls.DISTANCE_FOR_MIN_Y_OFFSET),
         'boost_start': section.readFloat('boost_start', cls.BOOST_START)}
        return config

    @property
    def guiMarkerType(self):
        return CommonMarkerType.LOCATION

    @property
    def bcMarkerType(self):
        return MarkerType.TARGET_POINT_MARKER_TYPE

    @property
    def symbol(self):
        return self._symbol or MARKER_SYMBOL_NAME.LOCATION_MARKER

    def update(self, distance, *args, **kwargs):
        pass

    def _setupMarker(self, gui, **kwargs):
        config = self._config
        isSticky = config['is_sticky'] & bool(self.settingsCore.getSetting(BattleCommStorageKeys.SHOW_STICKY_MARKERS))
        gui.setMarkerSticky(self._componentID, isSticky)
        gui.setMarkerRenderInfo(self._componentID, config['min_scale'], config['bounds'], config['inner_bounds'], config['cull_distance'], config['bounds_min_scale'])
        gui.setMarkerLocationOffset(self._componentID, config['min_y_offset'], config['max_y_offset'], config['distance_for_min_y_offset'], config['max_y_boost'], config['boost_start'])

    def _onSettingsChanged(self, diff):
        gui = self._gui()
        if not gui:
            return
        addSettings = {}
        for item in diff:
            if item in (BattleCommStorageKeys.SHOW_STICKY_MARKERS,):
                addSettings[item] = diff[item]

        if not addSettings:
            return
        newIsSticky = bool(addSettings.get(BattleCommStorageKeys.SHOW_STICKY_MARKERS, self._isStickyFromConfig))
        gui.setMarkerSticky(self.componentID, newIsSticky & self._isStickyFromConfig)


class BaseMinimapMarkerComponent(_IMarkerComponentBase):

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(BaseMinimapMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self._gui = lambda : None
        self._isMarkerExists = False
        self._onlyTranslation = self._config.get('onlyTranslation', False)
        self._translationOnlyMP = Math.WGTranslationOnlyMP()
        self._translationOnlyMP.source = self._matrixProduct.a

    @classmethod
    def configReader(cls, section):
        config = {'symbol': section.readString('symbol', 'ArtyMarkerMinimapEntry'),
         'container': section.readString('container', 'personal'),
         'onlyTranslation': section.readBool('onlyTranslation', False)}
        return config

    @property
    def maskType(self):
        raise NotImplementedError

    def attachGUI(self, guiProvider, **kwargs):
        self._gui = weakref.ref(self._getPlugin(guiProvider))
        self._createMarker(**kwargs)
        return self._isMarkerExists

    def detachGUI(self):
        self.clear()

    def clear(self):
        self._deleteMarker()
        self._gui = lambda : None

    def setVisible(self, isVisible):
        if self._isVisible == isVisible:
            return
        else:
            self._isVisible = isVisible
            gui = self._gui()
            if gui is None:
                return
            gui.setActive(self._componentID, self._isVisible)
            return

    def _createMarker(self, **kwargs):
        gui = self._gui()
        if gui and not self._isMarkerExists:
            matrix = self._translationOnlyMP if self._onlyTranslation else self._matrixProduct.a
            self._isMarkerExists = gui.createMarker(self._componentID, self._config['symbol'], self._config['container'], matrix=matrix, active=self._isVisible)
            if self._isMarkerExists:
                self._setupMarker(gui, **kwargs)

    def _deleteMarker(self):
        gui = self._gui()
        if self._isMarkerExists and gui:
            gui.deleteMarker(self._componentID)
        self._isMarkerExists = False
        self._isVisible = False

    def update(self, *args, **kwargs):
        gui = self._gui()
        if self._isVisible and gui and self._isMarkerExists:
            gui.update(self._componentID, *args, **kwargs)

    def setMarkerMatrix(self, matrix):
        super(BaseMinimapMarkerComponent, self).setMarkerMatrix(matrix)
        self._translationOnlyMP.source = self._matrixProduct.a
        gui = self._gui()
        if gui and self._isMarkerExists:
            mtx = self._translationOnlyMP if self._onlyTranslation else self._matrixProduct.a
            gui.setMatrix(self._componentID, mtx)

    def _getPlugin(self, guiProvider):
        return guiProvider.getFullscreenMapPlugin() if self.maskType == ComponentBitMask.FULLSCREEN_MAP_MARKER else guiProvider.getMinimapPlugin()

    def _setupMarker(self, gui, **kwargs):
        pass


class MinimapMarkerComponent(BaseMinimapMarkerComponent):

    @property
    def maskType(self):
        return ComponentBitMask.MINIMAP_MARKER


class FullscreenMapComponent(BaseMinimapMarkerComponent):

    @property
    def maskType(self):
        return ComponentBitMask.FULLSCREEN_MAP_MARKER


class DirectionIndicatorMarkerComponent(_IMarkerComponentBase):
    _DIRECT_INDICATOR_SWF = SWF
    _DIRECT_INDICATOR_MC_NAME = MC_NAME

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(DirectionIndicatorMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self.__shapes = self._config['dIndicatorShapes']
        self.__indicator = None
        self.__prevPosition = self.positionWithOffset
        self.__swf = self._config['swf']
        self.__mcName = self._config['mcName']
        return

    @classmethod
    def configReader(cls, section):
        config = {'dIndicatorShapes': (section.readString('dIndicatorShapes/default', 'green'), section.readString('dIndicatorShapes/colorBlind', 'green')),
         'swf': section.readString('swf', cls._DIRECT_INDICATOR_SWF),
         'mcName': section.readString('mcName', cls._DIRECT_INDICATOR_MC_NAME)}
        return config

    @property
    def maskType(self):
        return ComponentBitMask.DIRECTION_INDICATOR

    def attachGUI(self, _, **kwargs):
        if self.__indicator is None:
            self.__indicator = _getDirectionIndicator(self.__swf, self.__mcName)
            self.__indicator.setShape(self.__currentShape)
            self.__indicator.track(self.positionWithOffset)
        if not self.__indicator:
            return False
        else:
            self.settingsCore.onSettingsChanged += self.__onSettingsChanged
            self.__indicator.setPosition(self.positionWithOffset)
            self.__indicator.setVisibility(self._isVisible)
            return True

    def detachGUI(self):
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.clear()

    def update(self, distance, *args, **kwargs):
        if self.__indicator is None:
            return
        else:
            self.__indicator.setDistance(distance)
            currentPosition = self.positionWithOffset
            if currentPosition != self.__prevPosition:
                self.__indicator.setPosition(currentPosition)
                self.__prevPosition = currentPosition
            return

    def clear(self):
        if self.__indicator is None:
            return
        else:
            self.setVisible(False)
            self.__indicator.remove()
            self.__indicator = None
            return

    def setVisible(self, isVisible):
        if not self._isVisible and isVisible:
            self.__updateVisibility()
        elif self._isVisible and not isVisible:
            self._isVisible = False
            if self.__indicator is not None:
                self.__indicator.setVisibility(False)
        if self._isVisible and self.__indicator:
            self.__indicator.setPosition(self.positionWithOffset)
        return

    def __updateVisibility(self):
        if self.__indicator is not None:
            if not hasattr(BigWorld.player().inputHandler.ctrl, 'camera'):
                return
            self._isVisible = True
            camera = BigWorld.player().inputHandler.ctrl.camera.camera
            camMat = Math.Matrix(camera.invViewMatrix)
            if camMat is not None:
                view = camMat.applyV4Point(Math.Vector4(0, 0, 1, 0))
                direction = self.positionWithOffset - BigWorld.player().getOwnVehiclePosition()
                dotProduct = direction.dot(view[0:3])
                cosFov = math.cos(BigWorld.projection().fov / 2)
                if dotProduct > cosFov * direction.length:
                    self._isVisible = False
            self.__indicator.setVisibility(self._isVisible)
        return

    @property
    def __currentShape(self):
        return self.__shapes[1] if self.settingsCore.getSetting('isColorBlind') else self.__shapes[0]

    def __onSettingsChanged(self, diff):
        if self.__indicator is None:
            return
        else:
            if 'isColorBlind' in diff:
                self.__indicator.setShape(self.__currentShape)
            return


class AnimationSequenceMarkerComponent(_IMarkerComponentBase):

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(AnimationSequenceMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self.__path = self._config['path']
        self.__animator = None
        self.__spaceID = BigWorld.player().spaceID
        if self.__path is not None:
            loader = AnimationSequence.Loader(self.__path, self.__spaceID)
            BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onSequenceLoaded))
        return

    @classmethod
    def configReader(cls, section):
        config = {'path': section.readString('path')}
        return config

    @property
    def maskType(self):
        return ComponentBitMask.ANIM_SEQUENCE_MARKER

    def clear(self):
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
        return

    def update(self, *args, **kwargs):
        if self.__animator:
            self.__animator.bindToWorld(Math.Matrix(self._matrixProduct))

    def setVisible(self, isVisible):
        if self._isVisible == isVisible:
            return
        self._isVisible = isVisible
        if not self.__animator:
            return
        if self._isVisible:
            self.__animator.setEnabled(True)
            self.__animator.start()
        else:
            self.__animator.setEnabled(False)
            self.__animator.stop()

    def __onSequenceLoaded(self, resourceRefs):
        if self.__path in resourceRefs.failedIDs:
            return
        self.__animator = resourceRefs[self.__path]
        self.__animator.bindToWorld(Math.Matrix(self._matrixProduct))
        if self._isVisible:
            self.__animator.start()


class TerrainMarkerComponent(_IMarkerComponentBase):
    DEF_SIZE = (10, 10)
    DEF_DIRECTION = Math.Vector3(1.0, 0.0, 0.0)
    DEF_COLOR = CombatSelectedArea.COLOR_WHITE

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(TerrainMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self.__area = CombatSelectedArea.CombatSelectedArea()
        self.__direction = self._config['direction']
        self.__objDirection = self._config['objDirection']
        path = self._config['path']
        size = self._config['size']
        color = self._config['color']
        direction = Math.Matrix(self._matrixProduct.a).applyToAxis(2) if self.__objDirection else self.__direction
        self.__area.setup(self.position, direction, size, path, color, None)
        self.__area.setGUIVisible(self._isVisible)
        self.__prevPosition = self.position
        return

    @classmethod
    def configReader(cls, section):
        config = {'path': section.readString('path'),
         'size': section.readVector2('size', cls.DEF_SIZE),
         'direction': section.readVector3('direction', cls.DEF_DIRECTION),
         'objDirection': section.readBool('objDirection', True),
         'color': int(section.readString('color', '0'), 16) or cls.DEF_COLOR}
        return config

    @property
    def maskType(self):
        return ComponentBitMask.TERRAIN_MARKER

    def clear(self):
        if self.__area is not None:
            self.__area.destroy()
            self.__area = None
        return

    def update(self, *args, **kwargs):
        currentPosition = self.position
        if self.__area and currentPosition != self.__prevPosition:
            direction = Math.Matrix(self._matrixProduct.a).applyToAxis(2) if self.__objDirection else self.__direction
            self.__area.relocate(currentPosition, direction)
            self.__prevPosition = currentPosition

    def setVisible(self, isVisible):
        if self._isVisible == isVisible:
            return
        self._isVisible = isVisible
        if not self.__area:
            return
        self.__area.setGUIVisible(self._isVisible)


class PolygonalZoneMinimapMarkerComponent(MinimapMarkerComponent):

    class Blending(object):
        NORMAL = 'normal'
        ADD = 'add'
        MULTIPLY = 'multiply'
        SCREEN = 'screen'
        SUBTRACT = 'subtract'

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(PolygonalZoneMinimapMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self._polygon = None
        self._isBorderVisible = False
        self._maskingPolygons = []
        self._properties = config['color']
        return

    @classmethod
    def configReader(cls, section):
        config = super(PolygonalZoneMinimapMarkerComponent, cls).configReader(section)
        colorSection = section['color']
        color = {}
        for colorType in ('default', 'colorBlind'):
            colorTypeSection = colorSection[colorType]
            color.update({colorType: {'fillColor': int(colorTypeSection.readString('fillColor', '0'), 16),
                         'fillAlpha': colorTypeSection.readFloat('fillAlpha'),
                         'fillBlendMode': colorTypeSection.readString('fillBlendMode', cls.Blending.NORMAL),
                         'outlineColor': int(colorTypeSection.readString('outlineColor', '0'), 16),
                         'outlineAlpha': colorTypeSection.readFloat('outlineAlpha'),
                         'outlineBlendMode': colorTypeSection.readString('outlineBlendMode', cls.Blending.NORMAL),
                         'lineThickness': colorTypeSection.readFloat('lineThickness'),
                         'useGradient': colorTypeSection.readBool('useGradient', False),
                         'gradientColor': int(colorTypeSection.readString('gradientColor', '0'), 16),
                         'gradientAlpha': colorTypeSection.readFloat('gradientAlpha', 1.0)}})

        config.update({'color': color})
        return config

    @property
    def isVisible(self):
        return self._entity.entityPolygonalTrigger.isActive and self._entity.clientVisualComp.isVisible

    def getPolygon(self):
        udo = BigWorld.userDataObjects.get(self._entity.clientVisualComp.udoGuid, None)
        return [] if udo is None else udo.minimapMarkerPolygon

    def _setupMarker(self, gui, **kwargs):
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self._entity.onMaskAdded += self._addMask
        self._initPolygon()
        if self._polygon:
            self._updatePolygon()

    def detachGUI(self):
        super(PolygonalZoneMinimapMarkerComponent, self).detachGUI()
        self._polygon = None
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self._entity.onMaskAdded -= self._addMask
        return

    def update(self, *args, **kwargs):
        super(PolygonalZoneMinimapMarkerComponent, self).update(*args, **kwargs)
        gui = self._gui()
        if not self._isVisible or not gui or not self._isMarkerExists:
            return
        newIsVisible = self.isVisible
        if self._isBorderVisible == newIsVisible:
            return
        self._isBorderVisible = newIsVisible
        gui.setActive(self._componentID, self._isBorderVisible and self._isVisible)

    def setVisible(self, isVisible):
        if self._isVisible == isVisible:
            return
        else:
            self._isVisible = isVisible
            gui = self._gui()
            if gui is None:
                return
            gui.setActive(self._componentID, self._isBorderVisible and self._isVisible)
            return

    def _addMask(self, guid):
        arenaSize = BigWorld.player().arena.arenaType.boundingBox[1]
        xc = minimap_utils.MINIMAP_SIZE[0] / arenaSize[0]
        yc = minimap_utils.MINIMAP_SIZE[1] / arenaSize[1]
        udo = BigWorld.userDataObjects.get(guid, None)
        if udo:
            delta = udo.position - self.position
            polygon = sum(([(p[0] + delta[0]) * xc, (p[1] - delta[2]) * yc] for p in udo.minimapMarkerPolygon), list())
            self._gui().invoke(self._componentID, 'addZoneData', polygon)
        return

    def _initPolygon(self):
        polygon = self.getPolygon()
        if not polygon:
            return
        else:
            arenaSize = BigWorld.player().arena.arenaType.boundingBox[1]
            xc = minimap_utils.MINIMAP_SIZE[0] / arenaSize[0]
            yc = minimap_utils.MINIMAP_SIZE[1] / arenaSize[1]
            self._polygon = sum(([p[0] * xc, p[1] * yc] for p in polygon), list())
            for mask in self._entity.masks:
                udo = BigWorld.userDataObjects.get(mask.udoGuid, None)
                if udo:
                    delta = udo.position - self.position
                    self._maskingPolygons.append(sum(([(p[0] + delta[0]) * xc, (p[1] - delta[2]) * yc] for p in udo.minimapMarkerPolygon), list()))

            return

    def _updatePolygon(self):
        self._gui().invoke(self._componentID, 'setProperties', *self.__getMarkerProperties(self.__isColorBlind()))
        self._gui().invoke(self._componentID, 'addZoneData', self._polygon)
        self._gui().setActive(self._componentID, self._isBorderVisible and self._isVisible)
        for polygon in self._maskingPolygons:
            self._gui().invoke(self._componentID, 'addZoneData', polygon)

    def _getGradientSize(self):
        dimensions = self._entity.clientVisualComp.getDimensions()
        return max(dimensions.x, dimensions.z) / 2

    def __getMarkerProperties(self, isColorBlind):
        props = self._properties['default'] if not isColorBlind else self._properties['colorBlind']
        return (props['fillColor'],
         props['fillAlpha'],
         props['outlineColor'],
         props['outlineAlpha'],
         props['lineThickness'],
         props['fillBlendMode'],
         props['outlineBlendMode'],
         props['useGradient'],
         props['gradientColor'],
         props['gradientAlpha'],
         self._getGradientSize())

    def __isColorBlind(self):
        return self.settingsCore.getSetting(settings_constants.GRAPHICS.COLOR_BLIND)

    def __onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            self._gui().invoke(self._componentID, 'setProperties', *self.__getMarkerProperties(self.__isColorBlind()))


class StaticDeathZoneMinimapMarkerComponent(PolygonalZoneMinimapMarkerComponent):

    @property
    def isVisible(self):
        return self._entity.isActive

    def getPolygon(self):
        p = self._entity.position
        min, max = self._entity.clientVisualComp.getCorners()
        return [(min.x - p.x, min.z - p.z),
         (min.x - p.x, max.z - p.z),
         (max.x - p.x, max.z - p.z),
         (max.x - p.x, min.z - p.z)]
