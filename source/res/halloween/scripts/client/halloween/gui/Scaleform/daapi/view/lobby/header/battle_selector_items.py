# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from adisp import adisp_process
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import PrbAction
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem, SpecialSquadItem
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from skeletons.gui.game_control import IHalloweenController
from halloween_common.halloween_constants import QUEUE_TYPE, PREBATTLE_TYPE
from halloween.gui.halloween_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES

def addHalloweenBattleType(items):
    items.append(_HalloweenItem(backport.text(R.strings.halloween_hangar.battleSelector.headerButton.title()), PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE, 2, SELECTOR_BATTLE_TYPES.HALLOWEEN_BATTLE))


def addHalloweenSquadType(items):
    items.append(HalloweenSquadItem('Halloween squad', PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE_SQUAD, 2))


_R_ICONS = R.images.gui.maps.icons

class _HalloweenItem(_SelectorItem):
    __controller = dependency.descriptor(IHalloweenController)

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.HALLOWEEN_BATTLES) or state.isQueueSelected(QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL)
        self._isVisible = self._isEnabled()
        self._isLocked = not self.__controller.isCurrentQueueEnabled()

    @adisp_process
    def _doSelect(self, dispatcher):
        if self._isEnabled():
            isSuccess = yield dispatcher.doSelectAction(PrbAction(self.getData()))
            if isSuccess and self._isNew:
                selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def _isEnabled(self):
        return self.__controller.isAvailable() and not self.__controller.isPostPhase()

    def getSmallIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.halloween())

    def getLargerIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_64x64.halloween())


class HalloweenSquadItem(SpecialSquadItem):
    __controller = dependency.descriptor(IHalloweenController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(HalloweenSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.HALLOWEEN_BATTLES
        self._isVisible = self.__controller.isEnabled()
        self._isSpecialBgIcon = True
        self._isDescription = False

    @property
    def squadIcon(self):
        return backport.image(_R_ICONS.battleTypes.c_40x40.halloweenSquad())

    def _update(self, state):
        super(HalloweenSquadItem, self)._update(state)
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.HALLOWEEN_BATTLES) or state.isQueueSelected(QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL)
        inQueue = False
        if state.ctrlTypeID == CTRL_ENTITY_TYPE.PREQUEUE:
            inQueue = state.entityTypeID in (QUEUE_TYPE.HALLOWEEN_BATTLES, QUEUE_TYPE.HALLOWEEN_BATTLES_WHEEL)
        self._isVisible = self.__controller.isEnabled() and inQueue
