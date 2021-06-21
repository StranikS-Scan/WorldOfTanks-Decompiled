# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/tooltips/mapbox_calendar_tooltip.py
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.lobby.formatters.tooltips import packTimeTableHeaderBlock, packCalendarBlock
from gui.shared.tooltips import formatters, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IMapboxController
from gui.shared.formatters import text_styles
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES

class MapboxCalendarTooltip(BlocksTooltipData):
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self, context):
        super(MapboxCalendarTooltip, self).__init__(context, TOOLTIP_TYPE.MAPBOX_SELECTOR_INFO)
        self._setWidth(360)

    def _packBlocks(self, *args, **kwargs):
        blocks = super(MapboxCalendarTooltip, self)._packBlocks(args, kwargs)
        blocks.append(formatters.packBuildUpBlockData([self.__packHeader(), packTimeTableHeaderBlock(SELECTOR_BATTLE_TYPES.MAPBOX), formatters.packBuildUpBlockData(packCalendarBlock(self.__mapboxCtrl, time_utils.getCurrentTimestamp(), SELECTOR_BATTLE_TYPES.MAPBOX))]))
        return blocks

    def __packHeader(self):
        return formatters.packTextBlockData(text_styles.highlightText(backport.text(R.strings.mapbox.selector.tooltip.body(), day=self.__getCurrentSeasonDate())), padding=formatters.packPadding(bottom=10))

    def __getCurrentSeasonDate(self):
        currentSeason = self.__mapboxCtrl.getCurrentSeason()
        return self.__getDate(currentSeason.getEndDate()) if currentSeason is not None else ''

    def __getDate(self, date):
        timeStamp = time_utils.makeLocalServerTime(date)
        return backport.getShortDateFormat(timeStamp)
