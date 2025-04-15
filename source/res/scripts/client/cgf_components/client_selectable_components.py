# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/client_selectable_components.py
import CGF
import Event
from adisp import adisp_process
from cgf_script.component_meta_class import registerComponent, CGFMetaTypes, ComponentProperty
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from constants import MarathonConfig, IS_CLIENT
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if IS_CLIENT:
    from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
    from gui.game_control.links import URLMacros
    from gui.shared.event_dispatcher import showBrowserOverlayView

@registerComponent
class OnClickComponent(object):
    onClickAction = Event.Event()

    def doAction(self):
        self.onClickAction()


@registerComponent
class OpenBrowserOnClickComponent(object):
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

    @onAddedQuery(OpenBrowserOnClickComponent, OnClickComponent)
    def handleOpenBrowserOnClickAdded(self, openBrowserOnClickComponent, onClickComponent):
        onClickComponent.onClickAction += openBrowserOnClickComponent.doAction

    @onRemovedQuery(OpenBrowserOnClickComponent, OnClickComponent)
    def handleOpenBrowserOnClickRemoved(self, openBrowserOnClickComponent, onClickComponent):
        onClickComponent.onClickAction -= openBrowserOnClickComponent.doAction
