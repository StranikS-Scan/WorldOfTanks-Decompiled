# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/seasons.py
from gui.shared.tooltips import ToolTipDataField, ToolTipData, TOOLTIP_TYPE

class SeasonsImageField(ToolTipDataField):
    """
    This class provides the season data for the SeasonToolTip
    """

    def _getValue(self):
        return self._tooltip.item['seasonImage']


class SeasonsHeaderField(ToolTipDataField):
    """
    This class provides the header data for the SeasonToolTip
    """

    def _getValue(self):
        return self._tooltip.item['header']


class SeasonsBodyField(ToolTipDataField):
    """
    This class provides the body data for the SeasonToolTip
    """

    def _getValue(self):
        return self._tooltip.item['body']


class SeasonsTooltipData(ToolTipData):
    """
    A class that will initialize the data for SeasonsTooltipData
    """

    def __init__(self, context):
        """
        Sets up fields for SeasonsTooltipData
        
        :param context:
        """
        super(SeasonsTooltipData, self).__init__(context, TOOLTIP_TYPE.SEASONS)
        self.fields = (SeasonsImageField(self, 'seasonImage'), SeasonsHeaderField(self, 'header'), SeasonsBodyField(self, 'body'))
