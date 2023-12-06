# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/album/album_buy_dialog_base.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.gf_builders import BaseDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.dialogs.dialog_template_button_view_model import ButtonType
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.shards_balance_model import ShardsBalanceModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.collection_price_model import CollectionPriceModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from new_year.ny_constants import SyncDataKeys
if typing.TYPE_CHECKING:
    from gui.impl.dialogs.dialog_template import DialogTemplateView

class ShardsBalance(ViewImpl):
    __slots__ = ()
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.ShardsBalance())
        settings.flags = ViewFlags.VIEW
        settings.model = ShardsBalanceModel()
        super(ShardsBalance, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ShardsBalance, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ShardsBalance, self)._initialize()
        self._nyController.onDataUpdated += self.__onUpdated
        self._setBalance()

    def _finalize(self):
        self._nyController.onDataUpdated -= self.__onUpdated
        super(ShardsBalance, self)._finalize()

    def _setBalance(self):
        with self.viewModel.transaction() as model:
            model.setBalance(self._itemsCache.items.festivity.getShardsCount())

    def __onUpdated(self, keys):
        if SyncDataKeys.TOY_FRAGMENTS in keys:
            self._setBalance()


class Price(ViewImpl):
    __slots__ = ('__price',)

    def __init__(self, price):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.CollectionPrice())
        settings.flags = ViewFlags.VIEW
        settings.model = CollectionPriceModel()
        self.__price = price
        super(Price, self).__init__(settings)

    @property
    def viewModel(self):
        return super(Price, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(Price, self)._initialize()
        with self.viewModel.transaction() as model:
            model.setPrice(self.__price)


class AlbumBuyDialogBase(BaseDialogBuilder):
    __slots__ = ()

    def _extendTemplate(self, template):
        super(AlbumBuyDialogBase, self)._extendTemplate(template)
        template.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, ShardsBalance())
        self._setTitle(template)
        self._setPrice(template)
        template.addButton(ConfirmButton(R.strings.ny.dialogs.buyCollectionItem.btnBuy(), DialogButtons.SUBMIT, ButtonType.MAIN))
        template.addButton(CancelButton())

    def _setTitle(self, template):
        pass

    def _setPrice(self, template, price=None):
        template.setSubView(DefaultDialogPlaceHolders.FOOTER, Price(price))
