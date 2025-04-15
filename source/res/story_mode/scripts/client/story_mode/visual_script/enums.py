# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/visual_script/enums.py
import typing
from visual_script.type import VScriptEnum
from visual_script import ASPECT
from story_mode_common.story_mode_constants import AwarenessState

class SMAwarenessStateEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return AwarenessState

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT]
