# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/view_camera_sync.py
import logging
import re
from collections import defaultdict
from enum import IntEnum
import BigWorld
import CGF
from CameraComponents import CameraComponent
from cgf_components.hangar_camera_manager import CurrentCameraObject, CameraInFlightComponent, HangarCameraManager
from cgf_components.view_components import ViewComponent
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from frameworks.wulf import ViewStatus
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)

class CameraState(IntEnum):
    NOT_EXIST = -1
    NOT_INSTALLED = 0
    INSTALLED = 1
    IN_TRANSITION = 2


class IViewCameraSync(object):
    onInternalViewStateChanged = None

    @property
    def skipCameraFlightOnInit(self):
        raise NotImplementedError

    @property
    def skipCameraFlightOnClose(self):
        raise NotImplementedError

    def getInternalViewState(self):
        raise NotImplementedError

    def setInternalViewState(self, internalViewState):
        raise NotImplementedError

    def setCameraState(self, cameraState):
        raise NotImplementedError


@registerComponent
class ViewCameraSyncComponent(object):
    editorTitle = 'ViewCameraSyncComponent'
    category = 'lobby'
    viewLayoutPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='viewLayoutPath', value='')
    viewState = ComponentProperty(type=CGFMetaTypes.STRING, editorName='viewState', value='')
    cameraObject = ComponentProperty(type=CGFMetaTypes.LINK, editorName='camera', value=CGF.GameObject)
    skipFlight = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='skipFlight', value=False)

    def __init__(self):
        super(ViewCameraSyncComponent, self).__init__()
        self.viewLayoutID = _parseLayoutPath(self.viewLayoutPath)

    @property
    def camera(self):
        return self.cameraObject.findComponentByType(CameraComponent)


def _parseLayoutPath(path):
    res = R.views
    for p in re.split('[\\\\/]', path):
        res = res.dyn(p)

    if not res.exists():
        _logger.error('Wrong view path %s', path)
        return R.invalid()
    return res()


class ViewCameraSyncManager(CGF.ComponentManager):

    def __init__(self, *args):
        super(ViewCameraSyncManager, self).__init__(*args)
        self.__components = {}
        self.__currentCameraName = None
        self.__cameraOwners = set()
        return

    def deactivate(self):
        self.__components.clear()
        self.__currentCameraName = None
        self.__cameraOwners.clear()
        return

    @onAddedQuery(CGF.GameObject, ViewCameraSyncComponent)
    def onSyncCreated(self, go, syncComponent):
        if syncComponent.viewLayoutID:
            self.__components[syncComponent.viewLayoutID, syncComponent.viewState] = CGF.ComponentLink(go, ViewCameraSyncComponent)

    @onRemovedQuery(ViewCameraSyncComponent)
    def onSyncRemoved(self, syncComponent):
        if syncComponent.viewLayoutID:
            self.__components.pop((syncComponent.viewLayoutID, syncComponent.viewState), None)
        return

    @onAddedQuery(CurrentCameraObject, CameraComponent)
    def onCurrentCameraAdded(self, _, cameraComponet):
        self.__currentCameraName = cameraComponet.name

    @onAddedQuery(CurrentCameraObject, CameraInFlightComponent)
    def onCameraSwitching(self, _, currentCameraInFlight):
        for viewLayoutID, viewState in self.__cameraOwners:
            owner = self.__components.get((viewLayoutID, viewState), None)
            if owner:
                viewComponent = owner.gameObject.findComponentByType(ViewComponent)
                if viewComponent:
                    viewComponent.view.setCameraState(CameraState.IN_TRANSITION)

        return

    @onRemovedQuery(CurrentCameraObject)
    def onCurrentCameraRemoved(self, _):
        self.__currentCameraName = None
        for viewLayoutID, viewState in self.__cameraOwners:
            owner = self.__components.get((viewLayoutID, viewState), None)
            if owner:
                viewComponent = owner.gameObject.findComponentByType(ViewComponent)
                if viewComponent:
                    viewComponent.view.setCameraState(CameraState.NOT_INSTALLED)

        return

    @onAddedQuery(CurrentCameraObject, CGF.No(CameraInFlightComponent))
    def onCameraSwitched(self, _):
        for viewLayoutID, viewState in self.__cameraOwners:
            owner = self.__components.get((viewLayoutID, viewState), None)
            if owner:
                viewComponent = owner.gameObject.findComponentByType(ViewComponent)
                if viewComponent:
                    viewComponent.view.setCameraState(CameraState.INSTALLED)

        return

    @onAddedQuery(ViewCameraSyncComponent, ViewComponent)
    def onViewCreated(self, syncComponent, viewComponent):
        _logger.debug('onViewCreated %s %s', syncComponent.viewLayoutPath, syncComponent.viewState)
        internalState = viewComponent.view.getInternalViewState()
        viewComponent.view.onInternalViewStateChanged += self.__onInternalViewStateChanged
        if internalState == syncComponent.viewState:
            self.__sync(viewComponent.view, syncComponent, skipFlight=viewComponent.view.skipCameraFlightOnInit)

    @onRemovedQuery(ViewCameraSyncComponent, ViewComponent)
    def onViewRemoved(self, syncComponent, viewComponent):
        _logger.debug('onViewRemoved %s %s', syncComponent.viewLayoutPath, syncComponent.viewState)
        if (syncComponent.viewLayoutID, syncComponent.viewState) in self.__cameraOwners:
            self.__desync(syncComponent, skipFlight=viewComponent.view.skipCameraFlightOnClose)
            self.__forceSync(skipFlight=viewComponent.view.skipCameraFlightOnClose)
        viewComponent.view = None
        return

    def __sync(self, view, syncComponent, skipFlight=None):
        if self.__currentCameraName == syncComponent.camera.name:
            state = CameraState.IN_TRANSITION if BigWorld.camera().isInTransition() else CameraState.INSTALLED
            view.setCameraState(state)
        else:
            view.setCameraState(CameraState.NOT_INSTALLED)
            self.__switchCamera(syncComponent.camera.name, skipFlight if skipFlight is not None else syncComponent.skipFlight)
        self.__cameraOwners.add((syncComponent.viewLayoutID, syncComponent.viewState))
        return

    def __desync(self, syncComponent, skipFlight=None, newState=None):
        self.__cameraOwners.discard((syncComponent.viewLayoutID, syncComponent.viewState))
        if not self.__cameraOwners and self.__currentCameraName == syncComponent.camera.name and (syncComponent.viewLayoutID, newState) not in self.__components:
            cameraManager = self.__getHangarCameraManager()
            if cameraManager and cameraManager.isActive:
                cameraManager.switchToTank(skipFlight or syncComponent.skipFlight)

    def __forceSync(self, skipFlight):
        if not self.__cameraOwners:
            return
        else:
            layoutID, viewState = self.__cameraOwners.pop()
            newSyncComponent = self.__components.get((layoutID, viewState), None)
            newViewComponent = newSyncComponent.gameObject.findComponentByType(ViewComponent) if newSyncComponent else None
            if newSyncComponent and newViewComponent:
                self.__sync(newViewComponent.view, newSyncComponent(), skipFlight)
            return

    def __getHangarCameraManager(self):
        return CGF.getManager(self.spaceID, HangarCameraManager)

    def __switchCamera(self, cameraName, instantly=False):
        cameraManager = self.__getHangarCameraManager()
        if cameraManager and cameraManager.isActive:
            cameraManager.switchByCameraName(cameraName, instantly)

    def __onInternalViewStateChanged(self, state, skipFlight=None):
        items = CGF.Query(self.spaceID, (ViewCameraSyncComponent, ViewComponent))
        if self.__cameraOwners:
            self._desyncAll(items, state, skipFlight)
        self._syncAll(items, state, skipFlight)

    def _syncAll(self, items, state, skipFlight):
        for syncComponent, viewComponent in items:
            oldKey = (syncComponent.viewLayoutID, syncComponent.viewState)
            if syncComponent.viewState == state and oldKey not in self.__cameraOwners:
                _logger.debug('ViewCameraSyncManager.sync %s %s %s', viewComponent.view.layoutID, state, syncComponent.viewLayoutPath)
                self.__sync(viewComponent.view, syncComponent, skipFlight)

    def _desyncAll(self, items, state, skipFlight):
        for syncComponent, viewComponent in items:
            oldKey = (syncComponent.viewLayoutID, syncComponent.viewState)
            if syncComponent.viewState != state and oldKey in self.__cameraOwners:
                _logger.debug('ViewCameraSyncManager.desync %s %s %s', viewComponent.view.layoutID, state, syncComponent.viewLayoutPath)
                self.__desync(syncComponent, skipFlight, newState=state)


