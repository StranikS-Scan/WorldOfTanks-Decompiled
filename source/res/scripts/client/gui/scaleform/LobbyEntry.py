# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/LobbyEntry.py
from gui.Scaleform.framework.managers.CacheManager import CacheManager
from gui.Scaleform.framework.managers.TutorialManager import TutorialManager
from gui.Scaleform.framework.managers.event_logging import EventLogManager
from gui.Scaleform.managers.context_menu import ContextMenuManager
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.application import App
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.SoundManager import SoundManager
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.Scaleform.managers.GuiItemsManager import GuiItemsManager
from gui.Scaleform.managers.VoiceChatManager import VoiceChatManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.GameInputMgr import GameInputMgr
from gui.Scaleform.managers.TweenSystem import TweenManager
from gui.shared import EVENT_BUS_SCOPE

class LobbyEntry(App):

    def __init__(self, appNS):
        super(LobbyEntry, self).__init__(appNS)

    def _createManagers(self):
        super(LobbyEntry, self)._createManagers()
        self._varsMgr = GlobalVarsManager()
        self._soundMgr = SoundManager()
        self._colorSchemeMgr = ColorSchemeManager()
        self._eventLogMgr = EventLogManager()
        self._contextMgr = ContextMenuManager(self.proxy)
        self._popoverManager = PopoverManager(EVENT_BUS_SCOPE.LOBBY)
        self._guiItemsMgr = GuiItemsManager()
        self._voiceChatMgr = VoiceChatManager(self.proxy)
        self._utilsMgr = UtilsManager()
        self._tweenMgr = TweenManager()
        self._gameInputMgr = GameInputMgr()
        self._cacheMgr = CacheManager()
        self._tutorialMgr = TutorialManager(self.proxy, True, 'gui/tutorial-lobby-gui.xml')

    def _loadCursor(self):
        self._containerMgr.load(VIEW_ALIAS.CURSOR)

    def _loadWaiting(self):
        self._containerMgr.load(VIEW_ALIAS.WAITING)
