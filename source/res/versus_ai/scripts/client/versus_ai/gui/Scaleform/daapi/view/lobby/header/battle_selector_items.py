# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.battle_selector_item import SelectorItem
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import SpecialSquadItem
from helpers import dependency
from versus_ai.gui.versus_ai_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from versus_ai.skeletons.versus_ai_controller import IVersusAIController

def addVersusAIBattleType(items):
    items.append(_VersusAIItem(backport.text(R.strings.menu.headerButtons.battle.types.versusAI()), PREBATTLE_ACTION_NAME.VERSUS_AI, 3, SELECTOR_BATTLE_TYPES.VERSUS_AI))


def addVersusAISquadType(items):
    items.append(_VersusAISquadItem('', PREBATTLE_ACTION_NAME.VERSUS_AI_SQUAD, 3))


class _VersusAIItem(SelectorItem):
    __versusAIController = dependency.descriptor(IVersusAIController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_VersusAIItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isVisible = self.__versusAIController.isEnabled()

    def isRandomBattle(self):
        return True

    def getVO(self):
        vo = super(_VersusAIItem, self).getVO()
        return vo

    def _update(self, state):
        self._isVisible = self.__versusAIController.isEnabled()
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.VERSUS_AI)


class _VersusAISquadItem(SpecialSquadItem):
    __versusAIController = dependency.descriptor(IVersusAIController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_VersusAISquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._isVisible = self.__versusAIController.isEnabled()
        self._prebattleType = PREBATTLE_TYPE.VERSUS_AI

    @property
    def squadIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.versusAISquad())

    def getFormattedLabel(self):
        pass

    def _update(self, state):
        super(_VersusAISquadItem, self)._update(state)
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.VERSUS_AI)
        self._isVisible = self.__versusAIController.isEnabled() and state.isInPreQueue(queueType=QUEUE_TYPE.VERSUS_AI)
