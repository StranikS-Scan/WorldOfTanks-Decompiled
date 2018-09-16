# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/StrongholdBattlesListView.py
import BigWorld
from adisp import process
from helpers import dependency
from skeletons.gui.game_control import IBrowserController
from debug_utils import LOG_ERROR
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.clans.clan_helpers import getStrongholdUrl
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView
from gui.Scaleform.daapi.view.lobby.strongholds.web_handlers import createStrongholdsWebHandlers
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from shared_utils import BoundMethodWeakref

class StrongholdBattlesListView(BaseRallyListView):
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(StrongholdBattlesListView, self).__init__()
        self.childBrowsers = []
        self.__browserId = 0
        self.__browserCreated = False

    def addChildBrowserAlias(self, browserAlias):
        self.childBrowsers.append(browserAlias)

    def viewSize(self, width, height):
        self.__loadBrowser(width, height)

    def _populate(self):
        super(StrongholdBattlesListView, self)._populate()
        self.fireEvent(events.RenameWindowEvent(events.RenameWindowEvent.RENAME_WINDOW, ctx={'data': FORTIFICATIONS.SORTIE_INTROVIEW_TITLE}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        for browserAlias in self.childBrowsers:
            app = self.app
            if app is not None and app.containerManager is not None:
                browserWindow = app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.UNIQUE_NAME: browserAlias})
                if browserWindow is not None:
                    browserWindow.destroy()

        if not self.__browserCreated:
            self.browserCtrl.delBrowser(self.__browserId)
        super(StrongholdBattlesListView, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(StrongholdBattlesListView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.init(self.__browserId, createStrongholdsWebHandlers(onBrowserOpen=BoundMethodWeakref(self.addChildBrowserAlias)))
            self.__browserCreated = True

    @process
    def __loadBrowser(self, width, height):
        battlesListUrl = getStrongholdUrl('battlesListUrl')
        if battlesListUrl is not None:
            self.__browserId = yield self.browserCtrl.load(url=battlesListUrl, useBrowserWindow=False, showBrowserCallback=self.__showBrowser, browserSize=(width, height))
        browser = self.browserCtrl.getBrowser(self.__browserId)
        if browser:
            browser.useSpecialKeys = False
        else:
            LOG_ERROR('Setting "StrongholdsBattlesListUrl" missing!')
        return

    def __showBrowser(self):
        BigWorld.callback(0.01, self.as_loadBrowserS)
