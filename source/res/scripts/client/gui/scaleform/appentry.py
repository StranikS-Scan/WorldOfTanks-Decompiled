# Embedded file name: scripts/client/gui/Scaleform/AppEntry.py
from gui.Scaleform.framework.managers.CacheManager import CacheManager
from gui.Scaleform.framework.managers.event_logging import EventLogManager
from gui.Scaleform.managers.context_menu import ContextMenuManager
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.utils import decorators
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.daapi.business_layer import BusinessHandler
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.application import App
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.SoundManager import SoundManager
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.Scaleform.managers.GuiItemsManager import GuiItemsManager
from gui.Scaleform.managers.VoiceChatManager import VoiceChatManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.GameInputMgr import GameInputMgr
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.managers.TweenSystem import TweenManager

class AppEntry(App):

    def __init__(self):
        businessHandler = BusinessHandler()
        businessHandler.create()
        super(AppEntry, self).__init__(businessHandler)

    def _createManagers(self):
        super(AppEntry, self)._createManagers()
        self._varsMgr = GlobalVarsManager()
        self._soundMgr = SoundManager()
        self._colorSchemeMgr = ColorSchemeManager()
        self._eventLogMgr = EventLogManager()
        self._contextMgr = ContextMenuManager()
        self._popoverManager = PopoverManager()
        self._guiItemsMgr = GuiItemsManager()
        self._voiceChatMgr = VoiceChatManager()
        self._utilsMgr = UtilsManager()
        self._tweenMgr = TweenManager()
        self._gameInputMgr = GameInputMgr()
        self._cacheMgr = CacheManager()

    def _loadCursor(self):
        self._containerMgr.load(VIEW_ALIAS.CURSOR)

    def _loadWaiting(self):
        self._containerMgr.load(VIEW_ALIAS.WAITING)

    def afterCreate(self):
        super(AppEntry, self).afterCreate()
        self.fireEvent(events.GUICommonEvent(events.GUICommonEvent.APP_STARTED))
        self.addListener(events.GUICommonEvent.APP_LOGOFF, self.__logoffHandler, EVENT_BUS_SCOPE.GLOBAL)

    def beforeDelete(self):
        self.removeListener(events.GUICommonEvent.APP_LOGOFF, self.__logoffHandler, EVENT_BUS_SCOPE.GLOBAL)
        super(AppEntry, self).beforeDelete()

    def logOffAfterFrameworkInit(self):
        self.fireEventAfterInitialization(events.GUICommonEvent(events.GUICommonEvent.APP_LOGOFF), EVENT_BUS_SCOPE.GLOBAL)

    def __logoffHandler(self, event):
        self.logoff(True)

    @decorators.process('disconnect')
    def logoff(self, disconnectNow = False):
        if self.initialized:
            criteria = {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOGIN}
            if not self.containerManager.isViewAvailable(ViewTypes.VIEW, criteria=criteria):
                self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOGIN))
        else:
            self.logOffAfterFrameworkInit()
        yield super(AppEntry, self).logoff(disconnectNow)
