# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/page/comp7_light_prebattle_presenter.py
from __future__ import absolute_import
from gui.impl.lobby.page.prebattle_presenter import PrebattlePresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController
from skeletons.gui.shared import IItemsCache

class Comp7LightPrebattlePresenter(PrebattlePresenter):
    __comp7LightController = dependency.descriptor(IComp7LightController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def _getEvents(self):
        return super(Comp7LightPrebattlePresenter, self)._getEvents() + ((self.__comp7LightController.onModeConfigChanged, self._onPrebattleUpdate), (self.__itemsCache.onSyncCompleted, self._update))

    def _update(self, _, __):
        self._onPrebattleUpdate()
