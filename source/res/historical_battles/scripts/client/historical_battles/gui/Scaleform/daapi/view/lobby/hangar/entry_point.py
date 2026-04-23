# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/hangar/entry_point.py
from gui.Scaleform.daapi.view.meta.SE22EntryPointMeta import SE22EntryPointMeta
from helpers import dependency
from historical_battles.gui.impl.lobby.entry_point_view import EntryPointView
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

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
