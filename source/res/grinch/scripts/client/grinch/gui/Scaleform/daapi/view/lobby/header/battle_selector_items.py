# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from grinch_common.grinch_constants import QUEUE_TYPE, PREBATTLE_TYPE
from grinch.gui.grinch_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from grinch.skeletons.battle_controller import IGrinchController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import ISeasonsController
from skeletons.gui.system_messages import ISystemMessages

def addGrinchBattleType(items):
    items.append(GrinchItem(backport.text(R.strings.mode_selector.mode.grinch.title()), PREBATTLE_ACTION_NAME.GRINCH, 2, SELECTOR_BATTLE_TYPES.GRINCH))


def addGrinchSquadType(items):
    items.append(GrinchSquadItem('Grinch battle squad', PREBATTLE_ACTION_NAME.GRINCH_SQUAD, 2))


class GrinchItem(battle_selector_items.SelectorItem):
    __grinchCtrl = dependency.descriptor(IGrinchController)
    __seasonsController = dependency.descriptor(ISeasonsController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def isShowActiveModeState(self):
        return self.__grinchCtrl.isAvailable()

    def getSmallIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.grinch())

    def getLargerIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_64x64.grinch())

    def isRandomBattle(self):
        return True

    @property
    def squadIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.grinch_squad())

    def isIgnoreSelectorNewbieRuleInMode(self):
        return True

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.GRINCH)

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.GRINCH)
        self._isVisible = self.__grinchCtrl.isEnabled()

    def _doSelect(self, dispatcher):
        pass


class GrinchSquadItem(battle_selector_items.SpecialSquadItem):
    __grinchCtrl = dependency.descriptor(IGrinchController)
    __seasonsController = dependency.descriptor(ISeasonsController)

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(GrinchSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.GRINCH
        self._isVisible = self.__grinchCtrl.isEnabled()
        self._isSpecialBgIcon = True
        self._isDescription = False

    def getSmallIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.grinch_squad())

    def isIgnoreSelectorNewbieRuleInMode(self):
        return True

    def _update(self, state):
        super(GrinchSquadItem, self)._update(state)
        self._isDisabled = state.hasLockedState or not self.__grinchCtrl.isAvailable()
        self._isSelected = state.isInUnit(self._prebattleType) or state.isQueueSelected(QUEUE_TYPE.GRINCH)
        self._isVisible = self.__grinchCtrl.isEnabled()
