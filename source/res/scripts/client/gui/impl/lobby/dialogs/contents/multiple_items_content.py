# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/multiple_items_content.py
import typing
from gui.impl.gen.view_models.constants.fitting_types import FittingTypes
from gui.impl.common.base_sub_model_view import BaseSubModelView
from gui.impl.lobby.dialogs.auxiliary.confirmed_items_packer import ConfirmedItemsPacker
from gui.shared.gui_items import GUI_ITEM_TYPE
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.common.multiple_items_content_model import MultipleItemsContentModel
    from gui.shared.gui_items.fitting_item import FittingItem

class MultipleItemsContent(BaseSubModelView):
    __slots__ = ('_items', '_confirmedItemsPacker', '_itemsType')

    def __init__(self, viewModel, items, vehicleInvID=None, itemsType=None):
        super(MultipleItemsContent, self).__init__(viewModel)
        self._items = items
        self._confirmedItemsPacker = ConfirmedItemsPacker(vehicleInvID=vehicleInvID)
        self._itemsType = self._determineItemsType(items) if itemsType is None else itemsType
        return

    def onLoading(self, *args, **kwargs):
        super(MultipleItemsContent, self).onLoading(*args, **kwargs)
        with self._viewModel.transaction() as model:
            model.setItemsType(self._itemsType)
            self._fillItems(model.getConfirmedItems())

    def _fillItems(self, array):
        array.clear()
        for item in self._confirmedItemsPacker.packItems(items=self._items):
            array.addViewModel(item.getCofirmedItemViewModel())

        array.invalidate()

    def _determineItemsType(self, items):
        itemsTypes = self._confirmedItemsPacker.packItemsType(items, typesToCombine={GUI_ITEM_TYPE.VEHICLE_MODULES: FittingTypes.MODULE})
        return '' if not items or len(itemsTypes) > 1 else itemsTypes.pop()
