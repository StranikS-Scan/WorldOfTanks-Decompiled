# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/new_year_components.py
import CGF
import Event
from cgf_components.marker_component import LobbyGameFaceMarker
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from new_year.skeletons.new_year import INewYearController, ITamagotchiDataProvider
from cgf_components.hover_component import SelectionComponent, IsHoveredComponent, IsExternalHoveredComponent
from constants import IS_EDITOR
from new_year.gui.shared.ny_machine_helper import isMachineEnabled
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.ny_constants import ViewAliases
from helpers import dependency
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.impl import INewYearNavigation
from new_year.ny_constants import AnchorNames, OBJECT_TO_ANCHOR
from cgf_components.hangar_camera_manager import CurrentCameraObject, CameraInFlightComponent
from cgf_components.highlight_component import HighlightComponent
from CameraComponents import CameraComponent
if not IS_EDITOR:
    from new_year.gui.impl.new_year.navigation import NewYearNavigation

@registerComponent
class NyOutlineGoComponent(object):
    editorTitle = 'NY Outline Game object'
    category = 'New Year'
    objectName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='object name', value=AnchorNames.TREE)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)

    def clickAction(self):
        self.__newYearNavigation.switchByAnchorName(self.objectName)


class NewYearClickManager(CGF.ComponentManager):
    __festivityController = dependency.descriptor(IFestivityController)

    @onAddedQuery(NyOutlineGoComponent, SelectionComponent)
    def handleNewYearClickAdded(self, customizationObject, selectionComponent):
        selectionComponent.onClickAction += customizationObject.clickAction

    @onRemovedQuery(NyOutlineGoComponent, SelectionComponent)
    def handleNewYearClickRemoved(self, customizationObject, selectionComponent):
        selectionComponent.onClickAction -= customizationObject.clickAction


def _defaultObjectActiveRule(objectName, ctx):
    viewName = ctx.getCurrentViewName()
    cameraName = ctx.getCurrentCameraName()
    return objectName != cameraName and viewName is not None and not NewYearNavigation.isInCustomizationObject() and viewName not in (ViewAliases.ONBOARDING_VIEW, ViewAliases.SURPRISE_MACHINE_VIEW)


def _firObjectActiveRule(objectName, ctx):
    return objectName != ctx.getCurrentCameraName() and not NewYearNavigation.isInCustomizationObject() and ctx.getCurrentCameraName() != ViewAliases.TANK_CUSTOMIZATION


def _raccoonObjectActiveRule(_, ctx):
    return ctx.getCurrentViewName() is None and ctx.isPetVisible() and not ctx.isOnboarding and ctx.getCurrentCameraName() != ViewAliases.TANK_CUSTOMIZATION


def _machineObjectActiveRule(_, ctx):
    return ctx.getCurrentViewName() is None and not ctx.isOnboarding and isMachineEnabled() and ctx.getCurrentCameraName() != ViewAliases.TANK_CUSTOMIZATION


def _challengeObjectActiveRule(_, ctx):
    return ctx.getCurrentViewName() is None and not ctx.isOnboarding and ctx.getCurrentCameraName() != ViewAliases.TANK_CUSTOMIZATION


_ANCHOR_OBJECTS_HIGHLIGHT_ACTIVE_RULE = {AnchorNames.TREE: _firObjectActiveRule,
 AnchorNames.RACCOON: _raccoonObjectActiveRule,
 AnchorNames.CHALLENGE: _challengeObjectActiveRule,
 AnchorNames.MACHINE: _machineObjectActiveRule}

