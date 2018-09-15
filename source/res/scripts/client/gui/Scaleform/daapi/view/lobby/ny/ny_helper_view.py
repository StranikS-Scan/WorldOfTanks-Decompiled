# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_helper_view.py
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager, INewYearController
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.shared import events, EVENT_BUS_SCOPE
from tutorial.gui.Scaleform.offbattle.settings import OFFBATTLE_VIEW_ALIAS
_FREEZING_VIEW_ALIASES = (VIEW_ALIAS.LOBBY_HANGAR,
 VIEW_ALIAS.BATTLE_QUEUE,
 VIEW_ALIAS.BADGES_PAGE,
 CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY,
 PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY,
 PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY,
 PREBATTLE_ALIASES.SQUAD_WINDOW_PY,
 FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS,
 OFFBATTLE_VIEW_ALIAS.GREETING_DIALOG,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS,
 RANKEDBATTLES_ALIASES.RANKED_BATTLES_BROWSER_VIEW)

class NYHelperView(LobbySubView):
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    _newYearController = dependency.descriptor(INewYearController)

    def __init__(self, ctx=None):
        super(NYHelperView, self).__init__(ctx)
        ctx = ctx or {}
        self.__previewAlias = ctx['previewAlias'] if 'previewAlias' in ctx else VIEW_ALIAS.LOBBY_HANGAR

    def delaySwitchTo(self, viewAlias, freezeCbk, unfreezeCbk):
        if self._customizableObjMgr.state and viewAlias in _FREEZING_VIEW_ALIASES:
            freezeCbk()
            self._customizableObjMgr.switchTo(None, unfreezeCbk)
            return True
        else:
            return False

    def _populate(self):
        super(NYHelperView, self)._populate()
        self._newYearController.onStateChanged += self.__onNyStateChanged

    def _dispose(self):
        self._newYearController.onStateChanged -= self.__onNyStateChanged
        super(NYHelperView, self)._dispose()

    def _switchBack(self, **kwargs):
        self.__switchToView(self.__previewAlias, kwargs)

    def _switchToCraft(self, **kwargs):
        self.__switchToView(VIEW_ALIAS.LOBBY_NY_CRAFT, kwargs)

    def _switchToBreak(self, **kwargs):
        self.__switchToView(VIEW_ALIAS.LOBBY_NY_BREAK, kwargs)

    def _switchToNYMain(self, **kwargs):
        self.__switchToView(VIEW_ALIAS.LOBBY_NY_SCREEN, kwargs)

    def _switchToRewards(self, **kwargs):
        self.__switchToView(VIEW_ALIAS.LOBBY_NY_REWARDS, kwargs)

    def _switchToGroups(self, **kwargs):
        self.__switchToView(VIEW_ALIAS.LOBBY_NY_COLLECTIONS_GROUP, kwargs)

    def _switchToCollection(self, **kwargs):
        self.__switchToView(VIEW_ALIAS.LOBBY_NY_COLLECTIONS, kwargs)

    def __onNyStateChanged(self, _):
        if not self._newYearController.isAvailable():
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __fadedSwitch(self, callback):
        app = self.app
        if app and app.faderManager:
            app.faderManager.startFade([callback])

    def __switchToView(self, viewAlias, ctx):
        self.__fadedSwitch(lambda : self.fireEvent(events.LoadViewEvent(viewAlias, ctx=ctx), EVENT_BUS_SCOPE.LOBBY))
