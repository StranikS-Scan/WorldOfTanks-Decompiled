# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/marker_component.py
import logging
from collections import defaultdict
import CGF
import GUI
import GenericComponents
import Math
from GenericComponents import TransformComponent
import math_utils
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from constants import IS_CLIENT
from frameworks.wulf import ViewStatus
from gui.impl.gen import R
from helpers import dependency
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from skeletons.gui.impl import IGuiLoader
if IS_CLIENT:
    from skeletons.gui.battle_session import IBattleSessionProvider
    from CurrentVehicle import g_currentPreviewVehicle
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers import AreaMarker
    from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask
else:

    class IBattleSessionProvider(object):
        pass


_logger = logging.getLogger(__name__)

@registerComponent
class LobbyFlashMarker(object):
    domain = CGF.DomainOption.DomainClient
    icon = ComponentProperty(type=CGFMetaTypes.STRING, editorName='marker icon', value='gui/maps/icons/marathon/marker/video.png', annotations={'path': '*.png'})
    textKey = ComponentProperty(type=CGFMetaTypes.STRING, editorName='marker text key', value='#marathon:3dObject/showVideo')
    iconPosition = ComponentProperty(type=CGFMetaTypes.STRING, editorName='icon position', value='')

    def __init__(self, icon=None, textKey=None, iconPosition=None):
        super(LobbyFlashMarker, self).__init__()
        if icon is not None:
            self.icon = icon
        if textKey is not None:
            self.textKey = textKey
        if iconPosition is not None:
            self.iconPosition = iconPosition
        return


@registerComponent
class LobbyFlashMarkerVisibility(object):
    domain = CGF.DomainOption.DomainClient
    mainTankMarkerGO = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='non-hero tank marker GO')
    heroTankMarkerGO = ComponentProperty(type=CGFMetaTypes.LINK, value=CGF.GameObject, editorName='hero tank marker GO')


@registerComponent
class CombatMarker(object):
    category = 'UI'
    editorTitle = 'Combat Marker'
    domain = CGF.DomainOption.DomainClient
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


def _getMarkerData(markerId, flashMarkerComponent, matrix):
    return {'markerId': markerId,
     'flashMarkerComponent': flashMarkerComponent,
     'matrix': matrix}