class _HighlightCtx(object):
    __slots__ = ('__currentCameraName', '__currentViewName', '__isCameraInFlight', '__newYearConfig', 'isOnboarding', 'onCtxUpdated', '_dataProvider')
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self):
        self.__currentViewName = None
        self.__currentCameraName = None
        self.__isCameraInFlight = False
        self.__newYearConfig = None
        self.isOnboarding = False
        self.onCtxUpdated = Event.Event()
        return

    @property
    def isCameraInFlight(self):
        return self.__isCameraInFlight

    @isCameraInFlight.setter
    def isCameraInFlight(self, value):
        self.__isCameraInFlight = value

    def setConfig(self, config):
        self.__newYearConfig = config
        self.onCtxUpdated()

    def setCurrentViewName(self, value):
        oldValue = self.__currentViewName
        self.__currentViewName = value
        if oldValue != self.__currentViewName:
            self.onCtxUpdated()

    def setCurrentCameraName(self, value):
        oldValue = self.__currentCameraName
        self.__currentCameraName = value
        if oldValue != self.__currentCameraName:
            self.onCtxUpdated()

    def setData(self, cameraName, viewName):
        oldValue = (self.__currentCameraName, self.__currentViewName)
        self.__currentCameraName = cameraName
        self.__currentViewName = viewName
        if oldValue != (self.__currentCameraName, self.__currentViewName):
            self.onCtxUpdated()

    def getCurrentViewName(self):
        return self.__currentViewName

    def getCurrentCameraName(self):
        return self.__currentCameraName

    def isPetVisible(self):
        return self._dataProvider.raccoonState and self.__newYearConfig and self.__newYearConfig.getPetVisible()


_HOVERED_MARKER_NAME = 'cityModel.objectsOverview.hoveredObject'

