# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/fullmap.py
from gui.Scaleform.daapi.view.battle.pve_base.fullmap import PveFullMapComponent
from story_mode.gui.scaleform.daapi.view.battle.minimap import BunkersPlugin, adjustBoundingBox

class StoryModeFullMapComponent(PveFullMapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(StoryModeFullMapComponent, self)._setupPlugins(arenaVisitor)
        setup['bunkers'] = BunkersPlugin
        return setup

    def getBoundingBox(self):
        arenaVisitor = self.sessionProvider.arenaVisitor
        return adjustBoundingBox(*arenaVisitor.type.getBoundingBox())
