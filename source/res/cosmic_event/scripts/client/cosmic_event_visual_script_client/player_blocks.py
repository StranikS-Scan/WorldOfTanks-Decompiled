# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event_visual_script_client/player_blocks.py
import typing
from visual_script.block import Block
from visual_script.misc import ASPECT
from visual_script.slot_types import SLOT_TYPE
from visual_script_client.player_blocks import PlayerEventMeta
if typing.TYPE_CHECKING:
    from skeletons.gui.battle_session import IBattleSessionProvider

class CosmicPlayerMeta(PlayerEventMeta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class SetScanningVehicles(Block, CosmicPlayerMeta):

    def __init__(self, *args, **kwargs):
        super(SetScanningVehicles, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._amount = self._makeDataInputSlot('amount', SLOT_TYPE.INT)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self, *args, **kwargs):
        sessionProvider = self._avatar.guiSessionProvider
        sessionProvider.dynamic.battleHints.setScanningVehicles(self._amount.getValue())
        self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
