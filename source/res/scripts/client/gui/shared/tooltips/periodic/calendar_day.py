# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/periodic/calendar_day.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import time_utils
from items.writers.c11n_writers import natsorted
_CONTENT_MARGINS = {'top': 18,
 'bottom': 18,
 'left': 20,
 'right': 20}
_TOOLTIP_MARGIN = 13
_TOOLTIP_MIN_WIDTH = 200

class PeriodicCalendarDayTooltip(BlocksTooltipData):
    _RES_ROOT = None
    _TOOLTIP_TYPE = None

    def __init__(self, ctx):
        super(PeriodicCalendarDayTooltip, self).__init__(ctx, self._TOOLTIP_TYPE)
        self._setMargins(_TOOLTIP_MARGIN)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        self._setContentMargin(**_CONTENT_MARGINS)

    def _getController(self, *_):
        raise NotImplementedError

    def _isValidPrimeTimes(self, _):
        return True

    def _packBlocks(self, *args):
        controller = self._getController(*args)
        items = super(PeriodicCalendarDayTooltip, self)._packBlocks()
        if controller is None or not controller.isAvailable():
            return items
        else:
            now = time_utils.getCurrentLocalServerTimestamp()
            serversPeriodsMapping = controller.getPrimeTimesForDay(now)
            if not self._isValidPrimeTimes(serversPeriodsMapping):
                return items
            blocks = [self._packHeaderBlock()]
            timeFmt = backport.getShortTimeFormat
            for serverName in natsorted(serversPeriodsMapping.keys()):
                dayPeriods = serversPeriodsMapping[serverName]
                if dayPeriods:
                    periodsStr = [ backport.text(self._RES_ROOT.time(), start=timeFmt(periodStart), end=timeFmt(periodEnd)) for periodStart, periodEnd in dayPeriods ]
                else:
                    periodsStr = backport.text(R.strings.common.common.dash())
                blocks.append(self.__packServerTimeBlock(serverStr=text_styles.main(backport.text(self._RES_ROOT.serverName(), server=serverName)), timeStr=text_styles.stats('\n'.join(periodsStr))))

            items.append(formatters.packBuildUpBlockData(blocks, _TOOLTIP_MARGIN))
            return items

    def _packHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(self._RES_ROOT.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=10))

    def __packServerTimeBlock(self, serverStr, timeStr):
        return formatters.packTextParameterBlockData(value=serverStr, name=timeStr, valueWidth=55, padding=formatters.packPadding(left=10))
