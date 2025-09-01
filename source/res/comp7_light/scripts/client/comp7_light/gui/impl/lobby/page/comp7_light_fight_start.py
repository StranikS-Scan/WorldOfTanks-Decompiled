# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/page/comp7_light_fight_start.py
from __future__ import absolute_import
from gui.impl.lobby.page.fight_start import FightStartPresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightFightStartPresenter(FightStartPresenter):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def _getEvents(self):
        return super(Comp7LightFightStartPresenter, self)._getEvents() + ((self.__comp7LightController.onModeConfigChanged, self._onFightButtonUpdate),)
