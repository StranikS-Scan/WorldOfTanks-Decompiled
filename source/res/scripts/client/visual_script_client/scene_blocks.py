# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/scene_blocks.py
import BigWorld
from visual_script import ASPECT
from visual_script.block import Block
from visual_script.block import SLOT_TYPE

class GetSpaceId(Block):

    @classmethod
    def blockCategory(cls):
        pass

    def __init__(self, *args, **kwargs):
        super(GetSpaceId, self).__init__(*args, **kwargs)
        self._spaceId = self._makeDataOutputSlot('spaceId', SLOT_TYPE.INT, GetSpaceId._execute)

    def _execute(self):
        from Avatar import PlayerAvatar
        player = BigWorld.player()
        spaceID = player.spaceID if isinstance(player, PlayerAvatar) else player.hangarSpace.spaceID
        self._spaceId.setValue(spaceID)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
