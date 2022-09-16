# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/scene_blocks.py
import BigWorld
from visual_script import ASPECT
from visual_script.block import Block
from visual_script.slot_types import SLOT_TYPE
from visual_script.arena_blocks import ArenaMeta
from material_kinds import EFFECT_MATERIAL_NAMES_BY_INDEXES, EFFECT_MATERIAL_INDEXES_BY_IDS

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
        return [ASPECT.CLIENT, ASPECT.HANGAR]


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
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class GetTerrainMaterialUnderPoint(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(GetTerrainMaterialUnderPoint, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._spaceID = self._makeDataInputSlot('spaceID', SLOT_TYPE.INT)
        self._position = self._makeDataInputSlot('position', SLOT_TYPE.VECTOR3)
        self._dropDistance = self._makeDataInputSlot('dropDistance', SLOT_TYPE.FLOAT)
        self._out = self._makeEventOutputSlot('out')
        self._material = self._makeDataOutputSlot('material', SLOT_TYPE.STR, None)
        return

    def _execute(self):
        material = BigWorld.wg_getMathInfoUnderPoint(self._spaceID.getValue(), self._position.getValue(), self._dropDistance.getValue())
        index = EFFECT_MATERIAL_INDEXES_BY_IDS.get(material)
        name = EFFECT_MATERIAL_NAMES_BY_INDEXES.get(index)
        if name is None:
            name = 'undefined'
        self._material.setValue(name)
        self._out.call()
        return


class TerrainIndexToName(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(TerrainIndexToName, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._index = self._makeDataInputSlot('index', SLOT_TYPE.INT)
        self._out = self._makeEventOutputSlot('out')
        self._material = self._makeDataOutputSlot('material', SLOT_TYPE.STR, None)
        return

    def _execute(self):
        index = EFFECT_MATERIAL_INDEXES_BY_IDS.get(self._index.getValue())
        name = EFFECT_MATERIAL_NAMES_BY_INDEXES.get(index)
        if name is None:
            name = 'undefined'
        self._material.setValue(name)
        self._out.call()
        return
