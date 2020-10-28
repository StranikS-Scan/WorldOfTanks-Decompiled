# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dog_tags_common/components_packer.py
import typing
if typing.TYPE_CHECKING:
    from typing import Tuple
_MASK_ID = 4294967295L
_MASK_GRADE = 1099511627775L - _MASK_ID
_MASK_TEAM = 281474976710655L - _MASK_GRADE - _MASK_ID

def pack_component(compId, grade, team=0):
    p_grade = grade << 32 & _MASK_GRADE
    p_team = team << 40 & _MASK_TEAM
    p_id = compId & _MASK_ID
    return p_grade | p_team | p_id


def unpack_component(packed):
    team = int((packed & _MASK_TEAM) >> 40)
    grade = int((packed & _MASK_GRADE) >> 32)
    compId = int(packed & _MASK_ID)
    return (compId, grade, team)
