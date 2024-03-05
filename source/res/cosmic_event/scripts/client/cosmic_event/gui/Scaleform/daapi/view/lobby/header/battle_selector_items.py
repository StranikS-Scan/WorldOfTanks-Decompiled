# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from cosmic_event.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_event_common.cosmic_constants import QUEUE_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem
from helpers import dependency
from gui.shared.utils.functions import makeTooltip
from gui.prb_control.settings import PREBATTLE_RESTRICTION

def addCosmicEventBattlesType(items):
    items.append(_CosmicEventBattlesItem(backport.text(R.strings.cosmicEvent.headerButtons.battle.types.cosmicEvent()), PREBATTLE_ACTION_NAME.COSMIC_EVENT, 2, SELECTOR_BATTLE_TYPES.COSMIC_EVENT))


class _CosmicEventBattlesItem(_SelectorItem):
    __cosmicEventBattleCtrl = dependency.descriptor(ICosmicEventBattleController)
    __ACCEPTED_RESTRICTIONS = (PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE,)

    def getSmallIcon(self):
        return backport.image(R.images.cosmic_event.gui.maps.icons.battleTypes.c_40x40.cosmicEvent())

    def getLargerIcon(self):
        return backport.image(R.images.cosmic_event.gui.maps.icons.battleTypes.c_64x64.cosmicEvent())

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isDisabled = state.hasLockedState
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.COSMIC_EVENT)
        self._isVisible = self.__cosmicEventBattleCtrl.isEnabled

    def hasDisabledFightButtonData(self, result):
        if not self.__cosmicEventBattleCtrl.isCosmicMode():
            return False
        return True if not result.isValid and result.restriction in self.__ACCEPTED_RESTRICTIONS else False

    def getDisabledFightButtonLabel(self, result):
        if not self.__cosmicEventBattleCtrl.isCosmicMode():
            return ''
        return backport.text(R.strings.cosmicEvent.fightButton.vehicleInBattle()) if result.restriction == PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE else ''

    def getDisabledFightButtonTooltip(self, result):
        if not self.__cosmicEventBattleCtrl.isCosmicMode():
            return ''
        if result.restriction == PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE:
            header = backport.text(R.strings.cosmicEvent.fightButton.tooltip.vehicleInBattle.header())
            body = backport.text(R.strings.cosmicEvent.fightButton.tooltip.vehicleInBattle.body())
        else:
            return ''
        return makeTooltip(header, body)
