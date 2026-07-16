# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/on_click_components.py
from __future__ import absolute_import
import logging
import CGF
from GenericComponents import VSEComponent
from adisp import adisp_process
from cgf_script.registration import ComponentProperty, registerComponent
from constants import MarathonConfig, IS_CLIENT
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.utils import IHangarSpace
from cgf_components.hover_component import IsHoveredComponent, SelectionComponent
if IS_CLIENT:
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.game_control.links import URLMacros
    from gui.shared.event_dispatcher import showBrowserOverlayView
_logger = logging.getLogger(__name__)

@registerComponent
class OpenBrowserOnClickComponent(object):
    domain = CGF.Domain.Client
    editorTitle = 'Open Browser On Click'
    urlProvider = ComponentProperty(type=CGF.PropertyType.String, editorName='url provider', value='MARATHON_VIDEO_URL_PROVIDER')

    def __init__(self):
        super(OpenBrowserOnClickComponent, self).__init__()
        self.__urlParser = URLMacros()

    def doAction(self):
        self.__openBrowser()

    @adisp_process
    def __openBrowser(self):
        getterFunc = URL_PROVIDERS[self.urlProvider]
        unparsedUrl = getterFunc()
        url = yield self.__urlParser.parse(unparsedUrl)
        showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_OVERLAY)


def getMarathonVideoUrl():
    lobbyContext = dependency.instance(ILobbyContext)
    return lobbyContext.getServerSettings().getMarathonConfig()[MarathonConfig.VIDEO_CONTENT_URL]


URL_PROVIDERS = {'MARATHON_VIDEO_URL_PROVIDER': getMarathonVideoUrl}

class ClientSelectableComponentsSystem(CGF.System):
    BrowserActivated = CGF.ActivateReaction(CGF.ReactRo(OpenBrowserOnClickComponent), CGF.Rw(SelectionComponent))
    BrowserDeactivated = CGF.DeactivateReaction(CGF.ReactRo(OpenBrowserOnClickComponent), CGF.Rw(SelectionComponent))
    Reactions = CGF.Reactions(BrowserActivated, BrowserDeactivated)

    def update(self):
        for openBrowserOnClickComponent, selectionComponent in self.reaction(self.BrowserDeactivated):
            self.handleOpenBrowserOnClickRemoved(openBrowserOnClickComponent, selectionComponent)

        for openBrowserOnClickComponent, selectionComponent in self.reaction(self.BrowserActivated):
            self.handleOpenBrowserOnClickAdded(openBrowserOnClickComponent, selectionComponent)

    def handleOpenBrowserOnClickAdded(self, openBrowserOnClickComponent, selectionComponent):
        selectionComponent.onClickAction += openBrowserOnClickComponent.doAction

    def handleOpenBrowserOnClickRemoved(self, openBrowserOnClickComponent, selectionComponent):
        selectionComponent.onClickAction -= openBrowserOnClickComponent.doAction


class ClickVSEComponentsSystem(CGF.System):
    ComponentActivated = CGF.ActivateReaction(CGF.ReactRw(VSEComponent), CGF.ReactRw(SelectionComponent))
    ComponentDeactivated = CGF.DeactivateReaction(CGF.ReactRw(VSEComponent), CGF.ReactRw(SelectionComponent))
    Reactions = CGF.Reactions(ComponentActivated, ComponentDeactivated)

    def update(self):
        for vseComponent, selectionComponent in self.reaction(self.ComponentDeactivated):
            self.handleComponentRemoved(selectionComponent, vseComponent)

        for vseComponent, selectionComponent in self.reaction(self.ComponentActivated):
            self.handleComponentAdded(selectionComponent, vseComponent)

    def handleComponentAdded(self, selectionComponent, vseComponent):
        ctx = vseComponent.context
        if ctx is not None:
            selectionComponent.onClickAction += ctx.onGameObjectClick
        return

    def handleComponentRemoved(self, selectionComponent, vseComponent):
        ctx = vseComponent.context
        if ctx is not None:
            selectionComponent.onClickAction -= ctx.onGameObjectClick
        return


class ClickSystem(CGF.System):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    ClickIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Rw(SelectionComponent), CGF.Has(IsHoveredComponent))
    Reactions = CGF.Reactions(ClickIterate)

    def __init__(self, *args):
        super(ClickSystem, self).__init__(*args)
        self._selectedGO = None
        return

    def onMappingLoaded(self):
        self._hangarSpace.onMouseDown += self._onMouseDown
        self._hangarSpace.onMouseUp += self._onMouseUp

    def onMappingUnloaded(self):
        self._hangarSpace.onMouseDown -= self._onMouseDown
        self._hangarSpace.onMouseUp -= self._onMouseUp

    def _onMouseDown(self):
        clickIterate = self.reaction(self.ClickIterate)
        for go, _ in clickIterate:
            self._selectedGO = go

    def _onMouseUp(self):
        clickIterate = self.reaction(self.ClickIterate)
        for go, selectionComponent in clickIterate:
            if self._selectedGO == go:
                _logger.info('ClickManager::Clicked')
                selectionComponent.onClickAction()
