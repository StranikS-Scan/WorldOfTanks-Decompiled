# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/presenters/battle_royale_platoon_presenter.py
from skeletons.gui.game_control import IBattleRoyaleController
from gui.impl.lobby.page.platoon_presenter import PlatoonPresenter
from helpers import dependency

class BattleRoyalePlatoonPresenter(PlatoonPresenter):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def _getEvents(self):
        return super(BattleRoyalePlatoonPresenter, self)._getEvents() + ((self.__battleRoyaleController.onPrimeTimeStatusUpdated, self.__update),)

    def __update(self, *_):
        self._onUpdatePlatoon()
