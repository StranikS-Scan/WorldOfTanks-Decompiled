# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/common_balance_content.py
import logging
from itertools import chain
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen.view_models.views.common_balance_content_model import CommonBalanceContentModel
from shared_utils import CONST_CONTAINER
from frameworks.wulf import NumberFormatType, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.value_price import ValuePrice
from gui.impl.lobby.dialogs.model_managers.balance_model_manager import BalanceModelManager
from gui.impl.pub.view_impl import ViewImpl
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IWalletController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class CurrencyStatus(CONST_CONTAINER):
    IN_PROGRESS = 0
    NOT_AVAILABLE = 1
    AVAILABLE = 2


class CommonBalanceContent(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __slots__ = ('__modelManager',)
    __CURRENCY_FORMATTER = {Currency.CREDITS: NumberFormatType.INTEGRAL,
     Currency.GOLD: NumberFormatType.GOLD,
     Currency.CRYSTAL: NumberFormatType.INTEGRAL,
     'freeXP': NumberFormatType.INTEGRAL}
    __SPECIAL_TOOLTIPS = {Currency.GOLD: TOOLTIPS_CONSTANTS.GOLD_STATS,
     Currency.CREDITS: TOOLTIPS_CONSTANTS.CREDITS_STATS}

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.common.dialog_view.components.balance_contents.CommonBalanceContent())
        settings.model = model = CommonBalanceContentModel()
        settings.args = args
        settings.kwargs = kwargs
        super(CommonBalanceContent, self).__init__(settings, *args, **kwargs)
        self.__modelManager = BalanceModelManager(model)

    @property
    def viewModel(self):
        return self.__modelManager.viewModel

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            if tooltipId in self.__SPECIAL_TOOLTIPS.values():
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId)
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return

    def _initialize(self, *args, **kwargs):
        super(CommonBalanceContent, self)._initialize()
        self.__modelManager.start(kwargs.get('currencies', chain(Currency.GUI_ALL, (ValuePrice.FREE_XP,))))

    def _finalize(self):
        super(CommonBalanceContent, self)._finalize()
        self.__modelManager.stop()
