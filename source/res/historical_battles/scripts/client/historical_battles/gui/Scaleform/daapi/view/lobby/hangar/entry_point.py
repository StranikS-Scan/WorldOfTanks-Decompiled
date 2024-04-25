# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/hangar/entry_point.py
from gui.Scaleform.daapi.view.meta.SE22EntryPointMeta import SE22EntryPointMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.shared.system_factory import registerBannerEntryPointValidator, registerBannerEntryPointLUIRule
from helpers import dependency
from historical_battles.gui.impl.lobby.entry_point_view import EntryPointView
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY
from skeletons.gui.lobby_context import ILobbyContext
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from gui.limited_ui.lui_rules_storage import LuiRules

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isSE22EntryPointAvailable(lobbyContext=None):
    hbConfig = lobbyContext.getServerSettings().getSettings().get(HB_GAME_PARAMS_KEY, {})
    return hbConfig.get('isEnabled', False)


def addSE22EntryPoint():
    registerBannerEntryPointValidator(HANGAR_ALIASES.SE22_EVENT_ENTRY_POINT, isSE22EntryPointAvailable)
    registerBannerEntryPointLUIRule(HANGAR_ALIASES.SE22_EVENT_ENTRY_POINT, LuiRules.HB_ENTRY_POINT)


class EntryPoint(SE22EntryPointMeta):
    _gameEventController = dependency.descriptor(IGameEventController)

    def _makeInjectView(self):
        self.__view = EntryPointView()
        return self.__view

    def _populate(self):
        super(EntryPoint, self)._populate()
        self.__view.onAnimationFinished += self.__onShowingAnimationFinish

    def _dispose(self):
        self.__view.onAnimationFinished -= self.__onShowingAnimationFinish
        super(EntryPoint, self)._dispose()

    def _hasNewMark(self):
        latestFront = self._gameEventController.frontController.getLatestFront()
        return latestFront is not None and not self._gameEventController.frontController.isFrontSeen(latestFront.getID())

    def __onShowingAnimationFinish(self):
        self.setIsNewS(self._hasNewMark())
