# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/tech_tree/aspects.py
import BigWorld
from gui.DialogsInterface import showDialog
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogButtons, DIALOG_BUTTON_ID
from gui.shared.formatters import icons
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import aop
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache

class OnTechTreePopulate(aop.Aspect):

    def atReturn(self, cd):
        cd.self.as_showMiniClientInfoS(_ms('#miniclient:tech_tree/description'), _ms('#miniclient:tech_tree/continue_download'))


class OnBuyVehicle(aop.Aspect):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        self._localKey = '#miniclient:buy_vehicle/%s'
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        vehicleItem = self.itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, cd.self.nationID, cd.self.inNationID)
        if self.__vehicle_is_available(vehicleItem):
            return None
        else:
            cd.avoid()

            def dialogButtonClickHandler(confirm):
                if confirm:
                    BigWorld.callback(0.1, lambda : cd.self._VehicleBuyWindow__requestForMoneyObtain(cd.args[0]))
                else:
                    cd.self.as_setEnabledSubmitBtnS(True)

            showDialog(SimpleDialogMeta(title=_ms(self._localKey % 'title'), message=icons.alert() + _ms(self._localKey % 'message'), buttons=I18nConfirmDialogButtons(i18nKey='questsConfirmDialog', focusedIndex=DIALOG_BUTTON_ID.SUBMIT)), dialogButtonClickHandler)
            return None


class OnRestoreVehicle(OnBuyVehicle):

    def __init__(self, config):
        super(OnRestoreVehicle, self).__init__(config)
        self._localKey = '#miniclient:restore_vehicle/%s'
