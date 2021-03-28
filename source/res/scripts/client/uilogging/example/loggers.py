# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/example/loggers.py
import typing
from uilogging.base.logger import BaseLogger, ifUILoggingEnabled
from uilogging.base.mixins import LogOnceMixin, TimedActionMixin
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from uilogging.example.views import BuyProductView

class ExampleLogger(TimedActionMixin, LogOnceMixin, BaseLogger):

    def __init__(self, group):
        super(ExampleLogger, self).__init__('example', group)

    @noexcept
    @ifUILoggingEnabled()
    def highlightProduct(self, view, product):
        highlighted = [ p.name for p in view.products.values() if p.highlighted ]
        self.info('highlight', product=product, highlighted=highlighted)


class ExampleTooltipLogger(ExampleLogger):

    def __init__(self):
        super(ExampleTooltipLogger, self).__init__('tooltip_view')
        self._openedTooltip = None
        return

    @noexcept
    @ifUILoggingEnabled()
    def tooltipOpened(self, tooltip):
        self._openedTooltip = tooltip
        self.startAction('tooltip_opened')

    @noexcept
    @ifUILoggingEnabled()
    def tooltipClosed(self, tooltip, timeLimit):
        if self._openedTooltip and self._openedTooltip == tooltip:
            self._openedTooltip = None
            self.stopAction('tooltip_opened', tooltip=tooltip, timeLimit=timeLimit)
        return
