# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/client_selectable_components.py
import CGF
import Event
from adisp import process
from cgf_script.component_meta_class import CGFComponent, CGFMetaTypes, ComponentProperty
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from constants import MarathonConfig, IS_CLIENT
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.game_control.links import URLMacros
from helpers import dependency
from lunar_ny import ILunarNYController
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.lunar_ny.loggers import LunarSelectableObject3dLogger
if IS_CLIENT:
    from gui.shared.event_dispatcher import showBrowserOverlayView
    from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showLunarNYMainView

class OnClickComponent(CGFComponent):
    onClickAction = Event.Event()

    def doAction(self):
        self.onClickAction()


class OpenBrowserOnClickComponent(CGFComponent):
    urlProvider = ComponentProperty(type=CGFMetaTypes.STRING, editorName='url provider', value='MARATHON_VIDEO_URL_PROVIDER')

    def __init__(self):
        super(OpenBrowserOnClickComponent, self).__init__()
        self.__urlParser = URLMacros()

    def doAction(self):
        self.__openBrowser()

    @process
    def __openBrowser(self):
        getterFunc = URL_PROVIDERS[self.urlProvider]
        unparsedUrl = getterFunc()
        url = yield self.__urlParser.parse(unparsedUrl)
        showBrowserOverlayView(url, alias=VIEW_ALIAS.BROWSER_OVERLAY)


class OpenEventOnClickComponent(CGFComponent):
    eventName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='event name', value='')

    def doAction(self):
        handler = OPEN_EVENT_HANDLERS.get(self.eventName, None)
        if handler is not None:
            handler()
        return


class SwitchSelectableStateComponent(CGFComponent):
    selectableEnabled = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='selectable enabled', value=True)
    objectName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='object name', value='default')
    onStateChanged = Event.Event()

    def setEnabled(self, enabled):
        self.selectableEnabled = enabled
        self.onStateChanged(self.selectableEnabled)


def getMarathonVideoUrl():
    lobbyContext = dependency.instance(ILobbyContext)
    return lobbyContext.getServerSettings().getMarathonConfig()[MarathonConfig.VIDEO_CONTENT_URL]


def showLunarNYHandler():
    showLunarNYMainView()
    LunarSelectableObject3dLogger().logClick()


URL_PROVIDERS = {'MARATHON_VIDEO_URL_PROVIDER': getMarathonVideoUrl}

class EventNames(CONST_CONTAINER):
    LUNAR_NY = 'lunarNY'


OPEN_EVENT_HANDLERS = {EventNames.LUNAR_NY: showLunarNYHandler}

@autoregister(presentInAllWorlds=False, category='lobby')
class ClientSelectableComponentsManager(CGF.ComponentManager):

    @onAddedQuery(OpenBrowserOnClickComponent, OnClickComponent)
    def handleOpenBrowserOnClickAdded(self, openBrowserOnClickComponent, onClickComponent):
        onClickComponent.onClickAction += openBrowserOnClickComponent.doAction

    @onRemovedQuery(OpenBrowserOnClickComponent, OnClickComponent)
    def handleOpenBrowserOnClickRemoved(self, openBrowserOnClickComponent, onClickComponent):
        onClickComponent.onClickAction -= openBrowserOnClickComponent.doAction

    @onAddedQuery(OpenEventOnClickComponent, OnClickComponent)
    def handleOpenEventOnClickAdded(self, openEventOnClickComponent, onClickComponent):
        onClickComponent.onClickAction += openEventOnClickComponent.doAction

    @onRemovedQuery(OpenEventOnClickComponent, OnClickComponent)
    def handleOpenEventOnClickRemoved(self, openEventOnClickComponent, onClickComponent):
        onClickComponent.onClickAction -= openEventOnClickComponent.doAction


@autoregister(presentInAllWorlds=False, category='lobby')
class LunarNYEntryPointManager(CGF.ComponentManager):
    __lunarNYController = dependency.descriptor(ILunarNYController)
    switchSelectableQuery = CGF.QueryConfig(SwitchSelectableStateComponent)

    def activate(self):
        self.__lunarNYController.onStatusChange += self.__onStatusChange

    def deactivate(self):
        self.__lunarNYController.onStatusChange -= self.__onStatusChange

    @onAddedQuery(SwitchSelectableStateComponent)
    def handleSwitchSelectableStateAdded(self, switchSelectableStateComponent):
        if switchSelectableStateComponent.objectName == EventNames.LUNAR_NY:
            switchSelectableStateComponent.setEnabled(self.__lunarNYController.isActive())

    def __onStatusChange(self):
        for component in self.switchSelectableQuery:
            if component.objectName == EventNames.LUNAR_NY:
                component.setEnabled(self.__lunarNYController.isActive())