class NewYearHoverManager(CGF.ComponentManager):
    __festivityController = dependency.descriptor(IFestivityController)
    __newYearNavigation = dependency.descriptor(INewYearNavigation)
    __newYearController = dependency.descriptor(INewYearController)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self):
        super(NewYearHoverManager, self).__init__()
        self.__highlightCtx = _HighlightCtx()

    def activate(self):
        self.__newYearController.onNySettingsChanged += self.__onNySettingsChanged
        self.__highlightCtx.setConfig(getNewYearGeneralConfig())
        self.__highlightCtx.setCurrentViewName(self.__newYearNavigation.getCurrentViewName())
        self.__highlightCtx.isOnboarding = not self.__newYearController.isOnboardingFinished()
        self.__highlightCtx.onCtxUpdated += self.__updateActive
        self.__newYearController.onGUIObjectHover += self.__onGUIObjectHover
        self.__newYearNavigation.onChangeView += self.__onChangeView
        self.__newYearController.onOnboardingFinished += self.__onOnboardingFinished
        self._dataProvider.onRaccoonStateUpdated += self.__onRaccoonStateUpdated

    def deactivate(self):
        self.__newYearController.onNySettingsChanged -= self.__onNySettingsChanged
        self.__newYearController.onGUIObjectHover -= self.__onGUIObjectHover
        self.__highlightCtx.onCtxUpdated -= self.__updateActive
        self.__newYearNavigation.onChangeView -= self.__onChangeView
        self.__newYearController.onOnboardingFinished -= self.__onOnboardingFinished
        self._dataProvider.onRaccoonStateUpdated -= self.__onRaccoonStateUpdated

    @onAddedQuery(NyOutlineGoComponent, CGF.GameObject, HighlightComponent)
    def onNyOutlineAdded(self, outline, gameObject, highlight):
        isActive = self.__isHighlightActive(outline)
        highlight.isActive = isActive
        self.__setHover(gameObject, isActive)

    @onAddedQuery(CurrentCameraObject, CameraComponent)
    def onCameraSwitched(self, _, cameraComponent):
        self.__highlightCtx.setData(cameraComponent.name, self.__newYearNavigation.getCurrentViewName())

    @onAddedQuery(CameraInFlightComponent)
    def onCameraInFlight(self, _):
        self.__highlightCtx.isCameraInFlight = True

    @onRemovedQuery(CameraInFlightComponent)
    def onCameraInFlightRemoved(self, _):
        self.__highlightCtx.isCameraInFlight = False
        self.__updateActive()

    def __onChangeView(self, viewAlias):
        self.__highlightCtx.setCurrentViewName(viewAlias)
        self.__clearSelection()

    def __clearSelection(self):
        for go, _ in CGF.Query(self.spaceID, (CGF.GameObject, IsExternalHoveredComponent)):
            go.removeComponentByType(IsExternalHoveredComponent)

    def __updateActive(self):
        queryOutline = CGF.Query(self.spaceID, (CGF.GameObject, NyOutlineGoComponent, HighlightComponent))
        for go, outline, highlight in queryOutline:
            isActive = self.__isHighlightActive(outline)
            if highlight.isActive != isActive:
                self.__setHover(go, isActive)
            highlight.isActive = isActive

    def __isHighlightActive(self, outline):
        return self.__festivityController.isEnabled() and _ANCHOR_OBJECTS_HIGHLIGHT_ACTIVE_RULE.get(outline.objectName, _defaultObjectActiveRule)(outline.objectName, self.__highlightCtx) and not self.__highlightCtx.isCameraInFlight

    @onAddedQuery(NyOutlineGoComponent, CGF.GameObject, IsHoveredComponent)
    def onHoverAdded(self, outline, gameObject, *_):
        self.__newYearController.setSpaceObjectHover(outline.objectName, True)
        self.__activateHoverMarker(gameObject)

    @onRemovedQuery(NyOutlineGoComponent, CGF.GameObject, IsHoveredComponent)
    def onHoverRemoved(self, outline, gameObject, *_):
        self.__newYearController.setSpaceObjectHover(outline.objectName, False)
        self.__deactivateHoverMarker(gameObject)

    def __onGUIObjectHover(self, objectName, isHovered):
        anchorName = OBJECT_TO_ANCHOR.get(objectName, '')
        if not isHovered:
            queryOutline = CGF.Query(self.spaceID, (CGF.GameObject, NyOutlineGoComponent, IsExternalHoveredComponent))
            for go, outline, _ in queryOutline:
                if outline.objectName == anchorName:
                    go.removeComponentByType(IsExternalHoveredComponent)

        else:
            queryOutline = CGF.Query(self.spaceID, (CGF.GameObject, NyOutlineGoComponent, CGF.No(IsExternalHoveredComponent)))
            for go, outline in queryOutline:
                if outline.objectName == anchorName:
                    go.createComponent(IsExternalHoveredComponent)

    def __setHover(self, go, isActive):
        if not isActive and go.findComponentByType(SelectionComponent) is not None:
            go.removeComponentByType(SelectionComponent)
        elif isActive and go.findComponentByType(SelectionComponent) is None:
            go.createComponent(SelectionComponent)
        return

    def __activateHoverMarker(self, gameObject):
        if self.__newYearNavigation.getCurrentViewName() != ViewAliases.CITY_VIEW:
            return
        else:
            hierarchyManager = CGF.HierarchyManager(self.spaceID)
            if not hierarchyManager:
                return
            topParent = hierarchyManager.getTopMostParent(gameObject)
            for children in hierarchyManager.getChildrenIncludingInactive(topParent):
                marker = children.findComponentByType(LobbyGameFaceMarker)
                if marker is not None and marker.markerName == _HOVERED_MARKER_NAME:
                    children.activate()

            return

    def __deactivateHoverMarker(self, gameObject):
        hierarchyManager = CGF.HierarchyManager(self.spaceID)
        if not hierarchyManager:
            return
        else:
            topParent = hierarchyManager.getTopMostParent(gameObject)
            for children in hierarchyManager.getChildrenIncludingInactive(topParent):
                marker = children.findComponentByType(LobbyGameFaceMarker)
                if marker is not None and marker.markerName == _HOVERED_MARKER_NAME:
                    children.deactivate()

            return

    def __onNySettingsChanged(self):
        self.__highlightCtx.setConfig(getNewYearGeneralConfig())

    def __onOnboardingFinished(self):
        self.__highlightCtx.isOnboarding = False

    def __onRaccoonStateUpdated(self, _):
        self.__updateActive()
