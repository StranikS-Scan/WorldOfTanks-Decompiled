# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/ability_common.py
from visual_script.type import VScriptEnum
from visual_script.misc import ASPECT
from constants import EQUIPMENT_STAGES as STAGES

class Stage(VScriptEnum):

    @classmethod
    def vs_enum(cls):
        return STAGES

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.ALL]
