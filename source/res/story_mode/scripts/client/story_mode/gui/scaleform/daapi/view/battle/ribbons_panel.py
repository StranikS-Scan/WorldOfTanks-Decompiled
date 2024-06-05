# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/ribbons_panel.py
from gui.Scaleform.daapi.view.battle.pve_base.ribbons_panel import PveRibbonsPanel
from story_mode.gui.scaleform.daapi.view.battle import ribbons_aggregator

class StoryModeRibbonsPanel(PveRibbonsPanel):

    def __init__(self):
        super(StoryModeRibbonsPanel, self).__init__(ribbonsAggregator=ribbons_aggregator.createRibbonsAggregator())
