# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/shared/component_marker/markers.py
import copy
from chat_commands_consts import INVALID_TARGET_ID
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers import AreaMarker
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import ComponentBitMask as FLAG
BITMASK = 'bitMask'
CLASS = 'clazz'

class StoryModeAreaMarker(AreaMarker):
    fullScreenVariations = {}

    def __init__(self, config, entity=None, targetID=INVALID_TARGET_ID):
        if FLAG.FULLSCREEN_MAP_MARKER not in config and FLAG.MINIMAP_MARKER in config:
            config[FLAG.FULLSCREEN_MAP_MARKER] = newConfig = copy.deepcopy(config[FLAG.MINIMAP_MARKER])
            for componentConfig in newConfig:
                oldClazz = componentConfig[CLASS]
                newClassName = oldClazz.__name__ + 'FullScreenVariation'
                if newClassName in StoryModeAreaMarker.fullScreenVariations:
                    componentConfig[CLASS] = StoryModeAreaMarker.fullScreenVariations.get(newClassName)
                newClass = type(newClassName, (oldClazz,), {'maskType': FLAG.FULLSCREEN_MAP_MARKER})
                componentConfig[CLASS] = StoryModeAreaMarker.fullScreenVariations[newClassName] = newClass

            if BITMASK in config:
                config[BITMASK] = config[BITMASK] | FLAG.FULLSCREEN_MAP_MARKER
        super(StoryModeAreaMarker, self).__init__(config, entity, targetID)
