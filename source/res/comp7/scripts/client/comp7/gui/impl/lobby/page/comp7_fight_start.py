# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/page/comp7_fight_start.py
from __future__ import absolute_import
from gui.impl.lobby.page.fight_start import FightStartPresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7FightStartPresenter(FightStartPresenter):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def _getEvents(self):
        return super(Comp7FightStartPresenter, self)._getEvents() + ((self.__comp7Controller.onQualificationStateUpdated, self._onFightButtonUpdate),
         (self.__comp7Controller.onBanUpdated, self._onFightButtonUpdate),
         (self.__comp7Controller.onModeConfigChanged, self._onFightButtonUpdate),
         (self.__comp7Controller.onOfflineStatusUpdated, self._onFightButtonUpdate))
