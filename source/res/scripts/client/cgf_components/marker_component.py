# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/marker_component.py
from __future__ import absolute_import
import importlib
import logging
import typing
import CGF
import Event
import GenericComponents
import Math
import math_utils
from cgf_script.registration import ComponentProperty, registerComponent
from constants import IS_CLIENT, IS_CGF_DUMP
from helpers import dependency
from UIComponents import GamefaceMarkerComponent
if IS_CLIENT:
    from skeletons.gui.battle_session import IBattleSessionProvider
    from CurrentVehicle import g_currentPreviewVehicle
    from skeletons.gui.app_loader import IAppLoader
    from skeletons.gui.impl import IGuiLoader
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.Scaleform.framework.entities.View import ViewKey
    from gui.app_loader.settings import APP_NAME_SPACE
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers import AreaMarker
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask
    from gui.impl.pub import WindowImpl
    from frameworks.wulf import WindowFlags, WindowLayer
else:

    class IBattleSessionProvider(object):
        pass


    class IAppLoader(object):
        pass


    class IGuiLoader(object):
        pass


if typing.TYPE_CHECKING:
    import BigWorld
_logger = logging.getLogger(__name__)

@registerComponent
class LobbyFlashMarker(object):
    domain = CGF.Domain.Client
    editorTitle = 'Lobby Flash Marker'
    icon = ComponentProperty(type=CGF.PropertyType.String, editorName='marker icon', value='gui/maps/icons/marathon/marker/video.png', annotations={'path': '*.png'})
    textKey = ComponentProperty(type=CGF.PropertyType.String, editorName='marker text key', value='#marathon:3dObject/showVideo')


@registerComponent
class LobbyFlashMarkerVisibility(object):
    domain = CGF.Domain.Client
    editorTitle = 'Lobby Flash Marker Visibility'
    mainTankMarkerGO = ComponentProperty(type=CGF.PropertyType.Link, value=CGF.GameObject, editorName='non-hero tank marker GO')
    heroTankMarkerGO = ComponentProperty(type=CGF.PropertyType.Link, value=CGF.GameObject, editorName='hero tank marker GO')


@registerComponent
class CombatMarker(object):
    group = 'UI'
    editorTitle = 'Combat Marker'
    domain = CGF.Domain.Client
    shape = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='Shape')
    offset = ComponentProperty(type=CGF.PropertyType.Vector3, value=Math.Vector3(0, 0, 0), editorName='offset')
    areaRadius = ComponentProperty(type=CGF.PropertyType.Float, value=0.0, editorName='areaRadius')
    disappearanceRadius = ComponentProperty(type=CGF.PropertyType.Float, value=1.0, editorName='Disappearance Radius')
    reverseDisappearing = ComponentProperty(type=CGF.PropertyType.Bool, value=False, editorName='Reverse disappearing')
    distanceFieldColor = ComponentProperty(type=CGF.PropertyType.String, value='white', editorName='Distance Field Color')

    def __init__(self):
        super(CombatMarker, self).__init__()
        self.marker = None
        self.markerID = None
        return


class LobbyMarkersSystem(CGF.System):
    if not IS_CGF_DUMP:
        __appLoader = dependency.descriptor(IAppLoader)
    MarkerActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(LobbyFlashMarker), CGF.Ro(CGF.TransformComponent))
    MarkerDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(LobbyFlashMarker), CGF.Has(CGF.TransformComponent))
    EntitySyncAccess = CGF.AccessReaction(CGF.Ro(GenericComponents.EntityGOSync))
    Reactions = CGF.Reactions(MarkerActivated, MarkerDeactivated, EntitySyncAccess)

    def __init__(self, *args):
        super(LobbyMarkersSystem, self).__init__(*args)
        self.onMarkerComponentAdded = Event.Event()
        self.onMarkerComponentRemoved = Event.Event()

    def update(self):
        entitySyncAccess = self.reaction(self.EntitySyncAccess)
        for gameObject, _ in self.reaction(self.MarkerDeactivated):
            self.handleMarkerRemoved(gameObject, entitySyncAccess)

        for gameObject, flashMarkerComponent, transformComponent in self.reaction(self.MarkerActivated):
            self.handleMarkerAdded(gameObject, flashMarkerComponent, transformComponent, entitySyncAccess)

    def handleMarkerAdded(self, gameObject, flashMarkerComponent, transformComponent, entitySyncAccess):
        entity = self.__getRootEntity(gameObject, entitySyncAccess)
        matrix = transformComponent.worldTransform
        view = self.__getMarkerView()
        if entity is not None and view is not None:
            view.addCgfMarker(entity.id, flashMarkerComponent, matrix)
        return

    def handleMarkerRemoved(self, gameObject, entitySyncAccess):
        entity = self.__getRootEntity(gameObject, entitySyncAccess)
        view = self.__getMarkerView()
        if entity is not None and view is not None:
            view.removeCgfMarker(entity.id)
        return

    def __getRootEntity(self, gameObject, entitySyncAccess):
        rootGameObject = self.hierarchy.getTopMostParent(gameObject)
        goSyncComponent = entitySyncAccess.find(rootGameObject)
        if goSyncComponent is None:
            _logger.error('gameObject id=%d, name=%s has no root bigworld entity to show marker', gameObject.id, gameObject.name)
            return
        else:
            return goSyncComponent.entity

    def __getMarkerView(self):
        app = self.__appLoader.getApp(APP_NAME_SPACE.SF_LOBBY)
        return app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_VEHICLE_MARKER_VIEW))


