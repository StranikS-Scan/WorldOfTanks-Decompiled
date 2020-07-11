# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/event_progression_widget_tooltip.py
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import IEventProgressionController

class EventProgressionWidgetTooltip(BlocksTooltipData):
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __slots__ = ()

    def __init__(self, context):
        super(EventProgressionWidgetTooltip, self).__init__(context, TOOLTIP_TYPE.EVENT_PROGRESSION_PROGRESS_INFO)
        self._setContentMargin(top=0, left=0, bottom=12, right=0)
        self._setWidth(width=320)

    def _packBlocks(self):
        blocks = super(EventProgressionWidgetTooltip, self)._packBlocks()
        season = self.__eventProgression.getCurrentSeason() or self.__eventProgression.getNextSeason()
        if season is None:
            return blocks
        else:
            blocks.append(self.__eventProgression.getHeaderTooltipPack())
            isPrimeTime = self.__eventProgression.isCurrentSeasonInPrimeTime()
            if isPrimeTime or self.__eventProgression.modeIsAvailable():
                blocks.append(self.__eventProgression.getCycleStatusTooltipPack())
            else:
                blocks.append(self.__eventProgression.getSeasonInfoTooltipPack())
            return blocks
