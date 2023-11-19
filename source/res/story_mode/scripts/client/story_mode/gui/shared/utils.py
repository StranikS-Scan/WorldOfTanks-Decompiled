# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/shared/utils.py
import typing
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.entities.DisposableEntity import EntityState
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from wg_async import wg_async, AsyncEvent, wg_await
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.application import AppEntry

@wg_async
def waitForLobby():
    appLoader = dependency.instance(IAppLoader)
    lobbyApp = appLoader.getDefLobbyApp()
    lobbyView = lobbyApp.containerManager.getContainer(WindowLayer.VIEW).getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY})
    if lobbyView.getState() != EntityState.CREATED:
        asyncEvent = AsyncEvent()

        def onLobbyViewCreated(_):
            asyncEvent.set()

        lobbyView.onCreated += onLobbyViewCreated
        yield wg_await(asyncEvent.wait())
        lobbyView.onCreated -= onLobbyViewCreated
