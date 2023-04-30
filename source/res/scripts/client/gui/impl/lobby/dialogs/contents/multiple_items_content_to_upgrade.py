# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/contents/multiple_items_content_to_upgrade.py
import typing
from gui.impl.lobby.dialogs.contents.multiple_items_content import MultipleItemsContent
from gui.impl.lobby.dialogs.auxiliary.confirmed_items_packer import ConfirmedItemsToUpgradePacker
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.common.multiple_items_content_model import MultipleItemsContentModel

class MultipleItemsContentToUpgrade(MultipleItemsContent):
    __slots__ = ()

    def __init__(self, viewModel, items, vehicleInvID=None, itemsType=None):
        super(MultipleItemsContentToUpgrade, self).__init__(viewModel, items, vehicleInvID, itemsType)
        self._confirmedItemsPacker = ConfirmedItemsToUpgradePacker(vehicleInvID=vehicleInvID)
