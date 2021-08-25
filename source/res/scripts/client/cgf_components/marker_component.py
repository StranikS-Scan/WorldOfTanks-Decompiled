# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/marker_component.py
import typing
import logging
import CGF
import Event
from CurrentVehicle import g_currentPreviewVehicle
from GenericComponents import TransformComponent, EntityGOSync
from cache import cached_property
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.app_loader.settings import APP_NAME_SPACE
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
if typing.TYPE_CHECKING:
    import BigWorld
_logger = logging.getLogger(__name__)

class LobbyFlashMarker(CGFComponent):
    icon = ComponentProperty(type=CGFMetaTypes.STRING, editorName='marker icon', value='gui/maps/icons/marathon/marker/video.png', annotations={'path': '*.png'})
    textKey = ComponentProperty(type=CGFMetaTypes.STRING, editorName='marker text key', value='#marathon:3dObject/showVideo')


class LobbyFlashMarkerVisibility(CGFComponent):
    mainTankMarkerGO = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='non-hero tank marker GO')
    heroTankMarkerGO = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='hero tank marker GO')


@autoregister(presentInAllWorlds=False, category='lobby')
class LobbyMarkersManager(CGF.ComponentManager):
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
