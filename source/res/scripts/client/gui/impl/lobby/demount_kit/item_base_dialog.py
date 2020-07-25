# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/demount_kit/item_base_dialog.py
from gui.impl.gen.view_models.common.format_resource_string_arg_model import FormatResourceStringArgModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView

class BaseItemDialog(FullScreenDialogView):
    __slots__ = ('_itemCD', '_item')

    def __init__(self, settings, compDescr):
        super(BaseItemDialog, self).__init__(settings)
        self._itemCD = compDescr
        self._item = self._itemsCache.items.getItemByCD(self._itemCD)

    def _setTitleArgs(self, arrModel, frmtArgs):
        for name, resource in frmtArgs:
            frmtModel = FormatResourceStringArgModel()
            frmtModel.setName(name)
            frmtModel.setValue(resource)
            arrModel.addViewModel(frmtModel)

        arrModel.invalidate()

    def _finalize(self):
        super(BaseItemDialog, self)._finalize()
        self._item = None
        return
