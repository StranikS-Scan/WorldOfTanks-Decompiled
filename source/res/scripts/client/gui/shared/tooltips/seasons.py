# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/seasons.py
from gui.shared.tooltips import ToolTipDataField, ToolTipData, TOOLTIP_TYPE

class SeasonsImageField(ToolTipDataField):

    def _getValue(self):
        return self._tooltip.item['seasonImage']


class SeasonsHeaderField(ToolTipDataField):

    def _getValue(self):
        return self._tooltip.item['header']


class SeasonsBodyField(ToolTipDataField):

    def _getValue(self):
        return self._tooltip.item['body']


class SeasonsTooltipData(ToolTipData):

    def __init__(self, context):
        super(SeasonsTooltipData, self).__init__(context, TOOLTIP_TYPE.SEASONS)
        self.fields = (SeasonsImageField(self, 'seasonImage'), SeasonsHeaderField(self, 'header'), SeasonsBodyField(self, 'body'))
