# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/directive_conversion_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.directive_conversion_tooltip_model import DirectiveConversionTooltipModel
from gui.impl.lobby.crew.utils import BOOSTER_ICON_MAPPING
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class DirectiveConversionTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__oldDirective', '__newDirective', '__amount')

    def __init__(self, **kwargs):
        settings = ViewSettings(R.views.lobby.crew.tooltips.DirectiveConversionTooltip())
        settings.model = DirectiveConversionTooltipModel()
        self.__oldDirective = self._itemsCache.items.getItemByCD(kwargs.get('oldDirectiveID'))
        self.__newDirective = self._itemsCache.items.getItemByCD(kwargs.get('newDirectiveID'))
        self.__amount = kwargs.get('amount')
        super(DirectiveConversionTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DirectiveConversionTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DirectiveConversionTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.oldDirective.setIcon(BOOSTER_ICON_MAPPING.get(self.__oldDirective.name, self.__oldDirective.name))
            vm.oldDirective.setUserName(self.__oldDirective.userName)
            vm.newDirective.setIcon(BOOSTER_ICON_MAPPING.get(self.__newDirective.name, self.__newDirective.name))
            vm.newDirective.setUserName(self.__newDirective.userName)
            vm.setAmount(self.__amount)
