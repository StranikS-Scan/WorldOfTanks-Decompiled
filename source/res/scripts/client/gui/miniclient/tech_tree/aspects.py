# Embedded file name: scripts/client/gui/miniclient/tech_tree/aspects.py
import BigWorld
from gui.DialogsInterface import showDialog
from gui.Scaleform.daapi.view.dialogs import SimpleDialogMeta, I18nConfirmDialogButtons, DIALOG_BUTTON_ID
from gui.shared import g_itemsCache
from gui.shared.formatters import icons
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import aop
from helpers.i18n import makeString as _ms

class OnTechTreePopulate(aop.Aspect):

    def atReturn(self, cd):
        cd.self.as_showMiniClientInfoS(_ms('#miniclient:tech_tree/description'), _ms('#miniclient:tech_tree/continue_download'))


class OnBuyVehicle(aop.Aspect):

    def __init__(self, config):
        self.__vehicle_is_available = config['vehicle_is_available']
        aop.Aspect.__init__(self)

    def atCall(self, cd):
        vehicleItem = g_itemsCache.items.getItem(GUI_ITEM_TYPE.VEHICLE, cd.self.nationID, cd.self.inNationID)
        if self.__vehicle_is_available(vehicleItem):
            return None
        else:
            cd.avoid()

            def dialogButtonClickHandler(confirm):
                if confirm:
                    BigWorld.callback(0.1, lambda : cd.self._VehicleBuyWindow__requestForBuy(cd.args[0]))
                else:
                    cd.self.as_setEnabledSubmitBtnS(True)

            showDialog(SimpleDialogMeta(title=_ms('#miniclient:buy_vehicle/title'), message=icons.alert() + _ms('#miniclient:buy_vehicle/message'), buttons=I18nConfirmDialogButtons(i18nKey='questsConfirmDialog', focusedIndex=DIALOG_BUTTON_ID.SUBMIT)), dialogButtonClickHandler)
            return None
