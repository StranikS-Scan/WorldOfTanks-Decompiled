# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from adisp import adisp_process
from constants import QUEUE_TYPE
from fun_random.gui.shared.event_dispatcher import showFunRandomInfoPage
from fun_random.gui.prb_control.prb_config import PrebattleActionName, SelectorBattleTypes
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.battle_selector_item import SelectorItem
from gui.prb_control.entities.base.ctx import PrbAction
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

def addFunRandomBattleType(items):
    items.append(_FunRandomItem(backport.text(R.strings.menu.headerButtons.battle.types.funRandom()), PrebattleActionName.FUN_RANDOM, 2, SelectorBattleTypes.FUN_RANDOM))


class _FunRandomItem(SelectorItem):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_FunRandomItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isVisible = self.__getIsVisible()

    def getSpecialBGIcon(self):
        return backport.image(R.images.gui.maps.icons.buttons.selectorRendererBGEvent()) if self.__funRandomCtrl.isAvailable() else ''

    @adisp_process
    def _doSelect(self, dispatcher):
        if self.__funRandomCtrl.getCurrentSeason() is None and self.__funRandomCtrl.getNextSeason() is not None:
            showFunRandomInfoPage()
            if self._isNew:
                selectorUtils.setBattleTypeAsKnown(self._selectorType)
        elif self.__funRandomCtrl.isAvailable():
            isSuccess = yield dispatcher.doSelectAction(PrbAction(self._data))
            if isSuccess and self._isNew:
                selectorUtils.setBattleTypeAsKnown(self._selectorType)
        return

    def _update(self, state):
        isDisabled = self.__funRandomCtrl.getCurrentSeason() is not None and self.__funRandomCtrl.isFrozen()
        self._isDisabled = state.hasLockedState or isDisabled
        self._isVisible = self.__getIsVisible()
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.FUN_RANDOM)
        return

    def __getIsVisible(self):
        hasSeasons = bool(self.__funRandomCtrl.getCurrentSeason() or self.__funRandomCtrl.getNextSeason())
        return self.__funRandomCtrl.isEnabled() and hasSeasons
