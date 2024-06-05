# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/area_marker_ctrl.py
from chat_commands_consts import INVALID_TARGET_ID
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers import AreaMarker
from gui.battle_control.controllers.area_marker_ctrl import AreaMarkersController
from story_mode.gui.shared.component_marker.markers import StoryModeAreaMarker

class StoryModeAreaMarkersController(AreaMarkersController):

    def createMarker(self, matrix, markerType, targetID=INVALID_TARGET_ID, entity=None, clazz=AreaMarker, visible=None, bitMask=0):
        return super(StoryModeAreaMarkersController, self).createMarker(matrix, markerType, targetID, entity, StoryModeAreaMarker, visible, bitMask)
