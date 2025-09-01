# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/page/comp7_prebattle_presenter.py
from __future__ import absolute_import
from gui.impl.lobby.page.prebattle_presenter import PrebattlePresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache

class Comp7PrebattlePresenter(PrebattlePresenter):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)

    def _getEvents(self):
        return super(Comp7PrebattlePresenter, self)._getEvents() + ((self.__comp7Controller.onQualificationStateUpdated, self._onPrebattleUpdate),
         (self.__comp7Controller.onBanUpdated, self._onPrebattleUpdate),
         (self.__comp7Controller.onModeConfigChanged, self._onPrebattleUpdate),
         (self.__comp7Controller.onOfflineStatusUpdated, self._onPrebattleUpdate),
         (self.__itemsCache.onSyncCompleted, self._update))

    def _update(self, _, __):
        self._onPrebattleUpdate()
