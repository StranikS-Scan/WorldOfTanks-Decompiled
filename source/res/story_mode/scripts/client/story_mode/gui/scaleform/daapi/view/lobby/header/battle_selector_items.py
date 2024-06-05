# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/lobby/header/battle_selector_items.py
from __future__ import absolute_import
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from story_mode.gui.story_mode_gui_constants import PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from story_mode.skeletons.story_mode_controller import IStoryModeController
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency

def addStoryModeType(items):
    items.append(_StoryModeItem(backport.text(R.strings.sm_lobby.headerButtons.battle.types.story_mode()), PREBATTLE_ACTION_NAME.STORY_MODE, 2, SELECTOR_BATTLE_TYPES.STORY_MODE))


class _StoryModeItem(battle_selector_items.SelectorItem):
    storyModeCtrl = dependency.descriptor(IStoryModeController)

    def select(self):
        super(_StoryModeItem, self).select()
        selectorUtils.setBattleTypeAsKnown(self._selectorType)

    def isRandomBattle(self):
        return True

    def setLocked(self, value):
        self._isLocked = value
        if self._isLocked:
            self._isDisabled = True
            self._isSelected = False

    def getSmallIcon(self):
        return backport.image(R.images.story_mode.gui.maps.icons.battleTypes.c_40x40.story_mode())

    def getLargerIcon(self):
        return backport.image(R.images.story_mode.gui.maps.icons.battleTypes.c_64x64.story_mode())

    def isInSquad(self, state):
        return state.isInUnit(PREBATTLE_TYPE.STORY_MODE)

    def isShowActiveModeState(self):
        return self.storyModeCtrl.isShowActiveModeState()

    def _update(self, state):
        self._isSelected = state.isQueueSelected(QUEUE_TYPE.STORY_MODE)
        self._isDisabled = state.hasLockedState or not self.storyModeCtrl.isEnabled() and not self._isSelected