class ViewCameraLinksManager(CGF.ComponentManager):
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, *args):
        super(ViewCameraLinksManager, self).__init__(*args)
        self.__viewGOLinks = defaultdict(dict)

    def activate(self):
        self.__guiLoader.windowsManager.onViewStatusChanged += self.__onViewStatusChanged

    def deactivate(self):
        self.__guiLoader.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        for values in self.__viewGOLinks.itervalues():
            for componentLink in values.itervalues():
                if componentLink.gameObject.findComponentByType(ViewComponent) is not None:
                    componentLink.gameObject.removeComponentByType(ViewComponent)

        self.__viewGOLinks.clear()
        return

    @onAddedQuery(CGF.GameObject, ViewCameraSyncComponent)
    def onSyncCreated(self, go, syncComponent):
        _logger.debug('onCameraCreated %s %s', syncComponent.viewLayoutPath, syncComponent.viewState)
        if syncComponent.viewLayoutID:
            self.__viewGOLinks[syncComponent.viewLayoutID][go.id] = CGF.ComponentLink(go, ViewCameraSyncComponent)

    @onRemovedQuery(CGF.GameObject, ViewCameraSyncComponent)
    def onSyncRemoved(self, go, syncComponent):
        _logger.debug('onSyncRemoved %s %s', syncComponent.viewLayoutPath, syncComponent.viewState)
        if syncComponent.viewLayoutID in self.__viewGOLinks:
            componentLink = self.__viewGOLinks[syncComponent.viewLayoutID].pop(go.id)
            if componentLink:
                if componentLink.gameObject.findComponentByType(ViewComponent) is not None:
                    componentLink.gameObject.removeComponentByType(ViewComponent)
        return

    def __onViewStatusChanged(self, uniqueID, newState):
        if newState == ViewStatus.LOADING:
            view = self.__guiLoader.windowsManager.getView(uniqueID)
            syncComponentLinks = self.__viewGOLinks.get(view.layoutID, {})
            if syncComponentLinks:
                pass
            for syncComponentLink in syncComponentLinks.itervalues():
                go = syncComponentLink.gameObject
                if go.findComponentByType(ViewComponent) is None:
                    go.createComponent(ViewComponent, view)

        elif newState == ViewStatus.DESTROYING:
            view = self.__guiLoader.windowsManager.getView(uniqueID)
            syncComponentLinks = self.__viewGOLinks.get(view.layoutID, {})
            if syncComponentLinks:
                view.onInternalViewStateChanged.clear()
            for syncComponentLink in syncComponentLinks.itervalues():
                go = syncComponentLink.gameObject
                viewComponent = go.findComponentByType(ViewComponent)
                if viewComponent and viewComponent.uniqueID == uniqueID:
                    go.removeComponentByType(ViewComponent)

        return
