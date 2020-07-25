# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/forsell/forsell_cm_handlers.py
from adisp import process
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs.ConfirmModuleMeta import SellModuleMeta
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import option, CMLabel, ContextMenu
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared import event_dispatcher as shared_events
from ids_generators import SequenceIDGenerator

class ForSellCMHandler(ContextMenu, EventSystemEntity):
    __sqGen = SequenceIDGenerator()

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showStorageModuleInfo(self._id)

    @option(__sqGen.next(), CMLabel.SELL)
    @process
    def sell(self):
        yield DialogsInterface.showDialog(SellModuleMeta(self._id))

    @option(__sqGen.next(), CMLabel.SALE_OPTION)
    def switchSaleOption(self):
        self.fireEvent(events.StorageEvent(events.StorageEvent.SELECT_MODULE_FOR_SELL, ctx={'intCD': self._id}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _getOptionCustomData(self, label):
        optionData = super(ForSellCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.SALE_OPTION:
            optionData.label = 'prohibitSale' if self._selected else 'allowSale'
        return optionData

    def _initFlashValues(self, ctx):
        super(ForSellCMHandler, self)._initFlashValues(ctx)
        self._selected = ctx.selected
