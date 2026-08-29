# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from helpers import dependency
from white_tiger.gui.white_tiger_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger_common.wt_constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import SelectorItem

def addWhiteTigerType(items):
    items.append(_WhiteTigerItem(backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger()), PREBATTLE_ACTION_NAME.WHITE_TIGER, 2, SELECTOR_BATTLE_TYPES.WHITE_TIGER))


def addWhiteTigerSquadType(items):
    items.append(_WhiteTigerSquadItem('White Tiger Squad Battle', PREBATTLE_ACTION_NAME.WHITE_TIGER, 2))


class _WhiteTigerItem(SelectorItem):
    _wtController = dependency.descriptor(IWhiteTigerController)

    def isShowEventIndication(self):
        return self._wtController.isAvailable()

    def hasSparksAnimation(self, isNewbie, hasEventIndication):
        return hasEventIndication

    def getSmallIcon(self):
        return backport.image(R.images.white_tiger.gui.maps.icons.battleTypes.c_40x40.white_tiger())

    def getLargerIcon(self):
        return backport.image(R.images.white_tiger.gui.maps.icons.battleTypes.c_64x64.white_tiger())

    def isRandomBattle(self):
        return True

    @property
    def squadIcon(self):
        return backport.image(R.images.white_tiger.gui.maps.icons.battleTypes.c_40x40.white_tiger_squad())

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.WHITE_TIGER)
        self._isVisible = self._wtController.isAvailable()


class _WhiteTigerSquadItem(battle_selector_items.SpecialSquadItem):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(_WhiteTigerSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.WHITE_TIGER
        self._isVisible = self.__wtCtrl.isEnabled()
        self._isSpecialBgIcon = True
        self._isDescription = False

    def getSmallIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.event())

    def isIgnoreSelectorNewbieRuleInMode(self):
        return True

    def _update(self, state):
        super(_WhiteTigerSquadItem, self)._update(state)
        self._isDisabled = state.hasLockedState or not self.__wtCtrl.isAvailable()
        self._isSelected = state.isInUnit(self._prebattleType) or state.isQueueSelected(QUEUE_TYPE.WHITE_TIGER)
        self._isVisible = self.__wtCtrl.isEnabled()
