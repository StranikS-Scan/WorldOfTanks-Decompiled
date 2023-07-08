# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/on_click_components.py
import logging
import CGF
from GenericComponents import VSEComponent
from adisp import adisp_process
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from constants import MarathonConfig, IS_CLIENT
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.utils import IHangarSpace
from hover_component import IsHoveredComponent, SelectionComponent
if IS_CLIENT:
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.game_control.links import URLMacros
    from gui.shared.event_dispatcher import showBrowserOverlayView
_logger = logging.getLogger(__name__)

@registerComponent
class OpenBrowserOnClickComponent(object):
    domain = CGF.DomainOption.DomainClient
    urlProvider = ComponentProperty(type=CGFMetaTypes.STRING, editorName='url provider', value='MARATHON_VIDEO_URL_PROVIDER')

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

@autoregister(presentInAllWorlds=False, category='lobby')
class ClientSelectableComponentsManager(CGF.ComponentManager):

    @onAddedQuery(OpenBrowserOnClickComponent, SelectionComponent)
    def handleOpenBrowserOnClickAdded(self, openBrowserOnClickComponent, selectionComponent):
        selectionComponent.onClickAction += openBrowserOnClickComponent.doAction

    @onRemovedQuery(OpenBrowserOnClickComponent, SelectionComponent)
    def handleOpenBrowserOnClickRemoved(self, openBrowserOnClickComponent, selectionComponent):
        selectionComponent.onClickAction -= openBrowserOnClickComponent.doAction


@autoregister(presentInAllWorlds=True, category='lobby')
class ClickVSEComponentsManager(CGF.ComponentManager):

    @onAddedQuery(SelectionComponent, VSEComponent)
    def handleComponentAdded(self, selectionComponent, vseComponent):
        selectionComponent.onClickAction += vseComponent.context.onGameObjectClick

    @onRemovedQuery(SelectionComponent, VSEComponent)
    def handleComponentRemoved(self, selectionComponent, vseComponent):
        selectionComponent.onClickAction -= vseComponent.context.onGameObjectClick


class ClickManager(CGF.ComponentManager):
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, *args):
        super(ClickManager, self).__init__(*args)
        self._selectedGO = None
        return

    def activate(self):
        self._hangarSpace.onMouseDown += self._onMouseDown
        self._hangarSpace.onMouseUp += self._onMouseUp

    def deactivate(self):
        self._hangarSpace.onMouseDown -= self._onMouseDown
        self._hangarSpace.onMouseUp -= self._onMouseUp

    def _onMouseDown(self):
        clickQuery = CGF.Query(self.spaceID, (CGF.GameObject, IsHoveredComponent, SelectionComponent))
        for go, _, __ in clickQuery:
            self._selectedGO = go

    def _onMouseUp(self):
        clickQuery = CGF.Query(self.spaceID, (CGF.GameObject, IsHoveredComponent, SelectionComponent))
        for go, _, selectionComponent in clickQuery:
            if self._selectedGO == go:
                _logger.info('ClickManager::Clicked')
                selectionComponent.onClickAction()
