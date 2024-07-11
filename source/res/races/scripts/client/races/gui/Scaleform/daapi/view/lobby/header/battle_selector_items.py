# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from races.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from races_common.races_constants import QUEUE_TYPE
from adisp import adisp_process
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IRacesBattleController

def addRacesBattlesType(items):
    items.append(_RacesBattlesItem(backport.text(R.strings.races.headerButtons.battle.types.races()), PREBATTLE_ACTION_NAME.RACES, 2, SELECTOR_BATTLE_TYPES.RACES))


class _RacesBattlesItem(_SelectorItem):
    __racesCtrl = dependency.descriptor(IRacesBattleController)
    __ACCEPTED_RESTRICTIONS = (PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE,)

    def getSmallIcon(self):
        return backport.image(R.images.gui.maps.icons.mode_selector.mode.races.icon_small())

    def getLargerIcon(self):
        return backport.image(R.images.gui.maps.icons.mode_selector.mode.races.icon_medium())

    def isRandomBattle(self):
        return True

    def _update(self, state):
        self._isDisabled = state.hasLockedState or self.__racesCtrl.isFrozen() or not self.__racesCtrl.isBattleAvailable()
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.RACES)
        self._isVisible = self.__racesCtrl.isEnabled

    def hasDisabledFightButtonData(self, result):
        if not self.__racesCtrl.isRacesMode():
            return False
        return True if not result.isValid and result.restriction in self.__ACCEPTED_RESTRICTIONS else False

    def getFightButtonLabel(self, state, playerInfo):
        return backport.text(R.strings.races.headerButtons.battle()) if self.__racesCtrl.isRacesMode() else super(_RacesBattlesItem, self).getFightButtonLabel(state, playerInfo)

    def getDisabledFightButtonLabel(self, result):
        if not self.__racesCtrl.isRacesMode():
            return ''
        return backport.text(R.strings.cosmicEvent.fightButton.vehicleInBattle()) if result.restriction == PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE else ''

    def getDisabledFightButtonTooltip(self, result):
        if not self.__racesCtrl.isRacesMode():
            return ''
        if result.restriction == PREBATTLE_RESTRICTION.VEHICLE_IN_BATTLE:
            header = backport.text(R.strings.races_tooltips.racesBattleButton.header())
            body = backport.text(R.strings.races_tooltips.racesBattleButton.body())
        else:
            return ''
        return makeTooltip(header, body)

    @adisp_process
    def _doSelect(self, dispatcher):
        isSuccess = yield dispatcher.doSelectAction(PrbAction(self.getData()))
        if isSuccess and self._isNew:
            selectorUtils.setBattleTypeAsKnown(self._selectorType)
