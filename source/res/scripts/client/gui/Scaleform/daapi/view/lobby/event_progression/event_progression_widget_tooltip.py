# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_progression/event_progression_widget_tooltip.py
from collections import namedtuple
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.daapi.view.lobby.event_progression.event_progression_helpers import EventProgressionTooltipHelpers
EpicBattlesWidgetTooltipVO = namedtuple('EpicBattlesWidgetTooltipVO', 'progressBarData')

class EventProgressionWidgetTooltip(BlocksTooltipData):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ()

    def __init__(self, context):
        super(EventProgressionWidgetTooltip, self).__init__(context, TOOLTIP_TYPE.EVENT_PROGRESSION_PROGRESS_INFO)
        self._setContentMargin(top=0, left=0, bottom=12, right=0)
        self._setWidth(width=320)

    def _packBlocks(self):
        blocks = super(EventProgressionWidgetTooltip, self)._packBlocks()
        season = self.__epicController.getCurrentSeason() or self.__epicController.getNextSeason()
        if season is None:
            return blocks
        else:
            _evc = EventProgressionTooltipHelpers.getInstance()
            blocks.append(_evc.getHeaderTooltipPack())
            isPrimeTime = _evc.isCurrentSeasonInPrimeTime()
            if isPrimeTime or self.__epicController.isAvailable():
                blocks.append(_evc.getCycleStatusPack())
            else:
                blocks.append(_evc.getSeasonInfoPack())
            _evc = None
            return blocks
