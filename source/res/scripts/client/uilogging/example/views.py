# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/example/views.py
from uilogging.base.logger import BaseLogger
from uilogging.core.core_constants import LogLevels
from uilogging.example.loggers import ExampleLogger, ExampleTooltipLogger
uiBuyLogger = BaseLogger('example', 'buy_product')

class Product(object):

    def __init__(self, name, count, highlighted):
        self.name = name
        self.count = count
        self.highlighted = highlighted


class BuyProduct(object):

    def __init__(self):
        self.cost = 0
        self.currency = 0
        self.products = {'car': Product('car', 1, False),
         'bear': Product('bear', 20, True)}

    @uiBuyLogger.dLog('buy_clicked', loglevel=LogLevels.DEBUG, test='test')
    def buy(self, name, count):
        costs = self.cost * count
        if name in self.products and costs and self.currency >= costs:
            self.currency -= costs
            self.products[name].count += count
            uiBuyLogger.info('bought', costs=costs, product=name)


class BuyProductView(BuyProduct):
    uiLogger = ExampleLogger('buy_view')

    def __init__(self):
        super(BuyProductView, self).__init__()
        self._ribbons = []

    @uiLogger.dLogOnce('opened', loglevel=LogLevels.DEBUG, test='test')
    @uiLogger.dStartAction('closed')
    def populate(self):
        self.cost = 500
        self.currency = 1000

    @uiLogger.dStopAction('closed', timeLimit=2, param='test')
    def dispose(self):
        self.cost = 0
        self.currency = 0
        self.uiLogger.reset()

    def highlight(self, name):
        product = self.products.get(name)
        if product and not product.highlighted:
            self.uiLogger.highlightProduct(self, product=name)
            product.highlighted = True


class BuyWithTooltips(BuyProductView):
    uiLogger = ExampleTooltipLogger()

    def showTooltip(self, tooltip):
        self.uiLogger.tooltipOpened(tooltip)

    def hideTooltip(self, tooltip):
        self.uiLogger.tooltipClosed(tooltip, timeLimit=2.0)
