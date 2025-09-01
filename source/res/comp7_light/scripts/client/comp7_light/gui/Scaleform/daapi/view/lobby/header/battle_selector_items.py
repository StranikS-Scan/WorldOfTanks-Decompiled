# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from comp7_light_constants import PREBATTLE_TYPE
from comp7_light.gui.comp7_light_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from comp7_light.gui.prb_control.entities import comp7_light_prb_helpers
from constants import QUEUE_TYPE
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import SelectorItem, SpecialSquadItem
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

def addComp7LightBattleType(items):
    items.append(_Comp7LightItem(backport.text(R.strings.menu.headerButtons.battle.types.comp7Light()), PREBATTLE_ACTION_NAME.COMP7_LIGHT, 1, SELECTOR_BATTLE_TYPES.COMP7_LIGHT))


def addComp7LightSquadType(items):
    items.append(_Comp7LightSquadItem(backport.text(R.strings.menu.headerButtons.battle.types.comp7LightSquad()), PREBATTLE_ACTION_NAME.COMP7_LIGHT_SQUAD, 1))


class _Comp7LightItem(SelectorItem):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def isRandomBattle(self):
        return True

    def select(self):
        comp7_light_prb_helpers.selectComp7Light()
        selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def _update(self, state):
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.COMP7_LIGHT)
        self._isVisible = self.__comp7LightController.isEnabled()
        self._isDisabled = state.hasLockedState or self.__comp7LightController.isFrozen()


class _Comp7LightSquadItem(SpecialSquadItem):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_Comp7LightSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.COMP7_LIGHT
        self._isVisible = self.__comp7LightController.isEnabled() and self.__comp7LightController.isInPrimeTime()
        primeTimeStatus, _, _ = self.__comp7LightController.getPrimeTimeStatus()
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE

    def _update(self, state):
        super(_Comp7LightSquadItem, self)._update(state)
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.COMP7_LIGHT)
        self._isVisible = self.__comp7LightController.isEnabled() and self.__comp7LightController.isInPrimeTime() and state.isInPreQueue(queueType=QUEUE_TYPE.COMP7_LIGHT)
        primeTimeStatus, _, _ = self.__comp7LightController.getPrimeTimeStatus()
        self._isDisabled = self._isDisabled or primeTimeStatus != PrimeTimeStatus.AVAILABLE
