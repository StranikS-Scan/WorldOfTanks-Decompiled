# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/scene_blocks.py
import BigWorld
from visual_script import ASPECT
from visual_script.block import Block
from visual_script.slot_types import SLOT_TYPE
from visual_script.arena_blocks import ArenaMeta

class GetSpaceId(Block, ArenaMeta):

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


class GetSpaceName(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(GetSpaceName, self).__init__(*args, **kwargs)
        self._spaceName = self._makeDataOutputSlot('spaceName', SLOT_TYPE.STR, self._execute)

    def _execute(self):
        from Avatar import PlayerAvatar
        player = BigWorld.player()
        if isinstance(player, PlayerAvatar):
            spaceName = player.arena.arenaType.geometryName
        else:
            spaceName = player.hangarSpace.spacePath.split('/')[-1]
        self._spaceName.setValue(spaceName)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
