# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/demount_kit/demount_from_slot_dialog.py
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.lobby.demount_kit.demount_kit_utils import getDemountDialogTitle
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders as Placeholder

class DemountOptionalDeviceFromSlotDialog(DialogTemplateView):
    __slots__ = ('__item', '__forFitting', '__vehicle')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemCD, forFitting=False, vehicle=None, layoutID=None, uniqueID=None):
        super(DemountOptionalDeviceFromSlotDialog, self).__init__(layoutID, uniqueID)
        self.__item = self.__itemsCache.items.getItemByCD(itemCD)
        self.__forFitting = forFitting
        self.__vehicle = vehicle

    def _onLoading(self, *args, **kwargs):
        rDK = R.strings.demount_kit
        self.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        self.setSubView(Placeholder.TITLE, SimpleTextTitle(getDemountDialogTitle(self.__item, forFitting=self.__forFitting, fromSlot=True)))
        self.setSubView(Placeholder.CONTENT, SimpleTextContent(rDK.equipmentDemountFromSlot.confirmation.description))
        self.addButton(ConfirmButton(label=rDK.equipmentDemountFromSlot.confirmation.submit()))
        self.addButton(CancelButton(label=rDK.equipmentDemountFromSlot.confirmation.cancel()))
        self.__itemsCache.onSyncCompleted += self._inventorySyncHandler
        super(DemountOptionalDeviceFromSlotDialog, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.__itemsCache.onSyncCompleted -= self._inventorySyncHandler
        super(DemountOptionalDeviceFromSlotDialog, self)._finalize()

    def _getAdditionalData(self):
        return {}

    def _inventorySyncHandler(self, *_):
        if self.__vehicle and not self.__vehicle.isPostProgressionExists:
            self._closeClickHandler()
            return
