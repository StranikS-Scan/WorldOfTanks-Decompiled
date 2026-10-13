# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
import logging
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from fort_rush_common.fort_rush_constants import QUEUE_TYPE, PREBATTLE_TYPE
from fort_rush.gui.fort_rush_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.system_messages import ISystemMessages
_logger = logging.getLogger(__name__)
_HIGHLIGHT_LOBBY_VIOLET_LINKAGE = 'BgAnimVioletUI'
_HIGHLIGHT_FIGHT_VIOLET_LINKAGE = 'BGFightHighlightUI'

def addFortRushBattlesType(items):
    items.append(_FortRushBattlesItem(backport.text(R.strings.menu.headerButtons.battle.types.fortRush()), PREBATTLE_ACTION_NAME.FORT_RUSH, 2, SELECTOR_BATTLE_TYPES.FORT_RUSH))


def addFortRushSquadType(items):
    items.append(FortRushSquadItem(backport.text(R.strings.menu.headerButtons.battle.types.fortRushSquad()), PREBATTLE_ACTION_NAME.FORT_RUSH_SQUAD, 2))


class _FortRushBattlesItem(battle_selector_items.SelectorItem):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def isRandomBattle(self):
        return True

    def isShowEventIndication(self):
        ctrl = dependency.instance(IFortRushBattleController)
        return ctrl is not None and ctrl.isAvailable()

    def hasSparksAnimation(self, isNewbie, hasEventIndication):
        return hasEventIndication

    def getSmallIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.dyn('fort_rush_battle')())

    def getLargerIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_64x64.dyn('fort_rush_battle')())

    def getHighlightLinkage(self, isNewbie, defaultLinkage=''):
        return _HIGHLIGHT_LOBBY_VIOLET_LINKAGE

    def getFightButtonHighlight(self, isNewbie):
        return _HIGHLIGHT_FIGHT_VIOLET_LINKAGE

    def _update(self, state):
        ctrl = dependency.instance(IFortRushBattleController)
        isEnabled = ctrl is not None and ctrl.isEnabled()
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.FORT_RUSH)
        self._isDisabled = state.hasLockedState or not isEnabled
        self._isVisible = isEnabled
        _logger.info('[FORT_RUSH] Battle selector visible: %s, disabled: %s, selected: %s', self._isVisible, self._isDisabled, self._isSelected)
        return


class FortRushSquadItem(battle_selector_items.SpecialSquadItem):

    def __init__(self, label, data, order, selectorType=None, isVisible=True):
        super(FortRushSquadItem, self).__init__(label, data, order, selectorType, isVisible)
        self._prebattleType = PREBATTLE_TYPE.FORT_RUSH
        ctrl = dependency.instance(IFortRushBattleController)
        self._isVisible = ctrl is not None and ctrl.isEnabled()
        self._isSpecialBgIcon = True
        self._isDescription = False
        return

    def isShowEventIndication(self):
        ctrl = dependency.instance(IFortRushBattleController)
        return ctrl is not None and ctrl.isAvailable()

    def getHighlightLinkage(self, isNewbie, defaultLinkage=''):
        return _HIGHLIGHT_LOBBY_VIOLET_LINKAGE

    def getSmallIcon(self):
        return backport.image(R.images.gui.maps.icons.battleTypes.c_40x40.dyn('fort_rush_squad')())

    def _update(self, state):
        super(FortRushSquadItem, self)._update(state)
        ctrl = dependency.instance(IFortRushBattleController)
        if ctrl is not None:
            self._isSelected = ctrl.isEventPrbActive()
            self._isDisabled = state.hasLockedState or not ctrl.isEnabled()
            self._isVisible = ctrl.isEnabled()
        else:
            self._isSelected = False
            self._isDisabled = True
            self._isVisible = False
        return
