# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/marker_component.py
import typing
import logging
import CGF
import Event
from GenericComponents import TransformComponent, EntityGOSync
import math_utils
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cache import cached_property
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from helpers import dependency
from constants import IS_CLIENT, IS_CGF_DUMP
import Math
if IS_CLIENT:
    from skeletons.gui.battle_session import IBattleSessionProvider
    from CurrentVehicle import g_currentPreviewVehicle
    from skeletons.gui.app_loader import IAppLoader
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.Scaleform.framework.entities.View import ViewKey
    from gui.app_loader.settings import APP_NAME_SPACE
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers import AreaMarker
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask
else:

    class IBattleSessionProvider(object):
        pass


    class IAppLoader(object):
        pass


if typing.TYPE_CHECKING:
    import BigWorld
_logger = logging.getLogger(__name__)

class LobbyFlashMarker(CGFComponent):
    icon = ComponentProperty(type=CGFMetaTypes.STRING, editorName='marker icon', value='gui/maps/icons/marathon/marker/video.png', annotations={'path': '*.png'})
    textKey = ComponentProperty(type=CGFMetaTypes.STRING, editorName='marker text key', value='#marathon:3dObject/showVideo')


class LobbyFlashMarkerVisibility(CGFComponent):
    mainTankMarkerGO = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='non-hero tank marker GO')
    heroTankMarkerGO = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='hero tank marker GO')


class CombatMarker(CGFComponent):
    category = 'UI'
    editorTitle = 'Combat Marker'
    shape = ComponentProperty(type=CGFMetaTypes.STRING, value='', editorName='Shape')
    offset = ComponentProperty(type=CGFMetaTypes.VECTOR3, value=Math.Vector3(0, 0, 0), editorName='offset')
    areaRadius = ComponentProperty(type=CGFMetaTypes.FLOAT, value=0.0, editorName='areaRadius')
    disappearanceRadius = ComponentProperty(type=CGFMetaTypes.FLOAT, value=1.0, editorName='Disappearance Radius')
    reverseDisappearing = ComponentProperty(type=CGFMetaTypes.BOOL, value=False, editorName='Reverse disappearing')
    distanceFieldColor = ComponentProperty(type=CGFMetaTypes.STRING, value='white', editorName='Distance Field Color')

    def __init__(self):
        super(CombatMarker, self).__init__()
        self.marker = None
        self.markerID = None
        return


@autoregister(presentInAllWorlds=False, category='lobby')
class LobbyMarkersManager(CGF.ComponentManager):
    if not IS_CGF_DUMP:
        __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *args):
        super(LobbyMarkersManager, self).__init__(*args)
        self.onMarkerComponentAdded = Event.Event()
        self.onMarkerComponentRemoved = Event.Event()

    @onAddedQuery(CGF.GameObject, LobbyFlashMarker, TransformComponent)
    def handleMarkerAdded(self, gameObject, flashMarkerComponent, transformComponent):
        entity = self.__getRootEntity(gameObject)
        matrix = transformComponent.worldTransform
        view = self.__getMarkerView()
        if entity is not None and view is not None:
            view.addCgfMarker(entity.id, flashMarkerComponent, matrix)
        return

    @onRemovedQuery(CGF.GameObject, LobbyFlashMarker, TransformComponent)
    def handleMarkerRemoved(self, gameObject, *_):
        entity = self.__getRootEntity(gameObject)
        view = self.__getMarkerView()
        if entity is not None and view is not None:
            view.removeCgfMarker(entity.id)
        return

    @cached_property
    def __hierarchyManager(self):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        return hierarchyManager

    def __getRootEntity(self, gameObject):
        rootGameObject = self.__hierarchyManager.getTopMostParent(gameObject)
        goSyncComponent = rootGameObject.findComponentByType(EntityGOSync)
        if goSyncComponent is None:
            _logger.error('gameObject id=%d, name=%s has no root bigworld entity to show marker', gameObject.id, gameObject.name)
            return
        else:
            return goSyncComponent.entity

    def __getMarkerView(self):
        app = self.__appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
        return app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW))


@autoregister(presentInAllWorlds=False, category='lobby')
class LobbyMarkersVisibilityManager(CGF.ComponentManager):

    @onAddedQuery(LobbyFlashMarkerVisibility, CGF.GameObject)
    def handleVisibilityAdded(self, lobbyFlashMarkerVisibility, _):
        self.__onHeroTankAction(lobbyFlashMarkerVisibility)
        g_currentPreviewVehicle.onSelected += lambda : self.__onHeroTankAction(lobbyFlashMarkerVisibility)

    @onRemovedQuery(LobbyFlashMarkerVisibility, CGF.GameObject)
    def handleVisibilityRemoved(self, lobbyFlashMarkerVisibility, _):
        g_currentPreviewVehicle.onSelected -= lambda : self.__onHeroTankAction(lobbyFlashMarkerVisibility)

    def __onHeroTankAction(self, component):
        if g_currentPreviewVehicle.isHeroTank and g_currentPreviewVehicle.item:
            self.__activateMarkerFromHeroTank(component)
        else:
            self.__activateMarkerFromNonHeroTank(component)

    @staticmethod
    def __activateMarkerFromNonHeroTank(component):
        if component.heroTankMarkerGO and component.heroTankMarkerGO.isValid():
            component.heroTankMarkerGO.deactivate()
        if component.mainTankMarkerGO and component.mainTankMarkerGO.isValid():
            component.mainTankMarkerGO.activate()

    @staticmethod
    def __activateMarkerFromHeroTank(component):
        if component.mainTankMarkerGO and component.mainTankMarkerGO.isValid():
            component.mainTankMarkerGO.deactivate()
        if component.heroTankMarkerGO and component.heroTankMarkerGO.isValid():
            component.heroTankMarkerGO.activate()


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE)
class CombatMarkerManager(CGF.ComponentManager):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @onAddedQuery(CombatMarker, TransformComponent)
    def onAddedMarker(self, combatMarker, transform):
        transform = transform.worldTransform
        matrixProduct = math_utils.MatrixProviders.product(transform, math_utils.createTranslationMatrix(combatMarker.offset))
        data = {'visible': True,
         'areaRadius': combatMarker.areaRadius,
         'disappearingRadius': combatMarker.disappearanceRadius,
         'reverseDisappearing': combatMarker.reverseDisappearing,
         ComponentBitMask.MARKER_2D: [{'shape': combatMarker.shape,
                                       'min-distance': 0.0,
                                       'max-distance': 0.0,
                                       'distance': 0.0,
                                       'distanceFieldColor': combatMarker.distanceFieldColor,
                                       'displayDistance': False}],
         'matrixProduct': matrixProduct,
         'bitMask': ComponentBitMask.MARKER_2D}
        combatMarker.marker = AreaMarker(data)
        combatMarker.markerID = self.__guiSessionProvider.shared.areaMarker.addMarker(combatMarker.marker)

    @onRemovedQuery(CombatMarker)
    def onRemovedMarker(self, combatMarker):
        self.__guiSessionProvider.shared.areaMarker.removeMarker(combatMarker.markerID)
