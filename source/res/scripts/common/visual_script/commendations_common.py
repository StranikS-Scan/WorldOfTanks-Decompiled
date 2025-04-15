# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/commendations_common.py
import typing
from live_tags_constants import LIVE_TAG_TYPES
from visual_script.type import VScriptEnum

class LiveTagTypes(VScriptEnum):

    @classmethod
    def vs_name(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return LIVE_TAG_TYPES