@autoregister(presentInAllWorlds=False, category='lobby')
class LobbyMarkersManager(CGF.ComponentManager):

    def activate(self):
        g_eventBus.addListener(events.LobbyMarkersManagerEvent.ON_MARKER_REQUEST, self.__onMarkerRequested, EVENT_BUS_SCOPE.LOBBY)

    def deactivate(self):
        g_eventBus.removeListener(events.LobbyMarkersManagerEvent.ON_MARKER_REQUEST, self.__onMarkerRequested, EVENT_BUS_SCOPE.LOBBY)

    @onAddedQuery(CGF.GameObject, LobbyFlashMarker, TransformComponent)
    def handleMarkerAdded(self, gameObject, flashMarkerComponent, transformComponent):
        matrix = transformComponent.worldTransform
        g_eventBus.handleEvent(events.LobbyMarkersManagerEvent(events.LobbyMarkersManagerEvent.ON_MARKER_ADDED, ctx=_getMarkerData(gameObject.id, flashMarkerComponent, matrix)), scope=EVENT_BUS_SCOPE.LOBBY)

    @onRemovedQuery(CGF.GameObject, LobbyFlashMarker, TransformComponent)
    def handleMarkerRemoved(self, gameObject, *_):
        g_eventBus.handleEvent(events.LobbyMarkersManagerEvent(events.LobbyMarkersManagerEvent.ON_MARKER_REMOVED, ctx={'markerId': gameObject.id}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onMarkerRequested(self, event):
        requesterId = event.ctx['requesterId']
        markers = []
        for go, marker, transform in CGF.Query(self.spaceID, (CGF.GameObject, LobbyFlashMarker, TransformComponent)):
            if go.isValid():
                markers.append(_getMarkerData(go.id, marker, transform.worldTransform))

        g_eventBus.handleEvent(events.LobbyMarkersManagerEvent(events.LobbyMarkersManagerEvent.ON_MARKER_RESPONSE, ctx={'requesterId': requesterId,
         'markers': markers}), scope=EVENT_BUS_SCOPE.LOBBY)


@autoregister(presentInAllWorlds=False, category='lobby')
class LobbyMarkersVisibilityManager(CGF.ComponentManager):

    def activate(self):
        g_currentPreviewVehicle.onSelected += self.__onPreviewVehicleSelected

    def deactivate(self):
        g_currentPreviewVehicle.onSelected -= self.__onPreviewVehicleSelected

    @onAddedQuery(LobbyFlashMarkerVisibility, CGF.GameObject)
    def handleVisibilityAdded(self, lobbyFlashMarkerVisibility, _):
        self.__onHeroTankAction(lobbyFlashMarkerVisibility)

    def __onPreviewVehicleSelected(self):
        for component in CGF.Query(self.spaceID, LobbyFlashMarkerVisibility):
            self.__onHeroTankAction(component)

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


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.BATTLEROYALE, CGF.DomainOption.DomainClient)
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


@registerComponent
class LobbyGameFaceMarker(object):
    domain = CGF.DomainOption.DomainClient
    layoutID = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Parent layoutID')
    markerName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Marker name')

    def __init__(self):
        super(LobbyGameFaceMarker, self).__init__()
        self.viewLayoutID = _parseLayoutPath(self.layoutID)


def _parseLayoutPath(path):
    res = R.views
    for p in path.split('.')[2:]:
        res = res.dyn(p)

    if not res.exists():
        _logger.error('Wrong view path %s', path)
        return R.invalid()
    return res()


class LobbyGFMarkersManager(CGF.ComponentManager):
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, *args):
        self.markerCtrl = GUI.MarkerPositionController()
        super(LobbyGFMarkersManager, self).__init__(*args)
        self.__viewMarkers = defaultdict(dict)

    def activate(self):
        self.__guiLoader.windowsManager.onViewStatusChanged += self.__onViewStatusChanged

    def deactivate(self):
        self.__guiLoader.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        self.__viewMarkers.clear()
        self.markerCtrl.clear()

    @onAddedQuery(CGF.GameObject, LobbyGameFaceMarker, GenericComponents.TransformComponent)
    def onMarkerAdded(self, go, markerComponent, transformComponent):
        _logger.debug('onMarkerAdded %s %s', markerComponent.viewLayoutID, markerComponent.markerName)
        if markerComponent.viewLayoutID:
            self.__viewMarkers[markerComponent.viewLayoutID][go.id] = (markerComponent, transformComponent)
            for view in self.__guiLoader.windowsManager.getViewsByLayout(markerComponent.viewLayoutID):
                if view.viewStatus == ViewStatus.LOADED:
                    self.__loadMarker(markerComponent, transformComponent, view)

    @onRemovedQuery(CGF.GameObject, LobbyGameFaceMarker)
    def onMarkerRemoved(self, go, markerComponent):
        _logger.debug('onMarkerRemoved %s %s', markerComponent.viewLayoutID, markerComponent.markerName)
        if markerComponent.viewLayoutID in self.__viewMarkers:
            self.__viewMarkers[markerComponent.viewLayoutID].pop(go.id)
            for view in self.__guiLoader.windowsManager.getViewsByLayout(markerComponent.viewLayoutID):
                if view.viewStatus == ViewStatus.LOADED:
                    self.__removeMarker(markerComponent, view)

    def __onViewStatusChanged(self, uniqueID, newState):
        if newState == ViewStatus.LOADING:
            view = self.__guiLoader.windowsManager.getView(uniqueID)
            markersComponent = self.__viewMarkers.get(view.layoutID)
            if markersComponent:
                for marker, trensform in markersComponent.itervalues():
                    self.__loadMarker(marker, trensform, view)

        elif newState == ViewStatus.DESTROYING:
            view = self.__guiLoader.windowsManager.getView(uniqueID)
            markersComponent = self.__viewMarkers.get(view.layoutID)
            if markersComponent:
                for marker, _ in markersComponent.itervalues():
                    self.__removeMarker(marker, view)

    def __loadMarker(self, markerComponent, transformComponent, view):
        markerModel = self.__parseMarkerName(view, markerComponent.markerName)
        self.markerCtrl.add(markerModel.proxy, transformComponent.worldTransform.translation)

    def __removeMarker(self, markerComponent, view):
        markerModel = self.__parseMarkerName(view, markerComponent.markerName)
        self.markerCtrl.remove(markerModel.proxy)

    @classmethod
    def __parseMarkerName(cls, view, name):
        res = view.viewModel
        for p in name.split('.'):
            res = getattr(res, p)

        return res
