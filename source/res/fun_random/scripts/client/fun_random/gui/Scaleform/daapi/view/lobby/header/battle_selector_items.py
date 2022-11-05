# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from adisp import adisp_process
from constants import QUEUE_TYPE
from fun_random.gui.feature.fun_constants import FunSubModesState
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.fun_gui_constants import PrebattleActionName, SelectorBattleTypes
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.battle_selector_item import SelectorItem
from helpers import dependency
from skeletons.gui.game_control import IBootcampController

def addFunRandomBattleType(items):
    items.append(_FunRandomItem(backport.text(R.strings.menu.headerButtons.battle.types.funRandom()), PrebattleActionName.FUN_RANDOM, 2, SelectorBattleTypes.FUN_RANDOM))


class _FunRandomItem(SelectorItem, FunSubModesWatcher):
    __bootcampController = dependency.descriptor(IBootcampController)
    _HIDDEN_STATES = (FunSubModesState.UNDEFINED, FunSubModesState.AFTER_SEASON)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_FunRandomItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isVisible = self.__getIsVisible()

    def _update(self, state):
        self._isVisible, self._isDisabled = self.__getIsVisible(), state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.FUN_RANDOM)

    @adisp_process
    def _doSelect(self, dispatcher):
        yield self.selectFunRandomBattle()

    def __getIsVisible(self):
        subModesState = self._funRandomCtrl.subModesInfo.getSubModesStatus().state
        return not self.__bootcampController.isInBootcamp() and subModesState not in self._HIDDEN_STATES