class LobbyMarkersVisibilitySystem(CGF.System):
    VisibilityActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRo(LobbyFlashMarkerVisibility))
    VisibilityDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRo(LobbyFlashMarkerVisibility))
    VisibilityAccess = CGF.AccessReaction(CGF.Ro(LobbyFlashMarkerVisibility))
    Reactions = CGF.Reactions(VisibilityActivated, VisibilityDeactivated, VisibilityAccess)

    def update(self):
        for gameObject, _ in self.reaction(self.VisibilityDeactivated):
            self.handleVisibilityRemoved(gameObject)

        for gameObject, lobbyFlashMarkerVisibility in self.reaction(self.VisibilityActivated):
            self.handleVisibilityAdded(gameObject, lobbyFlashMarkerVisibility)

    def handleVisibilityAdded(self, gameObject, lobbyFlashMarkerVisibility):
        self.__onHeroTankAction(gameObject, lobbyFlashMarkerVisibility)
        g_currentPreviewVehicle.onSelected += lambda : self.__onHeroTankAction(gameObject)

    def handleVisibilityRemoved(self, gameObject):
        g_currentPreviewVehicle.onSelected -= lambda : self.__onHeroTankAction(gameObject)

    def __onHeroTankAction(self, gameObject, visibilityComponent=None):
        component = visibilityComponent
        if component is None:
            visibilityAccess = self.reaction(self.VisibilityAccess)
            component = visibilityAccess.find(gameObject)
        if g_currentPreviewVehicle.isHeroTank and g_currentPreviewVehicle.item:
            self.__activateMarkerFromHeroTank(component, self.gom)
        else:
            self.__activateMarkerFromNonHeroTank(component, self.gom)
        return

    @staticmethod
    def __activateMarkerFromNonHeroTank(component, gameObjectManager):
        if component.heroTankMarkerGO:
            heroMarkerObj = gameObjectManager.gameObject(component.heroTankMarkerGO)
            if heroMarkerObj.valid:
                heroMarkerObj.deactivate()
        if component.mainTankMarkerGO:
            mainMarkerObj = gameObjectManager.gameObject(component.mainTankMarkerGO)
            if mainMarkerObj.valid:
                mainMarkerObj.activate()

    @staticmethod
    def __activateMarkerFromHeroTank(component, gameObjectManager):
        if component.mainTankMarkerGO:
            mainMarkerObj = gameObjectManager.gameObject(component.mainTankMarkerGO)
            if mainMarkerObj.valid:
                mainMarkerObj.deactivate()
        if component.heroTankMarkerGO:
            heroMarkerObj = gameObjectManager.gameObject(component.heroTankMarkerGO)
            if heroMarkerObj.valid:
                heroMarkerObj.activate()


class CombatMarkerSystem(CGF.System):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    MarkerActivated = CGF.ActivateReaction(CGF.ReactRw(CombatMarker), CGF.Ro(CGF.TransformComponent))
    MarkerDeactivated = CGF.DeactivateReaction(CGF.ReactRo(CombatMarker))
    Reactions = CGF.Reactions(MarkerActivated, MarkerDeactivated)

    def update(self):
        for combatMarker in self.reaction(self.MarkerDeactivated):
            self.onRemovedMarker(combatMarker)

        for combatMarker, transform in self.reaction(self.MarkerActivated):
            self.onAddedMarker(combatMarker, transform)

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

    def onRemovedMarker(self, combatMarker):
        self.__guiSessionProvider.shared.areaMarker.removeMarker(combatMarker.markerID)


class GFMarkersCreatorSystem(CGF.System):
    __gui = dependency.descriptor(IGuiLoader)
    MarkerActivated = CGF.ActivateReaction(CGF.ReactRw(GamefaceMarkerComponent))
    MarkerDeactivated = CGF.DeactivateReaction(CGF.ReactRo(GamefaceMarkerComponent))
    Reactions = CGF.Reactions(MarkerActivated, MarkerDeactivated)

    def update(self):
        for markerComponent in self.reaction(self.MarkerDeactivated):
            self.onMarkerRemoved(markerComponent)

        for markerComponent in self.reaction(self.MarkerActivated):
            self.onMarkerAdded(markerComponent)

    def onMarkerAdded(self, markerComponent):
        module = importlib.import_module(markerComponent.viewPath)
        if not module or not hasattr(module, markerComponent.viewName):
            _logger.error('Cant find view. Module: %s, Name: %s', markerComponent.viewPath, markerComponent.viewName)
            return
        view = getattr(module, markerComponent.viewName)(markerComponent.viewKey)
        window = WindowImpl(WindowFlags.WINDOW, content=view, layer=WindowLayer.MARKER)
        window.load()
        markerComponent.windowID = window.uniqueID

    def onMarkerRemoved(self, markerComponent):
        window = self.__gui.windowsManager.getWindow(markerComponent.windowID)
        if window:
            window.destroy()
