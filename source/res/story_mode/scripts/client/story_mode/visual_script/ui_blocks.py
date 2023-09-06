# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/visual_script/ui_blocks.py
from visual_script.block import Block
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
from visual_script_client.battle_hud_block import BattleHUDEventMeta
observers = dependencyImporter('story_mode.gui.app_loader.observers')

class ShowWinMessage(Block, BattleHUDEventMeta):

    def __init__(self, *args, **kwargs):
        super(ShowWinMessage, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._teamSlot = self._makeDataInputSlot('team', SLOT_TYPE.INT)
        self._reasonSlot = self._makeDataInputSlot('reason', SLOT_TYPE.E_FINISH_REASON)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        battlePage = observers.getStoryModeBattle()
        if battlePage is not None:
            battlePage.showWinMessage(self._teamSlot.getValue(), self._reasonSlot.getValue())
        self._out.call()
        return
